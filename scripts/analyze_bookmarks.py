#!/usr/bin/env python3
"""Analyze a Chrome/Chromium Bookmarks JSON file.

Usage:
    python3 analyze_bookmarks.py [--path /path/to/Bookmarks] [--tree] [--stale-days 2000]

Outputs:
    - total bookmark count
    - duplicate URL groups
    - never-used / very-old bookmarks (by timestamp)
    - optional folder tree with per-folder counts
"""
import json, os, sys, time, argparse
from collections import defaultdict

DEFAULT_PATHS = [
    os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Bookmarks"),
    os.path.expanduser("~/Library/Application Support/Google/Chrome/Profile 1/Bookmarks"),
]
if os.environ.get("LOCALAPPDATA"):
    DEFAULT_PATHS.append(
        os.path.join(os.environ["LOCALAPPDATA"], "Google/Chrome/User Data/Default/Bookmarks")
    )


def chrome_to_unix(ts):
    """Chrome timestamps are microseconds since 1601-01-01."""
    try:
        ts = int(ts)
        if ts == 0:
            return 0
        return ts / 1e6 - 11644473600
    except Exception:
        return 0


def collect(node, acc, path=""):
    name = node.get("name", "")
    if node.get("type") == "url":
        acc.append({
            "name": name,
            "url": node.get("url", ""),
            "path": path,
            "date_added": node.get("date_added", "0"),
            "date_last_used": node.get("date_last_used", "0"),
        })
    for c in node.get("children", []):
        collect(c, acc, path + "/" + name)


def folder_count(node):
    if node.get("type") == "url":
        return 1
    return sum(folder_count(c) for c in node.get("children", []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", help="Path to Bookmarks file")
    ap.add_argument("--tree", action="store_true", help="Print folder tree")
    ap.add_argument("--stale-days", type=int, default=2000, help="Age threshold in days")
    args = ap.parse_args()

    path = args.path
    if not path:
        for p in DEFAULT_PATHS:
            if p and os.path.exists(p):
                path = p
                break
    if not path or not os.path.exists(path):
        print("Bookmarks file not found. Pass --path.", file=sys.stderr)
        sys.exit(1)

    data = json.load(open(path, encoding="utf-8"))
    roots = data.get("roots", {})

    bookmarks = []
    for k in ["bookmark_bar", "other", "synced"]:
        if k in roots:
            collect(roots[k], bookmarks, k)

    total = len(bookmarks)
    print(f"书签文件: {path}")
    print(f"总书签数: {total}")

    # Duplicates by URL
    by_url = defaultdict(list)
    for b in bookmarks:
        by_url[b["url"]].append(b)
    dups = {u: xs for u, xs in by_url.items() if len(xs) > 1}
    print(f"\n重复 URL 组数: {len(dups)} (共 {sum(len(x) for x in dups.values())} 个书签)")
    for u, xs in list(dups.items())[:25]:
        print(f"  • {u[:72]}")
        for x in xs:
            print(f"      - {x['name'][:38]}  ({x['path']})")

    # Timestamps
    now = time.time()
    never_used = [b for b in bookmarks if chrome_to_unix(b["date_last_used"]) == 0]
    old = [b for b in bookmarks
           if (now - chrome_to_unix(b["date_added"])) / 86400 > args.stale_days]
    print(f"\n从未使用过 (date_last_used=0): {len(never_used)}")
    print(f"添加超过 {args.stale_days} 天 (~{args.stale_days/365:.1f} 年): {len(old)}")

    if args.tree:
        print("\n=== 书签树（文件夹含计数）===")
        for k in ["bookmark_bar", "other", "synced"]:
            if k in roots:
                _print_tree(roots[k], 0)


def _print_tree(node, depth):
    if node.get("type") == "folder":
        print("  " * depth + f"📁 {node['name']} ({folder_count(node)})")
        for c in node.get("children", []):
            _print_tree(c, depth + 1)
    elif node.get("type") == "url":
        print("  " * depth + f"🔖 {node['name'][:40]}")


if __name__ == "__main__":
    main()
