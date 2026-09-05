#!/usr/bin/env python3
"""
Build a self-contained static site in docs/ for GitHub Pages.

WHY. The four published pages cross-link to each other by their claude.ai
artifact URLs, which is right for the artifacts but wrong for a website: a
visitor who lands on the GitHub Pages copy and clicks "Technical report" gets
bounced off the site. This rewrites those links to relative paths so the site
stands on its own, and leaves the artifact copies untouched.

WHY BOTHER AT ALL. GitHub renders .html as source code, not as a page, and
raw.githubusercontent.com serves it as text/plain. GitHub Pages is the only way
to make these readable from the repo — and unlike a Claude artifact, a Pages
site is crawled and indexed by search engines. For work whose whole
dissemination plan is "be findable without running a campaign", that indexing
is the point.

Pages is free on public repos; on private repos it needs a paid plan. So the
usual order is: make the repo public, then enable Pages on the docs/ folder.

    python report/build_site.py
    # then: Settings -> Pages -> Source: main, folder /docs
    # -> https://djhume.github.io/nepal-flood-2026/
"""
import os, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DOCS = os.path.join(ROOT, "docs")

# artifact URL -> the file it becomes on the static site
PAGES = {
    "50fbb9c4-1dd2-43f6-a8c1-dbbf80e9d197": ("hub.html", "index.html"),
    "39288bec-8708-4d94-8366-7a4966692543": ("plain.html", "plain.html"),
    "1fd064d2-fdc3-407e-b748-99b0e3cb3eb8": ("report.html", "report.html"),
    "60a02c4d-5fd3-439b-b483-bc42bcd4abcb": ("workings.html", "workings.html"),
}
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
    for uid, (src, dst) in PAGES.items():
        p = os.path.join(HERE, src)
        if not os.path.exists(p):
            print(f"  SKIP {src} (not built — run report/build.py first?)")
            continue
        html = open(p, encoding="utf-8").read()
        # point every cross-link at its neighbour on this site
        for u2, (_, d2) in PAGES.items():
            html = html.replace(f"https://claude.ai/code/artifact/{u2}", d2)
        # a one-line banner back to the repo, after the nav if there is one
        if "</nav>" in html:
            html = html.replace("</nav>", "</nav>\n" + BANNER, 1)
        else:
            html = re.sub(r"(<div class=\"wrap\"[^>]*>)", BANNER + r"\n\1",
                          html, count=1)
        open(os.path.join(DOCS, dst), "w", encoding="utf-8").write(html)
        built.append((dst, len(html) // 1024))
    # GitHub Pages otherwise runs Jekyll, which silently eats files and folders
    # beginning with an underscore
    open(os.path.join(DOCS, ".nojekyll"), "w").write("")
    print(f"docs/ built — {len(built)} pages")
    for d, kb in built:
        print(f"  {d:16s} {kb:4d} KB")
    leftover = 0
    for d, _ in built:
        leftover += open(os.path.join(DOCS, d), encoding="utf-8").read().count(
            "claude.ai/code/artifact")
    print(f"remaining claude.ai artifact links: {leftover} "
          f"({'self-contained' if leftover == 0 else 'CHECK THESE'})")


if __name__ == "__main__":
    main()
