#!/usr/bin/env python3
"""Optimize hero images: recompress JPEGs, convert PNGs to WebP. Rewrites refs.
Run: ./venv/bin/python optimize_images.py
"""
import os, re
from PIL import Image, ImageOps

SRC_IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "images")
POSTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "posts")
MAX_W = 1600
JPEG_Q = 72

def optimize():
    for fn in sorted(os.listdir(SRC_IMG)):
        path = os.path.join(SRC_IMG, fn)
        if fn.lower().endswith(".jpg") or fn.lower().endswith(".jpeg"):
            im = Image.open(path).convert("RGB")
            im = ImageOps.exif_transpose(im)
            if im.width > MAX_W:
                h = round(im.height * MAX_W / im.width)
                im = im.resize((MAX_W, h), Image.LANCZOS)
            im.save(path, "JPEG", quality=JPEG_Q, optimize=True, progressive=True)
            print(f"jpg  {fn:45s} -> {os.path.getsize(path)//1024:5d} KB")
        elif fn.lower().endswith(".png"):
            out = os.path.splitext(fn)[0] + ".webp"
            im = Image.open(path).convert("RGB")
            im = ImageOps.exif_transpose(im)
            if im.width > MAX_W:
                h = round(im.height * MAX_W / im.width)
                im = im.resize((MAX_W, h), Image.LANCZOS)
            op = os.path.join(SRC_IMG, out)
            im.save(op, "WEBP", lossless=True, quality=100, method=4)
            old = os.path.getsize(path) // 1024
            new = os.path.getsize(op) // 1024
            print(f"webp {fn:45s} {old:5d} -> {new:5d} KB")
            # rewrite post references to .webp
            for pf in sorted(os.listdir(POSTS)):
                if not pf.endswith(".md"):
                    continue
                p = os.path.join(POSTS, pf)
                txt = open(p, encoding="utf-8").read()
                if fn in txt:
                    txt2 = txt.replace(f"/images/{fn}", f"/images/{out}")
                    if txt2 != txt:
                        open(p, "w", encoding="utf-8").write(txt2)
                        print(f"       rewrote {pf} -> /images/{out}")
            os.remove(path)  # drop original png after rewrite

if __name__ == "__main__":
    optimize()
