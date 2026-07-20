#!/usr/bin/env python3
"""Inject curated explicit `tags:` into each post's front matter.
Tags use the 5-theme vocabulary: Strategy, Startups, Leadership, AI, Musings.
Run: ./venv/bin/python add_tags.py
"""
import os, re

POSTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "posts")

# slug (filename minus date+ext) -> explicit themes
TAGS = {
    "fruits-passion": ["Musings"],
    "work-play": ["Leadership", "Musings"],
    "you-listening": ["Leadership"],
    "clarity-competitive-advantage": ["Strategy"],
    "focus-strtups": ["Startups"],
    "some-challenges-around-deep-learning-networks": ["AI"],
    "startups-chaos": ["Startups"],
    "idea-selection-idea-genertion": ["Startups"],
    "myths-ai-bandwagon": ["AI"],
    "decentralisation-and-purpose": ["Strategy", "Leadership"],
    "what-does-great-mean-product": ["Leadership"],
    "How-do-the-winds-blow-in-your-organisation": ["Leadership", "Startups"],
    "The-value-of-last-5percent": ["Startups"],
    "Why-positioning-matters-for-startups": ["Startups", "Strategy"],
    "When-does-Activity-translate-into-Productivity": ["Startups", "Leadership"],
    "First-ABC-then-PQR": ["Strategy"],
    "Stability-and-Change": ["Strategy", "Leadership"],
    "Generating-advantage-through-constraints": ["Strategy"],
    "From-me-to-we": ["Leadership"],
    "The-game-of-strategy": ["Strategy"],
    "Cultivating-trust-through-positioning-and-tranparency": ["Startups", "Strategy"],
    "The-AI-Decision-Open-source-or-Proprietary": ["AI"],
    "Strategic-wandering": ["Strategy", "Leadership"],
    "Generative-ai-the-new-probabilistic-shift": ["AI"],
    "Generative-ai-debunking-myths-for-leaders": ["AI", "Leadership"],
    "The-land-and-expand-strategy": ["Strategy", "Startups"],
    "Organisational-harmony": ["Leadership", "Startups"],
    "The-fallacy-of-If-we-build-it-they-will-come": ["Startups", "Strategy"],
}

def slug_of(fn):
    return re.sub(r"^\d{4}-\d{1,2}-\d{1,2}-", "", fn)[:-3]

def inject():
    for fn in sorted(os.listdir(POSTS)):
        if not fn.endswith(".md"):
            continue
        slug = slug_of(fn)
        tags = TAGS.get(slug)
        if not tags:
            print(f"NO MAPPING for {slug}")
            continue
        p = os.path.join(POSTS, fn)
        t = open(p, encoding="utf-8").read()
        tagline = "tags: " + ", ".join(tags)
        # insert tags right after the `title:` line in front matter
        if re.search(r"^tags:", t, re.M):
            # replace existing
            t = re.sub(r"^tags:.*$", tagline, t, count=1, flags=re.M)
        else:
            t = re.sub(r"^(title:.*\n)", r"\1" + tagline + "\n", t, count=1, flags=re.M)
        open(p, "w", encoding="utf-8").write(t)
        print(f"{slug:50s} -> {tags}")

if __name__ == "__main__":
    inject()
