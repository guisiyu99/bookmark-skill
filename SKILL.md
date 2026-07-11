---
name: chrome-bookmark-organizer
description: This skill should be used when a user wants to clean up, deduplicate, reorganize, analyze, or back up their Chrome (or Chromium-based) bookmarks. It covers reading the Bookmarks JSON file, diagnosing classification problems, finding dead/duplicate/outdated bookmarks, designing a clean taxonomy, and safely rewriting the file. It also documents the critical, non-obvious gotchas that break naive approaches: Chrome Sync is cloud-led (edits get merged/overwritten from the server), unpacked extensions cannot be loaded in a sandboxed/macOS environment, and force-killing Chrome destroys unsaved session state (e.g. Tab Groups).
agent_created: true
---

# Chrome Bookmark Organizer

## Overview

Clean and reorganize a user's Chrome bookmarks directly by editing the `Bookmarks` JSON
file (located at `~/Library/Application Support/Google/Chrome/Default/Bookmarks` on macOS,
`%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks` on Windows). The skill provides
analysis scripts, a dead-bookmark detector, and a safe rewrite workflow that survives Chrome
Sync instead of being silently reverted.

## When To Use

Trigger this skill when the user:
- Asks to "整理 / 清理 / 分类 / 去重" their Chrome bookmarks
- Reports messy bookmarks, duplicates, or "old/unused" links
- Wants a backup export of their bookmarks (HTML)
- Mentions Chrome Sync reverting or re-merging their bookmark changes

## Prerequisites & Safety (do this first)

1. **Locate the profile.** Find the active profile directory. Look for `Default` or
   `Profile N` under the Chrome user-data dir. The `Bookmarks` file lives inside it.
2. **Close Chrome before editing.** Failure to do so causes the running instance to
   overwrite changes. See Gotcha #3 for the *correct* way to close Chrome.
3. **Always back up.** Copy `Bookmarks` to `Bookmarks.bak.<tag>` before any mutation.
   Keep the pre-edit copy around — it is the only way to recover if something goes wrong.

## Workflow

### Step 1 — Read & parse the Bookmarks file
The file is a single JSON document: `{ "roots": { "bookmark_bar": {...}, "other": {...}, "synced": {...} } }`.
Each node is either `{type:"folder", name, children:[...]}` or `{type:"url", name, url, date_added, date_last_used}`.
Chrome timestamps are **microseconds since 1601-01-01**; convert to Unix via
`unix = ts/1e6 - 11644473600`.

Run `scripts/analyze_bookmarks.py` to print a tree, count duplicates, and report
never-used / very-old bookmarks.

### Step 2 — Diagnose classification problems
Look for: top-level scattered bookmarks (not in any folder), mixed taxonomy dimensions
(content-type vs project vs purpose vs style vs tool all mixed), duplicate bookmarks
(same URL in 2+ places), "junk-drawer" folders (one giant folder absorbing everything),
misplaced bookmarks (personal links inside work folders), and不规范 naming / inconsistent depth.

### Step 3 — Identify dead / duplicate / outdated bookmarks
Run `scripts/find_dead_bookmarks.py`, which matches URLs against a curated list of
dead/closed services (see `references/dead_domains.md`): Sketch-era sites, discontinued
apps (Principle/InVision), dead design-nav sites, deprecated component libs (iView/Layui
old versions), expired Baidu-pan shares, and `baidu.com/link?url=` redirect stubs.
Also flag: `chrome://` internal pages, untitled/`` bookmarks, HTTP-only (non-HTTPS) links.
Always let the user confirm the delete list — it is destructive.

### Step 4 — Design a clean taxonomy
Recommend a **single classification dimension** (by *purpose/用途*) to replace the mixed
dimensions. Typical top-level set:
- 6–8 pinned bookmarks on the bar (Google, Gmail, YouTube, 百度, 翻译, Figma — whatever the
  user names as "must stay visible")
