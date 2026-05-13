#!/usr/bin/env python3
"""Regenerate index.html with a tree of all html files on this branch."""
from pathlib import Path
from datetime import datetime, timezone
import subprocess
import html

ROOT = Path(__file__).parent
EXCLUDE_NAMES = {"index.html"}
EXCLUDE_DIRS = {".git", ".github"}

def collect():
    files = []
    for p in sorted(ROOT.rglob("*.html")):
        if any(seg in EXCLUDE_DIRS for seg in p.relative_to(ROOT).parts):
            continue
        if p.name in EXCLUDE_NAMES and p.parent == ROOT:
            continue
        files.append(p.relative_to(ROOT))
    return files

def fmt_size(n):
    if n < 1024: return f"{n}B"
    if n < 1024 * 1024: return f"{n / 1024:.1f}K"
    return f"{n / 1024 / 1024:.1f}M"

def build_tree(paths):
    root = {"dirs": {}, "files": []}
    for rel in paths:
        parts = rel.parts
        node = root
        for seg in parts[:-1]:
            node = node["dirs"].setdefault(seg, {"dirs": {}, "files": []})
        node["files"].append({"name": parts[-1], "path": str(rel), "size": (ROOT / rel).stat().st_size})
    return root

def render_node(node, prefix, lines):
    dirs = sorted(node["dirs"].items())
    files = sorted(node["files"], key=lambda f: f["name"])
    entries = [("dir", n, sub) for n, sub in dirs] + [("file", f["name"], f) for f in files]
    for i, (kind, name, payload) in enumerate(entries):
        last = i == len(entries) - 1
        branch = "└── " if last else "├── "
        next_prefix = prefix + ("    " if last else "│   ")
        if kind == "dir":
            lines.append(f'{html.escape(prefix)}<span class="branch">{branch}</span><span class="dir">{html.escape(name)}/</span>')
            render_node(payload, next_prefix, lines)
        else:
            pad = " " * max(1, 42 - (len(prefix) + len(branch) + len(name)))
            href = "./" + payload["path"]
            lines.append(
                f'{html.escape(prefix)}<span class="branch">{branch}</span>'
                f'<a href="{html.escape(href)}">{html.escape(name)}</a>'
                f'{pad}<span class="size">{fmt_size(payload["size"])}</span>'
            )

def git_info():
    try:
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        sha = "—"
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        branch = "—"
    return sha, branch

TEMPLATE = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>cool_page/</title>
<style>
:root {{ --bg:#0e0b09; --ink:#f5f0e8; --ink-dim:#b5ac9d; --ink-mute:#6b6358; --line:#2a2520; --amber:#f4b942; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:var(--bg); color:var(--ink); font-family:ui-monospace,'JetBrains Mono','SF Mono',Menlo,monospace; font-size:14px; line-height:1.7; padding:6vh 5vw; min-height:100vh; }}
header {{ margin-bottom:32px; padding-bottom:16px; border-bottom:1px solid var(--line); }}
.title {{ color:var(--amber); font-size:16px; }}
.title::before {{ content:'$ '; color:var(--ink-mute); }}
.cmd {{ color:var(--ink-dim); margin-top:6px; font-size:12px; }}
.cmd::before {{ content:'# '; color:var(--ink-mute); }}
.meta {{ color:var(--ink-mute); font-size:11px; margin-top:12px; letter-spacing:0.05em; }}
.tree {{ white-space:pre; color:var(--ink-dim); }}
.tree a {{ color:var(--ink); text-decoration:none; border-bottom:1px dotted transparent; }}
.tree a:hover {{ color:var(--amber); border-bottom-color:var(--amber); }}
.tree .dir {{ color:var(--amber); }}
.tree .branch {{ color:var(--ink-mute); }}
.tree .size {{ color:var(--ink-mute); font-size:11px; }}
footer {{ margin-top:40px; padding-top:16px; border-top:1px solid var(--line); font-size:11px; color:var(--ink-mute); letter-spacing:0.05em; }}
footer a {{ color:var(--ink-mute); text-decoration:none; border-bottom:1px dotted var(--line); }}
footer a:hover {{ color:var(--amber); }}
</style>
</head>
<body>
<header>
  <div class="title">tree cool_page/</div>
  <div class="cmd">git branch: {branch} · github.com/TerryKiddy/cool_page</div>
  <div class="meta">generated {timestamp} · {dir_count} director{dir_plural}, {file_count} file{file_plural} · rev {sha}</div>
</header>
<pre class="tree"><span class="dir">cool_page/</span>
{tree_body}
</pre>
<footer>
  <a href="https://github.com/TerryKiddy/cool_page/tree/gh-pages" target="_blank" rel="noopener">source ↗</a>
</footer>
</body>
</html>
"""

def main():
    files = collect()
    tree = build_tree(files)
    lines = []
    render_node(tree, "", lines)
    body = "\n".join(lines)
    file_count = len(files)
    dir_count = len({str(Path(f).parent) for f in files if str(Path(f).parent) != "."})
    sha, branch = git_info()
    out = TEMPLATE.format(
        branch=html.escape(branch),
        sha=html.escape(sha),
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        dir_count=dir_count,
        dir_plural="y" if dir_count == 1 else "ies",
        file_count=file_count,
        file_plural="" if file_count == 1 else "s",
        tree_body=body,
    )
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    print(f"wrote index.html · {file_count} file(s), {dir_count} dir(s)")

if __name__ == "__main__":
    main()
