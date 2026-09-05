#!/usr/bin/env python3
"""Build report/workings.html from the executed notebook.

WHY THIS EXISTS. Until 5 September 2026 this page was produced by hand — run
nbconvert, paste in some CSS — and nothing recorded how. It drifted: the
published workings sat at the 2 September notebook while the summary pages
announced findings 04 and 05, so the one page whose whole job is "check the
arithmetic rather than trust it" did not contain the arithmetic being checked.
A hand step that nobody can repeat is a hand step that silently goes stale, so
the page is now built by this script and rebuilt whenever the notebook is.

    .venv/bin/python notebooks/build_workings.py            # cells -> .ipynb
    (cd notebooks && ../.venv/bin/jupyter nbconvert --to notebook \
        --execute --inplace trishuli_workings.ipynb)        # run them
    .venv/bin/python notebooks/build_workings_html.py       # -> report/
    .venv/bin/python report/build_site.py                   # -> docs/

OUTPUT FORMAT. report/*.html are fragments, not documents: a <title>, the
<style> blocks that belong in the head, then body content. report/build_site.py
hoists the leading style run into a head skeleton it supplies. This script
emits the same shape so workings.html goes through that pipeline like the other
three pages, including its dead-internal-link check.

THEMING. nbconvert's lab template is light-only and hardcodes the JupyterLab
CSS variables. The other three pages follow the reader's theme, so the reader
used to fall out of a dark site into a white wall. The injected CSS below
redefines the --jp-* variables under a dark media query — but deliberately
keeps CODE CELLS AND FIGURES on a light card even in dark mode, because
pygments syntax colours and matplotlib PNGs are both baked light and would be
unreadable or ugly inverted. Dark chrome, light code, on purpose.
"""
import os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NB   = os.path.join(HERE, "trishuli_workings.ipynb")
OUT  = os.path.join(ROOT, "report", "workings.html")
PY   = sys.executable

NAV = """<nav class="hubnav"><a href="index.html">&#9664; Project home</a>\
<a href="plain.html">Plain English</a><a href="report.html">Technical report</a>\
<span class="here">Model workings</span></nav>
"""

# Site chrome, appended after the template's own styles so it wins.
CHROME = """
<style>
/* ---- site chrome, injected by notebooks/build_workings_html.py ---------- */
:root{
  --ground:#f2f5f4; --panel:#ffffff; --ink:#22303a; --ink-soft:#54646f;
  --river:#1e5f8e; --line:#d3dcda;
  --serif:"Source Serif 4",Georgia,"Times New Roman",serif;
  --mono:"IBM Plex Mono","SFMono-Regular",Consolas,monospace;
}
html,body{background:var(--ground);color:var(--ink)}
body{margin:0 auto;max-width:1140px;padding:0 18px 3rem}
.jp-Cell{overflow-x:auto}

/* the nav the other three pages carry; this page had none at all, so a
   reviewer who landed here from a shared link could not get back */
.hubnav{max-width:1140px;margin:0 auto;padding:16px 0 0;font-family:var(--mono);
  font-size:11.5px;letter-spacing:.06em;display:flex;gap:14px;flex-wrap:wrap;
  align-items:center;color:var(--ink-soft)}
.hubnav a{color:var(--ink-soft);text-decoration:none;
  border-bottom:1px solid var(--line)}
.hubnav a:hover{color:var(--river);border-color:var(--river)}
.hubnav .here{color:var(--river);border-bottom:1px solid var(--river)}

/* prose reads as prose, not as UI chrome */
.jp-RenderedHTMLCommon{font-family:var(--serif);font-size:16px;line-height:1.6}
.jp-RenderedHTMLCommon table{font-size:14px}
.jp-RenderedHTMLCommon a{color:var(--river)}

@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#131b21; --panel:#1b262e; --ink:#e2e9ec; --ink-soft:#9fb0ba;
    --river:#6aa8d8; --line:#2c3a44;
  }
  /* Redefine the template's own variables rather than fighting them rule by
     rule. Everything the notebook paints reads from these. */
  :root:not([data-theme="light"]) body{
    --jp-layout-color0:#131b21; --jp-layout-color1:#131b21;
    --jp-layout-color2:#1b262e; --jp-layout-color3:#22303a;
    --jp-content-font-color0:#e2e9ec; --jp-content-font-color1:#e2e9ec;
    --jp-content-font-color2:#9fb0ba; --jp-content-font-color3:#7d8f9a;
    --jp-ui-font-color0:#e2e9ec; --jp-ui-font-color1:#e2e9ec;
    --jp-ui-font-color2:#9fb0ba; --jp-ui-font-color3:#7d8f9a;
    --jp-border-color0:#2c3a44; --jp-border-color1:#2c3a44;
    --jp-border-color2:#22303a; --jp-border-color3:#1b262e;
    --jp-content-link-color:#6aa8d8;
  }
  /* ...but NOT the code cells or the figures. Pygments syntax colours and
     matplotlib PNGs are both baked for a light background; inverted they are
     unreadable and grubby respectively. Put them on an explicit light card so
     it reads as a deliberate choice rather than a theming miss. */
  :root:not([data-theme="light"]) .jp-InputArea-editor,
  :root:not([data-theme="light"]) .jp-RenderedImage{
    background:#fbfcfc;border:1px solid #2c3a44;border-radius:6px;
    padding:4px 6px}
  :root:not([data-theme="light"]) .jp-InputArea-editor .highlight,
  :root:not([data-theme="light"]) .jp-InputArea-editor pre{
    background:transparent;color:#22303a}
  :root:not([data-theme="light"]) .jp-RenderedImage img{
    background:#ffffff;border-radius:4px}
}

/* wide code and wide tables scroll rather than forcing the page sideways */
@media (max-width:700px){
  body{padding-left:12px;padding-right:12px}
  .jp-RenderedHTMLCommon table{display:block;overflow-x:auto}
}
</style>
"""


def main():
    with tempfile.TemporaryDirectory() as td:
        subprocess.run([PY, "-m", "jupyter", "nbconvert", "--to", "html",
                        "--template", "lab", "--output-dir", td,
                        "--output", "wk", NB], check=True,
                       stdout=subprocess.DEVNULL)
        html = open(os.path.join(td, "wk.html"), encoding="utf-8").read()

    # nbconvert titles the page after the notebook FILENAME
    # ("trishuli_workings"), which is what a reader would see in the browser
    # tab and in a shared link preview. Name it properly.
    title = "Trishuli Model Workings"

    head = html[:html.index("</head>")]
    styles = re.findall(r"<style\b[^>]*>.*?</style>", head, re.S | re.I)

    body = html[html.index("<body"):]
    body = body[body.index(">") + 1:]
    body = re.sub(r"</body>.*", "", body, flags=re.S | re.I).strip()

    # nbconvert cannot know what a matplotlib output shows, so it emits
    # alt="No description has been provided for this image" on every figure —
    # which is worse than useless read aloud. Point at the prose instead, which
    # does describe each one.
    body, n_alt = re.subn(
        r'alt="No description has been provided for this image"',
        'alt="Figure produced by the code cell above; described in the '
        'surrounding text."', body)

    frag = (f"<title>{title}</title>\n"
            + "\n".join(styles) + "\n" + CHROME.strip() + "\n\n"
            + NAV + body + "\n")
    open(OUT, "w", encoding="utf-8").write(frag)
    print(f"report/workings.html  {len(frag) // 1024} KB  "
          f"({len(styles)} style blocks, nav injected, {n_alt} alts fixed)")


if __name__ == "__main__":
    main()