- Folders such as: AI工具 / 作品集 / 设计素材 / 设计灵感 / 设计规范 / 工作项目 / 个人常用
- Merge overlapping junk folders into the new structure; keep platform-specific favorites
  the user explicitly names (e.g. 站酷/ZCOOL collection) even if they look old.

### Step 5 — Reorganize safely (the part that usually fails)
Build the target structure as a Python dict (top-level bookmarks + folders→subfolders→urls)
and generate a fresh, valid `Bookmarks` JSON with `scripts/reorganize_bookmarks.py`.
**Then handle Chrome Sync — see Gotcha #1.** The naive "edit the file and reopen Chrome"
approach merges the old cloud bookmarks back in.

### Step 6 — Export a backup
After the new structure is in place, export to Netscape HTML
(`<DT><A HREF=...>` format) so the user can re-import anywhere. `analyze_bookmarks.py`
can be extended, or generate the HTML directly from the JSON.

## Critical Gotchas

### Gotcha #1 — Chrome Sync is cloud-led; editing the local file gets reverted
If the user is signed in with Sync enabled, any local `Bookmarks` edit is **merged** with the
server copy on next launch (old + new coexist → bookmark count balloons, e.g. 547→923).
Disabling Sync by editing `Preferences` keys (`sync.requested=False` etc.) does **NOT** work —
Chrome re-validates and restores its own sync state on startup.

**What actually works:**
- Confirm Sync is genuinely off. Check `Preferences`:
  `google.services.consented_to_sync == false`, `sync.requested == false`,
  `sync.data_type_status_for_sync_to_signin.bookmarks == false`. If all false, the local
  file is authoritative and a write will stick.
- Then: close Chrome properly → back up → write the clean `Bookmarks` → also clear
  `Sync Data/LevelDB` (the local mirror of cloud state) → reopen normally. The clean data
  persists because there is nothing to merge from.
- To later re-enable Sync without the old bookmarks returning, the user must first
  **Reset Sync** (`chrome://settings/syncSetup` → clear & reset) to wipe the server copy,
  then turn Sync back on so the clean local set pushes up.

**What does NOT work here (verified):** loading an unpacked extension to call
`chrome.bookmarks` API (Gotcha #2), `pkill`-ing Chrome then editing (Gotcha #3), and
editing `Preferences` to flip sync flags.

### Gotcha #2 — Unpacked extensions cannot be loaded in this sandbox
Auto-loading an extension via `--load-extension`, `Playwright`, `open --args`, or even
manual `chrome://extensions` (the `/tmp` path is hidden from the file picker; moving to
Desktop still failed) all failed: macOS TCC blocks AppleScript/remote-debug control, the
sandbox silently drops the flag, and `Preferences` showed 0 installed extensions. Do not
rely on an extension-based approach in a constrained environment — go through the file
directly (Gotcha #1 path).

### Gotcha #3 — Never force-kill Chrome
`pkill -x "Google Chrome"` / `kill -9` skips the normal shutdown that serializes session
state. This **destroys unsaved local session state** — notably **Tab Groups** (which are
local-only, not synced, and have no standalone on-disk file). Bookmarks survive (they are
written to disk), but Tab Groups vanish. Always close Chrome via normal exit
(`Cmd+Q`, or AppleScript `tell application "Google Chrome" to quit` — though TCC may block
the latter, in which case ask the user to quit manually).

## Bundled Resources

- `scripts/analyze_bookmarks.py` — parse, print tree, detect duplicates, timestamp analysis.
- `scripts/find_dead_bookmarks.py` — match URLs against the dead-domain list.
- `scripts/reorganize_bookmarks.py` — build target dict → emit valid `Bookmarks` JSON.
- `references/dead_domains.md` — curated list of closed/deprecated services to flag.
- `references/chrome_sync_mechanics.md` — deep dive on Sync merge behavior & the working fix.

See `references/chrome_sync_mechanics.md` before attempting Step 5 on a synced profile.
