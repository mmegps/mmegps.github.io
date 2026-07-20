#!/usr/bin/env python3
"""Extra pass: convert the heavy WebP/PNG-origin and large JPEGs to lossy WebP (q80)
for big wins. Rewrites refs. Run: ./venv/bin/python optimize_heavy.py
"""
import os, re
from PIL import Image, ImageOps

SRC_IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "images")
POSTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "posts")
MAX_W = 1600
WEBP_Q = 80

HEAVY = {"DALL-E-2023-10-27-16.03.48.webp", "Photo-by-Vladislav Babienko.webp",
         "MyBaby.webp", "MM3.webp", "umbrella-ga28d6cc99_1920.jpg",
         "Cartoon-Go_for_it.jpg", "artur-matosyan-SBpy0oUR2tg-unsplash.jpg",
         "tolga-ulkan-9k36QqhA0cU-unsplash.jpg"}

def to_webp(fn, path):
    out = os.path.splitext(fn)[0] + ".webp"
    im = Image.open(path).convert("RGB")
    im = ImageOps.exif_transpose(im)
    if im.width > MAX_W:
        h = round(im.height * MAX_W / im.width)
        im = im.resize((MAX_W, h), Image.LANCZOS)
    op = os.path.join(SRC_IMG, out)
    im.save(op, "WEBP", quality=WEBP_Q, method=5)
    old = os.path.getsize(path)//1024; new = os.path.getsize(op)//1024
    print(f"webp {fn:45s} {old:5d} -> {new:5d} KB")
    for pf in sorted(os.listdir(POSTS)):
        if not pf.endswith(".md"):
            continue
        p = os.path.join(POSTS, pf); txt = open(p, encoding="utf-8").read()
        if fn in txt:
            txt2 = txt.replace(f"/images/{fn}", f"/images/{out}")
            if txt2 != txt:
                open(p, "w", encoding="utf-8").write(txt2)
                print(f"       rewrote {pf} -> /images/{out}")
    if out != fn:
        os.remove(path)

def optimize():
    for fn in sorted(os.listdir(SRC_IMG)):
        if fn in HEAVY:
            to_webp(fn, os.path.join(SRC_IMG, fn))

if __name__ == "__main__":
    optimize()
