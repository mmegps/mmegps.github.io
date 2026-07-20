#!/usr/bin/env python3
"""
Static site generator for the Mohit Mehta personal site revamp.
Zero-dependency except `markdown`. Preserves /Title/ permalinks.
Run: ./venv/bin/python build.py
"""
import os, re, html, shutil, datetime
from collections import defaultdict
from markdown import markdown

SRC = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(SRC, "src", "posts")
IMAGES_DIR = os.path.join(SRC, "src", "images")
OUTPUT = os.path.join(SRC, "output")
TODAY = datetime.date(2026, 7, 11)

SITE = {
    "name": "Mohit Mehta",
    "role": "Management Innovation PhD · Strategy & AI Advisor",
    "tagline": "Less theory, more decision clarity around what matters. Management innovation basics meeting start-up reality.",
    "url": "https://mmegps.github.io",
    "email": "mmegps@gmail.com",
    "github": "mmegps",
    "linkedin": "momehta",
    "twitter": "mmegps",
    "bio": "You don't need another think-piece about AI. You need clear, decision-ready thinking you can bring into a leadership team — backed by a Cranfield PhD in Management Innovation and daily work inside a London tech scale-up.",
    "headline": "Strategy and AI, without the noise",
    "avatar": "https://github.com/mmegps.png",
    "ga4": "G-HV88E628WJ",
}

# Theme taxonomy (overlapping tags used for the homepage topic chips)
THEMES = ["Strategy", "Startups", "Leadership", "AI", "Musings"]

# Old typo'd URLs -> clean target (301-style redirect stubs). Keeps external links alive.
REDIRECTS = {
    "/focus-strtups/": "/focus-startups/",
    "/Cultivating-trust-through-positioning-and-tranparency/": "/Cultivating-trust-through-positioning-and-transparency/",
    "/idea-selection-idea-genertion/": "/idea-selection-idea-generation/",
}

# Primary pillars (curated, one per post) — drive the Start here page + honest counts
PILLARS = [
    ("Clarity & Positioning", "Turning ambiguity into a decision."),
    ("From Me to We", "Moving from individual to collective."),
    ("Scale-up Reality", "Activity into productivity; the last 5%."),
    ("The AI Shift", "What applied AI means for your choices."),
]

# Curated "start here" picks per pillar (by slug) — the exec fast-path
START_PICKS = {
    "Clarity & Positioning": ["clarity-competitive-advantage", "Why-positioning-matters-for-startups"],
    "From Me to We": ["From-me-to-we", "Organisational-harmony"],
    "Scale-up Reality": ["The-fallacy-of-If-we-build-it-they-will-come", "The-value-of-last-5percent"],
    "The AI Shift": ["Generative-ai-the-new-probabilistic-shift", "The-AI-Decision-Open-source-or-Proprietary"],
}

# Keyword -> theme inference (applied to title+body)
THEME_KEYWORDS = {
    "Strategy": ["strategy", "positioning", "competitive", "advantage", "game of",
                 "land and expand", "purpose", "constraint", "clarity", "stability",
                 "change", "foundation", "abc", "pqr"],
    "Startups": ["startup", "founder", "scale-up", "venture", "chaos", "idea selection",
                 "idea generation", "focus", "organisation", "organisational", "winds blow",
                 "activity", "productivity", "last 5%", "five percent", "trust"],
    "Leadership": ["leadership", "leader", "management", "me to we", "harmony", "listening",
                   "wandering", "great mean", "great product", "work and play", "fruits of passion"],
    "AI": ["ai", "artificial intelligence", "generative", "machine learning", "deep learning",
           "probabilistic", "open-source", "proprietary", "bandwagon", "myth"],
    "Musings": [],  # fallback
}

IMG_CREDITS = {}  # filled per post parse

def parse_front_matter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        return {}, text
    fm_raw, body = m.group(1), m.group(2)
    fm = {}
    for line in fm_raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, body

