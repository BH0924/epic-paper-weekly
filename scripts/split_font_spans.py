# -*- coding: utf-8 -*-
"""split_font_spans.py — 把一段文本按字符类别切成片段，用于中文宋体 / 英文 Times New Roman 分字体排版。

用法:
    python split_font_spans.py "文本内容"
    python split_font_spans.py --input text.txt

输出 JSON 数组: [{"t": "...", "lang": "zh"|"en"}, ...]
    zh = 中文/全角标点（用宋体 SimSun）
    en = 英文字母/数字/半角符号（用 Times New Roman）
连续同类字符合并为一片；调用方据此分别套 fontFamily。
"""
import sys, json, unicodedata

def is_zh(ch: str) -> bool:
    if not ch.strip():
        return True  # 空白跟随前一片，由合并逻辑处理
    o = ord(ch)
    # CJK 统一表意、扩展A、兼容表意
    if 0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF or 0xF900 <= o <= 0xFAFF:
        return True
    # 全角标点 / 全角字母数字
    if 0xFF00 <= o <= 0xFFEF:
        return True
    # 中文标点（。，、；：？！""''（）《》…—·）
    if ch in "。，、；：？！…—·“”‘’（）《》〈》「」『』【】":
        return True
    return False

def split(text: str):
    segs = []
    cur, cur_lang = "", None
    for ch in text:
        lang = "zh" if is_zh(ch) else "en"
        if cur_lang is None:
            cur, cur_lang = ch, lang
        elif lang == cur_lang:
            cur += ch
        else:
            segs.append({"t": cur, "lang": cur_lang})
            cur, cur_lang = ch, lang
    if cur:
        segs.append({"t": cur, "lang": cur_lang})
    return segs

def main():
    args = sys.argv[1:]
    if "--input" in args:
        p = args[args.index("--input") + 1]
        with open(p, encoding="utf-8") as f:
            text = f.read()
    elif args:
        text = args[0]
    else:
        print(__doc__)
        sys.exit(1)
    segs = split(text)
    print(json.dumps(segs, ensure_ascii=False, indent=2))
    zh = sum(len(s["t"]) for s in segs if s["lang"] == "zh")
    en = sum(len(s["t"]) for s in segs if s["lang"] == "en")
    print(f"# segments={len(segs)} zh_chars={zh} en_chars={en}", file=sys.stderr)

if __name__ == "__main__":
    main()
