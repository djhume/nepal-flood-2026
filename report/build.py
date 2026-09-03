#!/usr/bin/env python3
"""Assemble report.html from report.src.html: inject chart JSON + links."""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "report.src.html")).read()
chart = open(os.path.join(HERE, "chart_data.json")).read()
assert "</script" not in chart
src = src.replace("{{CHART_DATA}}", chart)
workings_url = sys.argv[1] if len(sys.argv) > 1 else ""
if workings_url:
    src = src.replace("{{WORKINGS_URL}}", workings_url)
assert "{{CHART_DATA}}" not in src
open(os.path.join(HERE, "report.html"), "w").write(src)
print(f"report.html {len(src)//1024} KB"
      + ("" if "{{WORKINGS_URL}}" not in src else "  (WORKINGS_URL unresolved)"))
