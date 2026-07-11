#!/usr/bin/env python3
"""Flag dead / closed / outdated bookmarks for review before deletion.

This does NOT delete anything. It prints a categorized list the user must confirm.

Usage:
    python3 find_dead_bookmarks.py [--path /path/to/Bookmarks]

Matching is URL-substring based against the curated DEAD_DOMAINS list below,
plus structural checks (chrome://, baidu redirect stubs, untitled, http-only).
"""
import json, os, sys, argparse
from collections import defaultdict

DEFAULT_PATHS = [
    os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Bookmarks"),
    os.path.expanduser("~/Library/Application Support/Google/Chrome/Profile 1/Bookmarks"),
]

# Curated list of closed / deprecated / moved services. Extend as needed.
DEAD_DOMAINS = [
    # Discontinued apps / services
    "invisionapp.com", "principlerepo.com", "principleux.com", "macwk.com",
    "thenextweb.com", "sketchappsources.com", "sketchapp.com", "oursketch.com",
    "materialdesignkit.com", "uikit.me", "freebiesupply.com", "sketchsheets.com",
    "appanimations.com", "app-ealing.com", "animaticons.co", "zoommyapp.com",
    # Dead design-navigation / inspiration sites
    "seeseed.com", "hao.uisdc.com", "idesign.qq.com", "so.uigreat.com",
    "niudana.com", "spscollection.com", "findicons.com", "sketch.im", "psddd.co",
    "madefordesigners.com", "emptystat.es", "oops.re", "chuangzaoshi.com",
    "next.36kr.com", "damndigital.com", "gooddesignweb.com", "81-web.com",
    "io3000.com", "bm.straightline.jp", "ifavart.com", "designdisruptors.com",
    "thegreatdiscontent.com", "uxcoffee.co", "mvsm.com", "invesdesign.com",
    "09ui.com", "dtailstudio.com", "colorfavs.com", "materialpalette.com",
    "color.hailpixel.com", "findguidelin.es", "globe.cid.harvard.edu",
    "hollywoodcamerawork.com", "leewiart.com", "poocg.com", "cgsociety.org",
    "cargocollective.com", "arkdesign.cn", "ui.figma.cool", "element.eleme.cn",
    "iviewui.com", "layui.com", "g2.antv.vision", "axhub.im",
    # Old company-internal / competitor links
    "mkittest.cig.com.cn", "mail.cig.com.cn", "fxiaoke.com", "zhidieyun.com",
    "om.qq.com", "yunmeipai.com", "isux.tencent.com", "ldxg20201026081506491.worktile.com",
    "lanhuhu.com",
    # Old Mac-software / download sites (frequently down)
    "xclient.info", "clipconverter.cc", "savevideo.me", "macx.cn", "waitsun.com",
    # Misc dead
    "zealer.com", "youku.com", "flyme.cn", "meizu.com", "pantone.com",
    "alpha.wallhaven.cc", "zerospace.asika.tw", "vera.kkuistore.com",
]

KEEP_DOMAINS = ["zcool", "zhihu", "behance", "pinterest", "dribbble", "figma"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", help="Path to Bookmarks file")
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

    flat = []
    def collect(node, p=""):
        name = node.get("name", "")
        if node.get("type") == "url":
            flat.append({"name": name, "url": node.get("url", ""), "path": p})
        for c in node.get("children", []):
            collect(c, p + "/" + name)
    for k in ["bookmark_bar", "other", "synced"]:
        if k in roots:
            collect(roots[k], k)

    groups = defaultdict(list)
    for b in flat:
        ul = b["url"].lower()
        reason = ""
        if any(d in ul for d in KEEP_DOMAINS):
            continue
        if any(d in ul for d in DEAD_DOMAINS):
            reason = "网站已关闭/服务已停更"
        elif ul.startswith("chrome://"):
            reason = "Chrome 内部页面，无需书签"
        elif "baidu.com/link?url=" in ul:
            reason = "百度跳转临时链接（非有效 URL）"
        elif b["name"] in ("", "`"):
            reason = "无标题/无效书签"
        elif ul.startswith("http://"):
            reason = "HTTP 非 HTTPS（可能已迁移或失效）"
        elif "pan.baidu.com" in ul:
            reason = "百度网盘分享链接（大概率已失效）"
        if reason:
            groups[reason].append(b)

    print("=== 建议删除（请用户确认，本脚本不执行删除）===\n")
    total = 0
    for reason, items in groups.items():
        print(f"--- {reason}（{len(items)} 个）---")
        for it in items[:60]:
            print(f"  [{it['name'][:46]}] {it['url'][:64]}")
        if len(items) > 60:
            print(f"  … 还有 {len(items)-60} 个")
        print()
        total += len(items)
    print(f"=== 总计建议删除: {total} 个 ===")


if __name__ == "__main__":
    main()
