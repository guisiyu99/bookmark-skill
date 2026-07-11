---
name: chrome-bookmark-organizer
description: >-
  A personal toolkit + workflow for cleaning up YOUR OWN currently-messy Chrome /
  Chromium bookmarks by editing the local Bookmarks JSON file. Covers analysis,
  dead-duplicate-outdated detection, taxonomy design, and a Sync-safe rewrite.
  NOT a pre-made bookmark collection to share or import.
  一套用于整理「你自己」当前错乱的 Chrome 书签的本地工作流与工具包：解析、
  失效/重复检测、分类设计，以及能扛住 Chrome 同步的安全重写。它不是一份
  拿来分享或导入的现成书签合集。
agent_created: true
---

# Chrome Bookmark Organizer / Chrome 书签整理

## Overview / 概述

**EN** — A personal toolkit + workflow for cleaning up **your own** currently-messy
Chrome (or Chromium-based) bookmarks, by editing the `Bookmarks` JSON file on
**your** machine. It gives you analysis scripts, a dead-bookmark detector, and a
safe rewrite workflow that survives Chrome Sync instead of being silently
reverted.

This is a **method / toolkit you run on your own browser** — it is **NOT** a
pre-made bookmark collection to import or share with others. The "547 → 414"
numbers mentioned below are only a real *worked example* of what this workflow
achieved for one user; your result and your taxonomy will be your own.

**中文** — 一套个人工具 + 工作流，用于整理**你自己**当前错乱的 Chrome（或
Chromium 系）书签——直接编辑**你本机**的 `Bookmarks` JSON 文件。它提供分析脚本、
失效书签检测，以及一套能扛住 Chrome 同步、不会被悄悄还原的安全重写流程。

这是一个**你在本机浏览器上运行的方法 / 工具包**——**不是**一份拿来导入或
分享给他人的现成书签合集。下文提到的「547→414」只是一个真实的「跑通这套流程」
的**示例数字**；你的结果和分类体系都会是你自己的。

## When To Use / 触发场景

**EN** — Trigger this skill when the user:
- Asks to "整理 / 清理 / 分类 / 去重" their own Chrome bookmarks.
- Reports messy bookmarks, duplicates, or "old/unused" links on their machine.
- Wants a backup export of their own bookmarks (HTML).
- Mentions Chrome Sync reverting or re-merging their bookmark changes.

**中文** — 当用户出现以下情况时触发：
- 要求「整理 / 清理 / 分类 / 去重」**自己**的 Chrome 书签。
- 反映本机书签乱、有重复、或堆了一堆「老旧的 / 不用的」链接。
- 想要给自己导出一个书签备份（HTML）。
- 提到 Chrome 同步把改动还原 / 又把旧书签合并回来了。

## Prerequisites & Safety (do this first) / 前置与安全（先做这些）

1. **Locate the profile.** / **定位配置文件。** Find the active profile dir
   (`Default` or `Profile N` under the Chrome user-data dir). The `Bookmarks`
   file lives inside it. 找活跃配置文件目录（Chrome 用户数据目录下的 `Default`
   或 `Profile N`），`Bookmarks` 文件就在里面。
2. **Close Chrome before editing.** / **改文件前先关掉 Chrome。** A running
   instance overwrites your changes. See Gotcha #3 for the *correct* way to close.
   浏览器开着会覆盖你的改动。正确关闭方式见雷区 #3。
3. **Always back up.** / **一定要先备份。** Copy `Bookmarks` to
   `Bookmarks.bak.<tag>` before any mutation. 任何改动前先复制一份
   `Bookmarks` 为 `Bookmarks.bak.<tag>`。

macOS path / macOS 路径:
`~/Library/Application Support/Google/Chrome/Default/Bookmarks`
Windows path / Windows 路径:
`%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks`

## Workflow / 工作流

### Step 1 — Read & parse the Bookmarks file / 读取并解析
**EN** — The file is one JSON doc:
`{ "roots": { "bookmark_bar": {...}, "other": {...}, "synced": {...} } }`.
Each node is `{type:"folder", name, children:[...]}` or
`{type:"url", name, url, date_added, date_last_used}`. Chrome timestamps are
**microseconds since 1601-01-01**; convert via `unix = ts/1e6 - 11644473600`.
Run `scripts/analyze_bookmarks.py` to print a tree, count duplicates, and report
never-used / very-old bookmarks.

**中文** — 文件是单个 JSON：`{ "roots": { "bookmark_bar": {...}, "other": {...},
"synced": {...} } }`。每个节点是文件夹 `{type:"folder", name, children:[...]}`
或网址 `{type:"url", name, url, date_added, date_last_used}`。Chrome 时间戳是
**自 1601-01-01 起的微秒数**，换算：`unix = ts/1e6 - 11644473600`。运行
`scripts/analyze_bookmarks.py` 可打印书签树、统计重复、并报告从未使用 / 超老的书签。

