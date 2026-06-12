#!/usr/bin/env python3
"""EPOE dashboard build: inline dashboard/epoe-model.js into
dashboard/index.template.html and write the self-contained index.html at the
repository root (which GitHub Pages serves directly).

Run from the repository root:  python dashboard/build.py
"""
import pathlib

root = pathlib.Path(__file__).resolve().parent.parent
model = (root / "dashboard" / "epoe-model.js").read_text()
template = (root / "dashboard" / "index.template.html").read_text()

marker = "/*__EPOE_MODEL__*/"
assert marker in template, "marker missing from template"
# guard against accidental </script> termination inside the inlined source
assert "</script" not in model.lower(), "model source may not contain </script>"

out = template.replace(marker, model)
(root / "index.html").write_text(out)
print(f"wrote {root/'index.html'} ({len(out):,} bytes)")
