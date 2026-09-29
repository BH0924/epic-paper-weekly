# -*- coding: utf-8 -*-
"""fix_exported_pptx.py — 飞书导出的 PPTX 在 Windows 打开前修正中文字体映射。

飞书在线 Slides 导出时把"宋体"写成 Mac 专用字体 Songti SC，Windows 无此字体会错配。
本脚本把包内所有 XML 里的 Songti SC（及常见 Mac 中文字体别名）替换为 SimSun，并报告替换数量。

用法:
    python fix_exported_pptx.py papers.pptx                # 原地修正
    python fix_exported_pptx.py papers.pptx --out fixed.pptx
    python fix_exported_pptx.py papers.pptx --map "Songti SC=SimSun,STSong=SimSun"
"""
import sys, argparse, zipfile, shutil, os, re

DEFAULT_MAP = {
    "Songti SC": "SimSun",
    "STSong": "SimSun",
    "宋体-PUA": "SimSun",
    "PingFang SC": "SimSun",   # 若混入苹方，中文按宋体交付
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("--out", default=None)
    ap.add_argument("--map", default=None, help="覆盖默认映射，逗号分隔 Old=New")
    a = ap.parse_args()

    m = dict(DEFAULT_MAP)
    if a.map:
        m = {}
        for kv in a.map.split(","):
            old, new = kv.split("=")
            m[old.strip()] = new.strip()

    out = a.out or a.pptx
    tmp = out + ".tmp"
    total = 0
    files_touched = []

    with zipfile.ZipFile(a.pptx, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith(".xml"):
                text = data.decode("utf-8")
                before = text
                for old, new in m.items():
                    # typeface="Songti SC" / typeface='Songti SC'
                    text = text.replace(old, new)
                if text != before:
                    n = sum(before.count(old) for old in m)
                    total += n
                    files_touched.append((item.filename, n))
                    data = text.encode("utf-8")
            zout.writestr(item, data)

    if out == a.pptx:
        os.replace(tmp, a.pptx)
    else:
        shutil.move(tmp, out)

    print(f"replaced occurrences={total} across {len(files_touched)} xml parts -> {out}")
    for fn, n in files_touched[:20]:
        print(f"  {n:4d}  {fn}")
    if total == 0:
        print("（未发现需替换的字体名；可跑 scan_fonts.py 复核）")

if __name__ == "__main__":
    main()