### Step 2 — Diagnose classification problems / 诊断分类问题
**EN** — Look for: top-level scattered bookmarks (not in any folder), mixed
taxonomy dimensions (content-type vs project vs purpose vs style vs tool all
mixed), duplicate bookmarks (same URL in 2+ places), "junk-drawer" folders
(one giant folder absorbing everything), misplaced bookmarks (personal links
inside work folders), and inconsistent naming / depth.

**中文** — 检查：顶层散落的书签（不在任何文件夹里）、维度混乱（内容类型 / 项目 /
用途 / 风格 / 工具混在一起）、重复书签（同一 URL 出现 2 次以上）、「垃圾桶」式
文件夹（一个大文件夹啥都装）、错位的书签（个人链接塞进工作文件夹）、以及命名 /
层级不一致。

### Step 3 — Identify dead / duplicate / outdated bookmarks / 找出失效/重复/陈旧项
**EN** — Run `scripts/find_dead_bookmarks.py`, which matches URLs against a
curated list of dead/closed services (see `references/dead_domains.md`):
discontinued apps, dead design-nav sites, deprecated component libs, expired
Baidu-pan shares, and `baidu.com/link?url=` redirect stubs. It also flags
`chrome://` internal pages, untitled bookmarks, and HTTP-only links. **Always let
the user confirm the delete list — it is destructive.** This script never deletes.

**中文** — 运行 `scripts/find_dead_bookmarks.py`，它把 URL 对照一份「已关闭 / 停更
服务」清单（见 `references/dead_domains.md`）：停更的 App、死掉的设计导航站、过时的
组件库、失效的百度网盘分享、以及 `baidu.com/link?url=` 跳转桩。它还会标出
`chrome://` 内部页、无标题书签、HTTP 非 HTTPS 链接。**一定要让用户确认删除清单——
这是破坏性的操作。** 本脚本绝不自动删除。

### Step 4 — Design a clean taxonomy / 设计干净的分类
**EN** — Recommend a **single classification dimension** (usually by *purpose /
用途*) to replace the mixed dimensions. Design *your own* structure; the example
below is only what one user ended up with — do not treat it as the target.

Example structure (worked case, not a prescription) / 示例结构（真实案例，非标准答案）:
- 6–8 pinned bookmarks on the bar (whatever the user names as "must stay visible").
  书签栏钉 6–8 个常用（用户点名「必须常驻」的那些）。
- Folders such as: AI工具 / 作品集 / 设计素材 / 设计灵感 / 设计规范 / 工作项目 / 个人常用.
  文件夹例如：AI工具 / 作品集 / 设计素材 / 设计灵感 / 设计规范 / 工作项目 / 个人常用。
- Merge overlapping junk folders into the new structure; keep platform-specific
  favorites the user explicitly names (e.g. 站酷/ZCOOL collection) even if old.
  把重叠的垃圾桶文件夹并入新结构；用户明确点名要留的平台收藏（如站酷）即便显旧也保留。

### Step 5 — Reorganize safely (the part that usually fails) / 安全重写（最容易翻车的一步）
**EN** — Build the target structure as a Python dict (top-level bookmarks +
folders→subfolders→urls) and generate a fresh, valid `Bookmarks` JSON with
`scripts/reorganize_bookmarks.py`. **Then handle Chrome Sync — see Gotcha #1.**
The naive "edit the file and reopen Chrome" approach merges the old cloud
bookmarks back in.

**中文** — 把目标结构写成一个 Python dict（顶层书签 + 文件夹→子文件夹→网址），用
`scripts/reorganize_bookmarks.py` 生成一份新的、合法的 `Bookmarks` JSON。
**然后务必处理 Chrome 同步——见雷区 #1。** 那种「改完文件重开浏览器」的朴素做法，
会把云端旧书签又合并回来。

### Step 6 — Export a backup / 导出备份
**EN** — After the new structure is in place, export to Netscape HTML
(`<DT><A HREF=...>` format) so *you* can re-import anywhere. Generate the HTML
directly from the JSON, or extend `analyze_bookmarks.py`.

**中文** — 新结构就位后，导出成 Netscape 格式 HTML（`<DT><A HREF=...>`），方便**你**
随时再导入。可直接从 JSON 生成，或扩展 `analyze_bookmarks.py`。

## Critical Gotchas / 关键雷区

### Gotcha #1 — Chrome Sync is cloud-led; editing the local file gets reverted
**EN** — If the user is signed in with Sync enabled, any local `Bookmarks` edit is
**merged** with the server copy on next launch (old + new coexist → count balloons,
e.g. 547→923). Disabling Sync by editing `Preferences` keys (`sync.requested=False`
etc.) does **NOT** work — Chrome re-validates and restores its own sync state on
startup.

