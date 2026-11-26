# Sphinx configuration for the site that holds both tutorials (built from the exported repository's root).
import os
import re
from pathlib import Path

project = "Teaching a small robot dog to walk"
html_title = project
author = "MangDang Technology Co., Limited"
copyright = "2026, MangDang Technology Co., Limited. Text and our own media under CC BY 4.0"

extensions = ["myst_parser"]
source_suffix = {".md": "markdown"}
root_doc = "index"
exclude_patterns = ["README.md", "_static", "_build", "_readthedocs", ".venv", "LICENSE"]

# Read the Markdown the way GitHub shows it.
myst_heading_anchors = 3
myst_enable_extensions = ["html_image", "attrs_inline"]
smartquotes = False
highlight_language = "none"
suppress_warnings = ["image.nonlocal_uri"]

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "")
html_show_sourcelink = False

linkcheck_ignore = [r"http://localhost:\d+"]

# While the site is under review, ask search engines not to list it. Set to False at release.
NOINDEX = True


def _page_context(app, pagename, templatename, context, doctree):
    if NOINDEX:
        context["metatags"] = context.get("metatags", "") + '\n<meta name="robots" content="noindex">'


def _lazy_images(app, exception):
    # Every image loads only when the reader scrolls near it (the GIFs are large).
    if exception or app.builder.format != "html":
        return
    for page in Path(app.outdir).rglob("*.html"):
        html = page.read_text(encoding="utf-8")
        new = re.sub(r"<img (?![^>]*\bloading=)", '<img loading="lazy" ', html)
        if new != html:
            page.write_text(new, encoding="utf-8")


def setup(app):
    app.connect("html-page-context", _page_context)
    app.connect("build-finished", _lazy_images)
