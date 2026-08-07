#!/usr/bin/env python3
"""Build a single-file, self-contained snapshot of the running shop.

Useful for sharing a look at the site without deploying it: several real
rendered pages are captured, the stylesheet and every SVG illustration are
inlined, and internal links are rewritten to switch between the captured
pages client-side.

Interactive behaviour that needs the server (checkout, sign-in, search) is
disabled in the snapshot — it is a look, not a working shop.

    python3 tools/build_preview.py http://127.0.0.1:8020 preview.html
"""

from __future__ import annotations

import base64
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (url path, id used in the snapshot, label for the page switcher)
PAGES = [
    ("/", "home", "Home"),
    ("/flowers", "flowers", "All flowers"),
    ("/product/grafton-rose-hatbox", "product", "Product page"),
    ("/occasions", "occasions", "Occasions"),
    ("/delivery", "delivery", "Delivery"),
    ("/about", "about", "Our studio"),
    ("/flower-delivery/dublin", "dublin", "Dublin landing page"),
    ("/faq", "faq", "FAQ"),
]

PATH_TO_ID = {path: page_id for path, page_id, _ in PAGES}


def fetch(base, path):
    with urllib.request.urlopen(base + path, timeout=30) as response:
        return response.read().decode("utf-8")


def data_uri(rel_path):
    """Inline a static file as a base64 data URI."""
    full = os.path.join(ROOT, "static", rel_path)
    if not os.path.exists(full):
        return None
    with open(full, "rb") as handle:
        payload = base64.b64encode(handle.read()).decode("ascii")
    return f"data:image/svg+xml;base64,{payload}"


def extract_body(html):
    match = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
    return match.group(1) if match else html


def rewrite(body):
    """Inline images and repoint links at the snapshot's own sections."""
    # Inline every /static/img/... reference.
    def image_sub(match):
        quote, path = match.group(1), match.group(2)
        uri = data_uri(path)
        return f"src={quote}{uri or ''}{quote}"

    body = re.sub(r'src=(["\'])/static/(img/[^"\']+)\1', image_sub, body)

    # The artwork is embedded in the file, so deferring it buys nothing and
    # leaves blank frames when switching between captured pages.
    body = body.replace(' loading="lazy"', "")

    # Drop the stylesheet link and script tag; both are handled separately.
    body = re.sub(r'<link[^>]+stylesheet[^>]*>', "", body)
    body = re.sub(r"<script[^>]*></script>", "", body)

    # Point internal links at captured pages, and neutralise the rest.
    def link_sub(match):
        quote, href = match.group(1), match.group(2)
        if href in PATH_TO_ID:
            return f'href={quote}#{PATH_TO_ID[href]}{quote} data-nav'
        return f'href={quote}#{quote} data-inert'

    body = re.sub(r'href=(["\'])(/[^"\'#]*)\1', link_sub, body)

    # Forms would post to a server that is not there.
    body = re.sub(r"<form", '<form onsubmit="return false"', body)
    return body


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8020"
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "preview.html")

    with open(os.path.join(ROOT, "static", "css", "style.css"), encoding="utf-8") as f:
        css = f.read()

    sections = []
    for path, page_id, _label in PAGES:
        print(f"  capturing {path}")
        body = rewrite(extract_body(fetch(base, path)))
        sections.append(
            f'<section class="snap-page" id="{page_id}" '
            f'{"" if page_id == "home" else "hidden"}>{body}</section>'
        )

    switcher = "".join(
        '<button type="button" data-goto="{0}"{1}>{2}</button>'.format(
            page_id,
            ' class="is-active"' if page_id == "home" else "",
            label,
        )
        for _path, page_id, label in PAGES
    )

    page = f"""<title>Nested Blooms — site preview</title>
<style>
{css}

/* ---- snapshot chrome (not part of the real site) ---- */
.snap-bar {{
  position: sticky; top: 0; z-index: 500;
  display: flex; align-items: center; gap: .5rem; flex-wrap: wrap;
  padding: .6rem 1rem; background: #12261d; color: #e6e0d6;
  font: 500 13px/1.4 var(--sans); border-bottom: 2px solid #b8934a;
}}
.snap-bar strong {{ font-family: var(--serif); font-size: 15px; margin-right: .5rem; }}
.snap-bar button {{
  padding: .35rem .8rem; border-radius: 999px; cursor: pointer;
  background: transparent; color: #cfd8cf;
  border: 1px solid rgba(255,255,255,.25); font: inherit;
}}
.snap-bar button:hover {{ background: rgba(255,255,255,.1); color: #fff; }}
.snap-bar button.is-active {{ background: #b8934a; border-color: #b8934a; color: #201a10; }}
.snap-note {{ margin-left: auto; font-size: 12px; opacity: .7; }}
.snap-page .header {{ top: 44px; }}
[data-inert] {{ cursor: default; }}
@media (max-width: 700px) {{ .snap-note {{ display: none; }} }}
</style>

<div class="snap-bar">
  <strong>Nested Blooms</strong>
  {switcher}
  <span class="snap-note">Static preview — checkout &amp; search need the live app</span>
</div>

{"".join(sections)}

<script>
(function () {{
  var pages = Array.prototype.slice.call(document.querySelectorAll('.snap-page'));
  var buttons = Array.prototype.slice.call(document.querySelectorAll('[data-goto]'));

  function show(id) {{
    var found = false;
    pages.forEach(function (p) {{
      var match = p.id === id;
      p.hidden = !match;
      if (match) found = true;
    }});
    if (!found) {{ pages[0].hidden = false; id = pages[0].id; }}
    buttons.forEach(function (b) {{
      b.classList.toggle('is-active', b.dataset.goto === id);
    }});
    window.scrollTo(0, 0);
  }}

  buttons.forEach(function (b) {{
    b.addEventListener('click', function () {{
      history.replaceState(null, '', '#' + b.dataset.goto);
      show(b.dataset.goto);
    }});
  }});

  document.addEventListener('click', function (e) {{
    var link = e.target.closest('a');
    if (!link) return;
    var hash = (link.getAttribute('href') || '').replace('#', '');
    if (link.hasAttribute('data-nav')) {{
      e.preventDefault();
      history.replaceState(null, '', '#' + hash);
      show(hash);
    }} else if (link.hasAttribute('data-inert')) {{
      e.preventDefault();
    }}
  }});

  // Accordions on the product and FAQ pages, so they are explorable.
  document.querySelectorAll('.accordion__trigger').forEach(function (t, i) {{
    var panel = document.getElementById(t.getAttribute('aria-controls'));
    if (!panel) return;
    var open = i === 0;
    t.setAttribute('aria-expanded', String(open));
    panel.hidden = !open;
    t.addEventListener('click', function () {{
      var isOpen = t.getAttribute('aria-expanded') === 'true';
      t.setAttribute('aria-expanded', String(!isOpen));
      panel.hidden = isOpen;
    }});
  }});

  show((location.hash || '#home').slice(1));
}})();
</script>
"""

    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(page)

    size = os.path.getsize(out_path)
    print(f"\nWrote {out_path} — {size / 1024 / 1024:.1f}MB, {len(PAGES)} pages")
    if size > 15_500_000:
        print("WARNING: close to the 16MB artifact limit")


if __name__ == "__main__":
    main()
