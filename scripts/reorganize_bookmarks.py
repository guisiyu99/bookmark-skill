#!/usr/bin/env python3
"""Generate a clean, valid Chrome Bookmarks JSON from a target-structure dict.

This is the safe-rewrite step. It only *serializes* a target structure the agent
has already built (after diagnosis + dead-link removal). It does NOT decide the
taxonomy — that is user-specific and lives in the target JSON.

CRITICAL: before writing to a live profile, Sync must be confirmed OFF
(see references/chrome_sync_mechanics.md), else Chrome merges the old cloud
bookmarks back in on next launch.

Usage:
    python3 reorganize_bookmarks.py --target target.json --output Bookmarks --backup

target.json format:
{
  "topLevel": [ {"name": "Google", "url": "https://www.google.com/"}, ... ],
  "folders": {
     "AI工具": {
        "AI对话": [ {"name": "...", "url": "..."}, ... ],
        "AI创作": [ ... ]
     },
     "设计素材": { "图标": [...], "字体": [...] },
     ...
  }
}
"""
import json, os, sys, time, argparse, shutil

CHROME_EPOCH = 11644473600
_counter = [0]


def now_ts():
    return str(int((time.time() + CHROME_EPOCH) * 1e6))


def next_id():
    _counter[0] += 1
    return str(_counter[0])


def make_url(name, url):
    return {
        "type": "url",
        "id": next_id(),
        "name": name,
        "url": url,
        "date_added": now_ts(),
        "date_last_used": "0",
    }


def make_folder(name, children):
    return {
        "type": "folder",
        "id": next_id(),
        "name": name,
        "date_added": now_ts(),
        "date_last_modified": now_ts(),
        "children": children,
    }


def build_node(name, node):
    """Recursively build a node from a target dict/list."""
    if isinstance(node, list):
        return make_url(name, node) if isinstance(node, str) else [
            make_url(i["name"], i["url"]) for i in node
        ]
    if isinstance(node, dict):
        children = [build_node(sub, subnode) for sub, subnode in node.items()]
        return make_folder(name, children)
    # raw string leaf
    return make_url(name, str(node))


def build(target):
    bar_children = []
    for t in target.get("topLevel", []):
        bar_children.append(make_url(t["name"], t["url"]))
    for fname, sub in target.get("folders", {}).items():
        bar_children.append(build_node(fname, sub))
    return bar_children


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True, help="target structure JSON")
    ap.add_argument("--output", required=True, help="output Bookmarks path")
    ap.add_argument("--backup", action="store_true", help="back up output first")
    args = ap.parse_args()

    target = json.load(open(args.target, encoding="utf-8"))

    bar = make_folder("书签栏", build(target))
    other = make_folder("其他书签", [])
    synced = make_folder("synced", [])

    doc = {
        "roots": {
            "bookmark_bar": bar,
            "other": other,
            "synced": synced,
        },
        "version": 1,
    }

    if args.backup and os.path.exists(args.output):
        shutil.copy(args.output, args.output + ".bak.reorganize")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)

    total = [0]
    def cnt(n):
        if n["type"] == "url":
            total[0] += 1
        for c in n.get("children", []):
            cnt(c)
    cnt(bar)
    print(f"已生成: {args.output}")
    print(f"书签总数: {total[0]} (顶层 {len(bar['children'])} 项)")


if __name__ == "__main__":
    main()