def prose_excerpt(md, limit=220):
    """First real prose paragraph, skipping image tables and credit captions."""
    md = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", md)
    blocks = re.split(r"\n\s*\n", md)
    for b in blocks:
        text = re.sub(r"[|*_>`#\-]", " ", b)
        text = re.sub(r"\s+", " ", text).strip()
        if sum(c.isalpha() for c in text) < 40:
            continue
        if re.search(r"(image by|photo by|\(c\)|credit|copyright|unsplash|pixabay|pexels)", text, re.I):
            continue
        if len(text) > limit:
            text = text[:limit].rsplit(" ", 1)[0] + "\u2026"
        return text
    return ""

def strip_md_to_text(md):
    # remove images, links -> text, markdown emphasis
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", md)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[*_#>|`\-]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def first_image(md):
    m = re.search(r"!\[[^\]]*\]\(([^)]+)\)", md)
    if m:
        return m.group(1).replace("{{ site.baseurl }}", "").strip()
    return None

def infer_themes(title, body):
    blob = (title + " " + body).lower()
    hits = []
    for theme, kws in THEME_KEYWORDS.items():
        if any(kw in blob for kw in kws):
            hits.append(theme)
    if not hits:
        hits = ["Musings"]
    return hits

def read_time(text):
    words = len(text.split())
    return max(1, round(words / 200))

