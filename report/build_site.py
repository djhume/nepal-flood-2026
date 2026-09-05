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

PAGES = ["index.html", "plain.html", "report.html", "workings.html"]

BANNER = """<div style="max-width:780px;margin:0 auto;padding:10px 22px 0;
 font:12px/1.5 'IBM Plex Mono',monospace;color:#54646f">
 Static copy on GitHub Pages ·
 <a href="https://github.com/djhume/nepal-flood-2026" style="color:#1e5f8e">source,
 data and full revision history</a></div>"""


def main():
    if os.path.isdir(DOCS):
        shutil.rmtree(DOCS)
    os.makedirs(DOCS)
    built = []
    for name in PAGES:
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
    print("links: all internal links resolve" if not bad
          else f"links: {bad} PROBLEM(S) — fix before publishing")


if __name__ == "__main__":
    main()