**What actually works:** Confirm Sync is genuinely off. Check `Preferences`:
`google.services.consented_to_sync == false`, `sync.requested == false`,
`sync.data_type_status_for_sync_to_signin.bookmarks == false`. If all false, the
local file is authoritative and a write will stick. Then: close Chrome properly →
back up → write the clean `Bookmarks` → also clear `Sync Data/LevelDB` (the local
mirror of cloud state) → reopen normally. To later re-enable Sync without the old
bookmarks returning, the user must first **Reset Sync**
(`chrome://settings/syncSetup` → clear & reset) to wipe the server copy, then turn
Sync back on so the clean local set pushes up.

**中文** — 如果用户登录并开启了同步，本地对 `Bookmarks` 的任何改动，下次启动都会被和
**服务端**那份**合并**（旧的 + 新的共存 → 数量暴涨，比如 547→923）。靠改 `Preferences`
里的同步开关（`sync.requested=False` 等）来关同步**没用**——Chrome 启动时会重新校验
并恢复自己的同步状态。

**真正管用的做法：** 先确认同步确实关了。检查 `Preferences`：
`google.services.consented_to_sync == false`、`sync.requested == false`、
`sync.data_type_status_for_sync_to_signin.bookmarks == false`。三者全为 false 时，
本地文件才是权威的，写入才会生效。然后：正常关 Chrome → 备份 → 写入干净 `Bookmarks`
→ 再清掉 `Sync Data/LevelDB`（云端状态的本地镜像）→ 正常重开。若之后想重新开启同步又
不想让旧书签回来，必须先 **重置同步**（`chrome://settings/syncSetup` → 清除并重置）
清空服务端，再开同步，让干净的本地面板推上去。

### Gotcha #2 — Unpacked extensions cannot be loaded in this sandbox
**EN** — Auto-loading an extension via `--load-extension`, `Playwright`,
`open --args`, or even manual `chrome://extensions` (the `/tmp` path is hidden
from the file picker; moving to Desktop still failed) all failed: macOS TCC blocks
AppleScript/remote-debug control, the sandbox silently drops the flag, and
`Preferences` showed 0 installed extensions. Do not rely on an extension-based
approach in a constrained environment — go through the file directly (Gotcha #1).

**中文** — 用 `--load-extension`、Playwright、`open --args`，甚至手动去
`chrome://extensions` 加载未打包扩展（且 `/tmp` 路径在文件选择器里是隐藏的，挪到桌面
也照样失败）——全都不行：macOS TCC 拦截 AppleScript / 远程调试，沙盒静默丢弃该参数，
`Preferences` 里显示已装扩展数为 0。受限环境里别指望扩展方案，直接走文件（雷区 #1）。

### Gotcha #3 — Never force-kill Chrome
**EN** — `pkill -x "Google Chrome"` / `kill -9` skips the normal shutdown that
serializes session state. This **destroys unsaved local session state** — notably
**Tab Groups** (local-only, not synced, no standalone on-disk file). Bookmarks
survive (written to disk), but Tab Groups vanish. Always close Chrome via normal
exit (`Cmd+Q`, or AppleScript `tell application "Google Chrome" to quit` — though
TCC may block the latter, in which case ask the user to quit manually).

**中文** — `pkill -x "Google Chrome"` / `kill -9` 会跳过「序列化会话状态」的正常关闭，
从而**销毁未保存的本地会话状态**——尤其是**标签页分组（Tab Groups）**（纯本地、不同步、
磁盘上没有独立文件）。书签没事（已落盘），但标签页分组会消失。永远用正常方式退出
（`Cmd+Q`，或 AppleScript `tell application "Google Chrome" to quit`——不过可能被 TCC
拦截，那就请用户手动退出）。

## Bundled Resources / 附带资源

- `scripts/analyze_bookmarks.py` — parse, print tree, detect duplicates, timestamp analysis. / 解析、打印树、检测重复、时间戳分析。
- `scripts/find_dead_bookmarks.py` — match URLs against the dead-domain list (no delete). / 对照失效域名清单匹配（不删除）。
- `scripts/reorganize_bookmarks.py` — build target dict → emit valid `Bookmarks` JSON. / 目标结构 → 生成合法 Bookmarks JSON。
- `references/dead_domains.md` — curated list of closed/deprecated services to flag. / 已关闭 / 停更服务清单。
- `references/chrome_sync_mechanics.md` — deep dive on Sync merge behavior & the working fix. / 同步合并机制与可行修复详解。

See `references/chrome_sync_mechanics.md` before attempting Step 5 on a synced profile.
跑 Step 5 之前，若账号开着同步，务必先读 `references/chrome_sync_mechanics.md`。
