#!/usr/bin/env python3
"""
Build the static site in docs/ for GitHub Pages.

WHY THIS EXISTS. GitHub renders a committed .html file as source code, not as a
page, and raw.githubusercontent.com serves it as text/plain. GitHub Pages is the
only way to make these four pages readable straight from the repo. It is also
crawled and indexed by search engines, which matters here: the whole
dissemination plan for this work is "be findable without running a campaign".

The four pages are plain, self-contained static HTML — no build-time templating
beyond report.html (see build.py), no runtime beyond d3 from a CDN and fonts.
They cross-link to each other by relative path, so this script is a copy with a
banner added. It used to rewrite claude.ai artifact URLs into relative paths,
back when the pages were published as Claude artifacts; the artifacts have been
retired and GitHub Pages is now the only published home.

    python report/build.py          # report.src.html -> report.html
    python report/build_site.py     # report/*.html   -> docs/
"""
import os, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "..", "docs")

REPO = "https://github.com/djhume/nepal-flood-2026"
SITE = "https://djhume.github.io/nepal-flood-2026/"

# One description per page: the search-result snippet and the link preview.
PAGES = {
    "index.html": "Independent physics analysis of the 26 August 2026 Langtang "
                  "Lirung collapse and the Trishuli flood, Nepal. Where the "
                  "flood water came from, how big the collapse was, and every "
                  "retraction along the way.",
    "plain.html": "The whole argument in plain English, no equations: why a "
                  "1,200-metre fall cannot melt enough ice to make this flood, "
                  "and what actually carried the water.",
    "report.html": "Technical report: corridor map, water budget, routing "
                   "model, entrainment closure, the Chamoli stress test, and "
                   "what would change our mind.",
    "workings.html": "Every equation, fit and figure executed end-to-end from "
                     "the data files, so the arithmetic can be checked rather "
                     "than trusted.",
}

# WHY A SKELETON. These pages were first written as Claude artifacts, where the
# runtime supplied <!doctype html>, <head>, charset and viewport. GitHub Pages
# supplies nothing, so served bare they render in quirks mode and — because
# there is no viewport meta — phones lay them out at ~980px and zoom out, which
# also means none of the max-width breakpoints in their CSS ever fire.
HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Dave Hume">
<meta property="og:type" content="article">
<meta property="og:site_name" content="The Trishuli Investigation">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
<link rel="canonical" href="{url}">
</head>
<body>
"""
FOOT = "\n</body>\n</html>\n"

# Colours come from each page's own tokens where they exist, with a literal
# fallback for workings.html, which has no theme tokens of its own.
BANNER = f"""<div style="max-width:780px;margin:0 auto;padding:10px 22px 0;
 font:12px/1.5 'IBM Plex Mono',monospace;color:var(--ink-soft,#54646f)">
 Independent analysis ·
 <a href="{REPO}" style="color:var(--river,#1e5f8e)">source, data and full
 revision history on GitHub</a></div>"""


def _esc(s):
    """Escape for an HTML attribute — these strings go inside content="…"."""
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;"))


def _split_head(html):
    """Split off the leading run of head-only tags (<link>, <style>, comments).

    Stops at the first thing that renders, so nothing that belongs in the body
    is moved. Deliberately does NOT hoist <script>: these pages load d3 from a
    CDN and the inline code that uses it sits further down, so leaving script
    order exactly as authored is the safe choice.
    """
    style = re.compile(r"\s*(?:<link\b[^>]*>|<style\b[^>]*>.*?</style>|<!--.*?-->)",
                       re.S | re.I)
    script = re.compile(r"\s*<script\b[^>]*>.*?</script>", re.S | re.I)
    taken, kept, i = [], [], 0
    while True:
        if (m := style.match(html, i)):
            taken.append(m.group(0).strip())
        elif (m := script.match(html, i)):
            kept.append(m.group(0).strip())   # stays in body, order preserved
        else:
            break
        i = m.end()
    return ("\n".join(taken) + "\n" if taken else ""), \
           ("\n".join(kept) + "\n" if kept else "") + html[i:]


def main():
    if os.path.isdir(DOCS):
        shutil.rmtree(DOCS)
    os.makedirs(DOCS)
    built = []
    for name, desc in PAGES.items():
        p = os.path.join(HERE, name)
        if not os.path.exists(p):
            print(f"  SKIP {name} (not built — run report/build.py first?)")
            continue
        html = open(p, encoding="utf-8").read()
        # a one-line banner back to the repo, after the nav if there is one
        if "</nav>" in html:
            html = html.replace("</nav>", "</nav>\n" + BANNER, 1)
        else:
            html = re.sub(r"(<div class=\"wrap\"[^>]*>)", BANNER + r"\n\1",
                          html, count=1)
        # lift the page's own <title> into the head we are about to give it
        m = re.search(r"<title>(.*?)</title>", html, re.S)
        title = m.group(1).strip() if m else name
        if m:
            html = html[:m.start()] + html[m.end():]
        # These files open with the <link>/<style> the artifact runtime used to
        # hoist into its own head. Left in <body> they still apply, but only
        # after the body has begun painting — a flash of unstyled text. Move
        # that leading run up into the head we are building.
        head_tags, rest = _split_head(html)
        url = SITE + ("" if name == "index.html" else name)
        head = HEAD.format(title=_esc(title), desc=_esc(desc), url=url)
        html = (head.replace("</head>", head_tags + "</head>")
                + rest.lstrip("\n") + FOOT)
        open(os.path.join(DOCS, name), "w", encoding="utf-8").write(html)
        built.append((name, len(html) // 1024))
    # GitHub Pages otherwise runs Jekyll, which silently eats files and folders
    # beginning with an underscore
    open(os.path.join(DOCS, ".nojekyll"), "w").write("")
    print(f"docs/ built — {len(built)} pages")
    for d, kb in built:
        print(f"  {d:16s} {kb:5d} KB")

    # every internal link must resolve to a file we actually shipped
    bad = 0
    for d, _ in built:
        html = open(os.path.join(DOCS, d), encoding="utf-8").read()
        if "claude.ai/code/artifact" in html:
            print(f"  ! {d}: still contains a claude.ai artifact link")
            bad += 1
        for href in set(re.findall(r'href="([^"#:?]+\.html)[^"]*"', html)):
            if not os.path.exists(os.path.join(DOCS, href)):
                print(f"  ! {d}: dead internal link -> {href}")
                bad += 1
        # the skeleton the artifact runtime used to supply and Pages does not
        for tag in ("<!doctype html>", '<meta charset="utf-8">',
                    'name="viewport"', 'name="description"', "<html lang="):
            if tag not in html:
                print(f"  ! {d}: missing {tag}")
                bad += 1
        if html.count("<title>") != 1:
            print(f"  ! {d}: {html.count('<title>')} <title> tags, expected 1")
            bad += 1
    print("checks: all pages well-formed, all internal links resolve" if not bad
          else f"checks: {bad} PROBLEM(S) — fix before publishing")


if __name__ == "__main__":
    main()