def load_posts():
    posts = []
    for fn in sorted(os.listdir(POSTS_DIR)):
        if not fn.endswith(".md"):
            continue
        with open(os.path.join(POSTS_DIR, fn), encoding="utf-8") as f:
            raw = f.read()
        fm, body = parse_front_matter(raw)
        title = fm.get("title", fn)
        # date from filename: 2020-5-10-... or 2022-3-04-...
        dm = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})-", fn)
        if dm:
            date = datetime.date(int(dm.group(1)), int(dm.group(2)), int(dm.group(3)))
        else:
            date = TODAY
        # permalink slug = filename minus date
        slug = re.sub(r"^\d{4}-\d{1,2}-\d{1,2}-", "", fn)[:-3]
        clean = strip_md_to_text(body)
        excerpt = prose_excerpt(body)
        img = first_image(body)
        themes = infer_themes(title, body)
        # prefer explicit front-matter tags if present
        if fm.get("tags"):
            themes = [t.strip() for t in fm["tags"].split(",") if t.strip()]
        pillar = fm.get("pillar", themes[0] if themes else "Musings")
        posts.append({
            "title": title,
            "date": date,
            "slug": slug,
            "url": f"/{slug}/",
            "excerpt": excerpt,
            "image": img,
            "themes": themes,
            "pillar": pillar,
            "read_time": read_time(clean),
            "body": body,
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts

# ---------- templates ----------
BASE_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="{ogtype}">
<meta property="og:url" content="{url}{path}">
{ogimage}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/style.css">
<link rel="alternate" type="application/rss+xml" title="{name}" href="/feed.xml">
{ga4}
</head>"""

def og_image_tag(image):
    if image:
        src = image if image.startswith("/") else "/" + image
        return f'<meta property="og:image" content="{SITE["url"]}{src}">'
    return f'<meta property="og:image" content="{SITE["url"]}/og-default.svg">'

def ga4_snippet():
    cid = SITE.get("ga4")
    if not cid:
        return ""
    return (
        f'<script async src="https://www.googletagmanager.com/gtag/js?id={cid}"></script>\n'
        f'<script>\n'
        f'  window.dataLayer = window.dataLayer || [];\n'
        f'  function gtag(){{ dataLayer.push(arguments); }}\n'
        f'  gtag("js", new Date());\n'
        f'  gtag("config", "{cid}");\n'
        f'</script>'
    )

def render_head(title, desc, path, image=None, ogtype="website"):
    return BASE_HEAD.format(
        title=html.escape(title), desc=html.escape(desc), url=SITE["url"],
        path=path, ogtype=ogtype, name=SITE["name"], ogimage=og_image_tag(image),
        ga4=ga4_snippet(),
    )

NAV = """
<header class="site-header">
  <div class="container nav">
    <a class="brand" href="/">{name}</a>
    <nav>
      <a href="/start-here/">Start here</a>
      <a href="/writing/">Writing</a>
      <a href="/about/">About</a>
      <a href="/#topics">Topics</a>
      <a class="cta" href="mailto:{email}">Get in touch</a>
    </nav>
  </div>
</header>"""

FOOTER = """
<footer class="site-footer">
  <div class="container">
    <p>{name} \u00b7 {role}</p>
    <div class="social">
      <a href="mailto:{email}">Email</a>
      <a href="https://github.com/{github}" rel="noopener">GitHub</a>
      <a href="https://www.linkedin.com/in/{linkedin}" rel="noopener">LinkedIn</a>
      <a href="https://www.twitter.com/{twitter}" rel="noopener">Twitter</a>
    </div>
    <p class="muted">© {year} {name}. Built as a static site.</p>
  </div>
</footer>"""

def page(head, body_inner, body_class=""):
    subs = dict(SITE, year=TODAY.year)
    nav = NAV.format(**subs)
    footer = FOOTER.format(**subs)
    return f"""{head}
<body>
{nav}
<main class="{body_class}">
{body_inner}
</main>
{footer}
</body>
</html>"""

def md_to_html(md):
    # normalize jekyll baseurl in image links
    md = md.replace("{{ site.baseurl }}", "")
    return markdown(md, extensions=["extra", "sane_lists", "smarty"])

def img_tag(src, alt="", cls=""):
    s = src if src.startswith("/") else "/" + src
    c = f' class="{cls}"' if cls else ""
    return f'<img src="{s}" alt="{html.escape(alt)}" loading="lazy" decoding="async"{c}>'

# ---------- pages ----------
def build_home(posts):
    featured = posts[:5]
    hero = f"""
<section class="hero">
  <div class="container hero-inner">
    <p class="eyebrow">For leaders building through the AI shift</p>
    <h1 class="headline">{html.escape(SITE['headline'])}</h1>
    <div class="byline">
      <img class="avatar" src="{SITE['avatar']}" alt="{html.escape(SITE['name'])}" loading="lazy" width="58" height="58">
      <div class="byline-text">
        <span class="who">{html.escape(SITE['name'])}</span>
        <span class="role">{html.escape(SITE['role'])}</span>
      </div>
    </div>
    <p class="tagline">{html.escape(SITE['tagline'])}</p>
    <div class="hero-actions">
      <a class="btn" href="/writing/">Read the writing</a>
      <a class="btn ghost" href="mailto:{SITE['email']}">Get in touch</a>
    </div>
  </div>
</section>"""
    # topic chips
    counts = defaultdict(int)
    for p in posts:
        for t in p["themes"]:
            counts[t] += 1
    chips = "".join(
        f'<a class="chip" href="/writing/#{t.lower()}">{t} <span>{counts[t]}</span></a>'
        for t in THEMES if counts.get(t)
    )
    topics = f"""
<section id="topics" class="topics">
  <div class="container">
    <h2>Topics</h2>
    <div class="chips">{chips}</div>
    <p class="more"><a href="/start-here/">Not sure where to start? Pick a thread →</a></p>
  </div>
</section>"""
    # latest list
    items = ""
    for p in featured:
        img = img_tag(p["image"], p["title"], "thumb") if p["image"] else ""
        th = "".join(f'<span class="tag">{t}</span>' for t in p["themes"])
        items += f"""
<article class="post-card">
  <a class="post-link" href="{p['url']}">{img}</a>
  <div class="post-body">
    <div class="tags">{th}</div>
    <h3><a href="{p['url']}">{html.escape(p['title'])}</a></h3>
    <p class="meta">{p['date'].strftime('%B %Y')} \u00b7 {p['read_time']} min read</p>
    <p>{html.escape(p['excerpt'])}</p>
  </div>
</article>"""
    latest = f"""
<section class="latest">
  <div class="container">
    <h2>Latest writing</h2>
    <div class="post-grid">{items}</div>
    <p class="more"><a href="/writing/">All writing \u2192</a></p>
  </div>
</section>"""
    head = render_head(SITE["headline"] + " — " + SITE["name"], SITE["headline"], "/")
    return page(head, hero + topics + latest, "home")

def build_writing(posts):
    by_pillar = {name: [] for name, _ in PILLARS}
    for p in posts:
        by_pillar.setdefault(p["pillar"], []).append(p)
    sections = ""
    for pname, blurb in PILLARS:
        items = ""
        for p in by_pillar.get(pname, []):
            img = img_tag(p["image"], p["title"], "thumb") if p["image"] else ""
            th = "".join(f'<span class="tag" data-theme="{t.lower()}">{t}</span>' for t in p["themes"])
            items += f"""
<article class="post-card" data-themes="{' '.join(t.lower() for t in p['themes'])}">
  <a class="post-link" href="{p['url']}">{img}</a>
  <div class="post-body">
    <div class="tags">{th}</div>
    <h3><a href="{p['url']}">{html.escape(p['title'])}</a></h3>
    <p class="meta">{p['date'].strftime('%B %Y')} · {p['read_time']} min read</p>
    <p>{html.escape(p['excerpt'])}</p>
  </div>
</article>"""
        sections += f"""
    <section class="pillar-block" id="{html.escape(pname.lower())}">
      <div class="container">
        <h2>{html.escape(pname)}</h2>
        <p class="pillar-blurb">{html.escape(blurb)}</p>
        <div class="post-grid">{items}</div>
      </div>
    </section>"""
    body = f"""
<section class="writing">
  <div class="container">
    <h1>Writing</h1>
    <p class="sub">Essays on strategy, startups, leadership and applied AI — grouped by theme.</p>
  </div>
  {sections}
</section>"""
    head = render_head("Writing — " + SITE["name"], "Essays on strategy, startups, leadership and applied AI.", "/writing/")
    return page(head, body, "writing-page")

def build_redirects():
    out = []
    for src, target in REDIRECTS.items():
        # src is like /focus-strtups/ -> folder focus-strtups
        folder = src.strip("/")
        canonical = SITE["url"] + target
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting…</title>
<link rel="canonical" href="{canonical}">
<meta http-equiv="refresh" content="0; url={target}">
</head>
<body>
<p>This page has moved. <a href="{target}">Continue to the new location</a>.</p>
</body>
</html>"""
        out.append((folder, html))
    return out

def build_post(p):
    html_body = md_to_html(p["body"])
    th = "".join(f'<span class="tag">{t}</span>' for t in p["themes"])
    body = f"""
<article class="post">
  <div class="container narrow">
    <div class="tags">{th}</div>
    <h1>{html.escape(p['title'])}</h1>
    <p class="meta">{p['date'].strftime('%B %d, %Y')} \u00b7 {p['read_time']} min read</p>
    <div class="post-content">{html_body}</div>
    <hr>
    <p class="back"><a href="/writing/">\u2190 Back to all writing</a></p>
  </div>
</article>"""
    head = render_head(p["title"] + " — " + SITE["name"], p["excerpt"], p["url"], image=p["image"], ogtype="article")
    return page(head, body, "post-page")

def build_about():
    body = f"""
<section class="about">
  <div class="container narrow">
    <h1>About</h1>
    <p class="lead">You do not need another think piece about AI or generic start-up advice. You need simple, clear, contextual and grounded thinking you can bring into a leadership team. This is what this site is for, and this is what I do.</p>
    <p>I hold a PhD in Management Innovation from Cranfield, and Masters in Mathematics and Computer Science, and bring 25 years of industry experience, applying my knowledge and experience daily within a fast-moving London technology start-up. I proudly pair established theory with real execution in strategy, leadership and applied AI. That is why you will see the ideas here are real reflections of the field and real executions, and not just admired good-sounding advice.</p>
    <h2>Focus areas</h2>
    <ul class="focus">
      <li><strong>Strategy &amp; Positioning</strong> — turning ambiguity into a decision.</li>
      <li><strong>Startups &amp; Scale-ups</strong> — activity into productivity; the last 5%.</li>
      <li><strong>Leadership &amp; Management Innovation</strong> — moving from me to we.</li>
      <li><strong>AI &amp; the Shift</strong> — what generative AI actually means for your choices.</li>
    </ul>
    <h2>Get in touch</h2>
    <p>Read the <a href="/writing/">writing</a>, or <a href="mailto:{SITE['email']}">get in touch</a> for advisory and consulting for startups.</p>
  </div>
</section>"""
    head = render_head("About — " + SITE["name"], SITE["bio"][:160], "/about/")
    return page(head, body, "about-page")

def build_start_here(posts):
    by_slug = {p["slug"]: p for p in posts}
    sections = ""
    for pname, blurb in PILLARS:
        picks = []
        for slug in START_PICKS.get(pname, []):
            p = by_slug.get(slug)
            if not p:
                continue
            picks.append(f"""
        <li class=\"pick\">
          <a href=\"{p['url']}\">{html.escape(p['title'])}</a>
          <span class=\"pick-meta\">{p['date'].strftime('%B %Y')} · {p['read_time']} min read</span>
          <p>{html.escape(p['excerpt'])}</p>
        </li>""")
        count = sum(1 for p in posts if p["pillar"] == pname)
        sections += f"""
    <section class="pillar">
      <div class="container">
        <h2>{html.escape(pname)} <span class="count">{count}</span></h2>
        <p class="pillar-blurb">{html.escape(blurb)}</p>
        <ul class="picks">{''.join(picks)}
        </ul>
        <p class="more"><a href="/writing/#{html.escape(pname.lower())}">All {html.escape(pname)} writing →</a></p>
      </div>
    </section>"""
    body = f"""
<section class="start-hero">
  <div class="container">
    <p class="eyebrow">For leaders building through the AI shift</p>
    <h1>If you have ten minutes</h1>
    <p class="lead">Start here. Pick the thread that matches where you are and whatever interests you. Each one is a curated path through the writings with unique reflections.</p>
  </div>
</section>{sections}"""
    head = render_head("Start here — " + SITE["name"], "A curated path through the writing for leaders.", "/start-here/")
    return page(head, body, "start-here-page")

def build_404():
    body = """
<section class="nf">
  <div class="container narrow">
    <h1>404</h1>
    <p>That page wandered off. <a href="/">Head home</a> or browse the <a href="/writing/">writing</a>.</p>
  </div>
</section>"""
    head = render_head("404 — " + SITE["name"], "Page not found.", "/404.html")
    return page(head, body, "nf-page")

# ---------- feeds ----------
def build_rss(posts):
    items = []
    for p in posts:
        desc = html.escape(p["excerpt"])
        items.append(f"""  <item>
    <title>{html.escape(p['title'])}</title>
    <link>{SITE['url']}{p['url']}</link>
    <guid>{SITE['url']}{p['url']}</guid>
    <pubDate>{p['date'].strftime('%a, %d %b %Y 00:00:00 +0000')}</pubDate>
    <description>{desc}</description>
  </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>{SITE['name']}</title>
  <link>{SITE['url']}</link>
  <description>{html.escape(SITE['tagline'])}</description>
  <lastBuildDate>{TODAY.strftime('%a, %d %b %Y 00:00:00 +0000')}</lastBuildDate>
{chr(10).join(items)}
</channel>
</rss>"""

def build_sitemap(posts):
    urls = [("/", "1.0"), ("/writing/", "0.8"), ("/about/", "0.6"), ("/start-here/", "0.8")]
    for p in posts:
        urls.append((p["url"], "0.7"))
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, pri in urls:
        out.append(f"  <url><loc>{SITE['url']}{path}</loc><priority>{pri}</priority></url>")
    out.append("</urlset>")
    return "\n".join(out)

def main():
    posts = load_posts()
    shutil.rmtree(OUTPUT, ignore_errors=True)
    os.makedirs(OUTPUT, exist_ok=True)
    # home
    open(os.path.join(OUTPUT, "index.html"), "w", encoding="utf-8").write(build_home(posts))
    # writing
    os.makedirs(os.path.join(OUTPUT, "writing"), exist_ok=True)
    open(os.path.join(OUTPUT, "writing", "index.html"), "w", encoding="utf-8").write(build_writing(posts))
    # about
    os.makedirs(os.path.join(OUTPUT, "about"), exist_ok=True)
    open(os.path.join(OUTPUT, "about", "index.html"), "w", encoding="utf-8").write(build_about())
    # start here
    os.makedirs(os.path.join(OUTPUT, "start-here"), exist_ok=True)
    open(os.path.join(OUTPUT, "start-here", "index.html"), "w", encoding="utf-8").write(build_start_here(posts))
    # posts
    for p in posts:
        d = os.path.join(OUTPUT, p["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(build_post(p))
    # redirects (old typo URLs -> clean targets)
    for folder, html in build_redirects():
        d = os.path.join(OUTPUT, folder)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(html)
    # 404
    open(os.path.join(OUTPUT, "404.html"), "w", encoding="utf-8").write(build_404())
    # feeds
    open(os.path.join(OUTPUT, "feed.xml"), "w", encoding="utf-8").write(build_rss(posts))
    open(os.path.join(OUTPUT, "sitemap.xml"), "w", encoding="utf-8").write(build_sitemap(posts))
    # copy images
    out_img = os.path.join(OUTPUT, "images")
    os.makedirs(out_img, exist_ok=True)
    for fn in os.listdir(IMAGES_DIR):
        shutil.copy2(os.path.join(IMAGES_DIR, fn), os.path.join(out_img, fn))
    # favicon + og-default
    write_assets(OUTPUT)
    # filter JS
    open(os.path.join(OUTPUT, "filter.js"), "w", encoding="utf-8").write(FILTER_JS)
    # style.css
    shutil.copy2(os.path.join(SRC, "src", "style.css"), os.path.join(OUTPUT, "style.css"))
    print(f"Built {len(posts)} posts + home/writing/about/404 + feeds into {OUTPUT}")

def write_assets(out):
    favicon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0f766e"/><text x="32" y="44" font-size="34" font-family="Georgia,serif" fill="#fff" text-anchor="middle">M</text></svg>'
    open(os.path.join(out, "favicon.svg"), "w").write(favicon)
    og = f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630"><rect width="1200" height="630" fill="#0f172a"/><text x="80" y="300" font-size="72" font-family="Georgia,serif" fill="#fff">{SITE["name"]}</text><text x="80" y="380" font-size="34" fill="#5eead4">{SITE["role"]}</text></svg>'
    open(os.path.join(out, "og-default.svg"), "w").write(og)

FILTER_JS = """
document.addEventListener('DOMContentLoaded', function(){
  var btns = document.querySelectorAll('.chip.filter');
  var cards = document.querySelectorAll('.post-card');
  btns.forEach(function(b){
    b.addEventListener('click', function(){
      btns.forEach(function(x){x.classList.remove('active');});
      b.classList.add('active');
      var t = b.getAttribute('data-theme');
      cards.forEach(function(c){
        var themes = c.getAttribute('data-themes') || '';
        c.style.display = (t === 'all' || themes.indexOf(t) !== -1) ? '' : 'none';
      });
    });
  });
});
"""

if __name__ == "__main__":
    main()
