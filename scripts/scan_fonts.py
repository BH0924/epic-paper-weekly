# -*- coding: utf-8 -*-
"""scan_fonts.py — 扫描 PPTX 内全部字体声明，统计使用情况并报告 Mac 字体残留。

用法:
    python scan_fonts.py papers.pptx

退出码: 0 = 无 Mac 字体残留；1 = 发现残留（提示先跑 fix_exported_pptx.py）。
"""
import sys, zipfile, re, collections

MAC_FONTS = {"Songti SC", "STSong", "PingFang SC", "Heiti SC", "Hiragino Sans GB",
             "STHeiti", "STKaiti", "STFangsong"}

def main():
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(2)
    path = sys.argv[1]
    counter = collections.Counter()
    bad = []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if not name.endswith(".xml"):
                continue
            text = z.read(name).decode("utf-8", errors="ignore")
            for m in re.finditer(r'typeface="([^"]*)"', text):
                face = m.group(1)
                counter[face] += 1
                if face in MAC_FONTS:
                    bad.append((name, face))
    print("== 字体声明统计 ==")
    for face, n in counter.most_common():
        flag = "  <-- Mac 字体残留" if face in MAC_FONTS else ""
        print(f"  {n:5d}  {face}{flag}")
    print(f"\n总声明数={sum(counter.values())}  不同字体={len(counter)}")
    if bad:
        print(f"\n发现 {len(bad)} 处 Mac 字体残留，先运行 fix_exported_pptx.py 修正：")
        for name, face in bad[:10]:
            print(f"  {face}  in {name}")
        sys.exit(1)
    print("未发现 Mac 字体残留。")

if __name__ == "__main__":
    main()
