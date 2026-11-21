#!/usr/bin/env python3
"""Builds Tools/PuzzleHarvester.html from shell.html + app.js, with chess.js (BSD-2) inlined.
Usage: python Tools/harvester_src/build.py <path to chess.js ESM file (dist/esm/chess.js)>"""
import re, sys, os
here = os.path.dirname(os.path.abspath(__file__))
chess = open(sys.argv[1], encoding="utf-8").read()
chess = re.sub(r"^export \{[^}]*\};?\s*$", "", chess, flags=re.M)   # inline, so drop the ESM export line
app = open(os.path.join(here, "app.js"), encoding="utf-8").read()
shell = open(os.path.join(here, "shell.html"), encoding="utf-8").read()
out = shell.replace("/*__CHESSJS__*/", chess).replace("/*__APP__*/", app)
open(os.path.join(here, "..", "PuzzleHarvester.html"), "w", encoding="utf-8").write(out)
print("built", len(out) // 1024, "KB")
