# -*- coding: utf-8 -*-
"""extract_figure.py — 从论文 PDF 渲染一页（或其中一块区域）为 PNG，作为 PPT 配图。

用法:
    python extract_figure.py paper.pdf --page 3 --out fig3.png
    python extract_figure.py paper.pdf --page 1 --bbox 50 80 550 720 --zoom 2 --out fig1.png

参数:
    --page  1 起始页码
    --bbox  可选，页内裁剪 (x0 y0 x1 y1)，单位 PDF point；不填则整页
    --zoom  渲染缩放倍数，默认 2（清晰）
    --out   输出 PNG 路径
依赖: pymupdf (pip install pymupdf)
"""
import sys, argparse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--page", type=int, required=True)
    ap.add_argument("--bbox", type=float, nargs=4, default=None)
    ap.add_argument("--zoom", type=float, default=2.0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    doc = fitz.open(a.pdf)
    page = doc[a.page - 1]
    clip = None
    if a.bbox:
        clip = fitz.Rect(*a.bbox)
    mat = fitz.Matrix(a.zoom, a.zoom)
    pix = page.get_pixmap(matrix=mat, clip=clip, alpha=False)
    pix.save(a.out)
    print(f"saved {a.out}  size={pix.width}x{pix.height}  page={a.page}")

if __name__ == "__main__":
    main()
