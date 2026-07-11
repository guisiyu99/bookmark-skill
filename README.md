# Chrome Bookmark Organizer / Chrome 书签整理

一套用于**整理你自己当前错乱的 Chrome 书签**的本地工作流与工具包——不是一份拿来
分享或导入的现成书签合集。仓库里装的是**方法 + 脚本 + 踩坑文档**，不含任何人的
真实书签数据。

A local workflow + toolkit for **cleaning up your own messy Chrome bookmarks** —
not a pre-made bookmark collection to share or import. The repo ships the
**method + scripts + hard-won notes**, not anyone's actual bookmark data.

> Repo: 一个可直接复用的「书签整理」技能（Skill），含分析脚本、失效检测、安全重写
> 流程，以及踩坑雷区文档。
> Repo: a reusable bookmark-cleanup Skill with analysis scripts, a dead-link
> detector, a Sync-safe rewrite flow, and gotcha docs.

## 为什么需要它 / Why you need it

直接改 `Bookmarks` 文件、或者用扩展调 `chrome.bookmarks` API，在真实环境里几乎都会失败：

**EN** — Editing the file naively fails because of three real-world traps:
- **Chrome Sync is cloud-led**: you clean locally, relaunch, and the old cloud
  bookmarks merge back in (real case: 547 → 923).
- **Sandboxes can't load unpacked extensions**: `--load-extension` is silently
  dropped, AppleScript is blocked by macOS TCC, manual load fails too.
- **`pkill`-ing Chrome destroys Tab Groups**: bookmarks survive, but unsaved
  session state (Tab Groups) is gone and unrecoverable.

**中文** — 朴素做法翻车，是因为有三个真实雷区：
- **Chrome 同步是云端主导的**：你本地删干净了，一重启，云端旧书签又合并回来
  （真实案例：547 → 923）。
- **沙盒里根本加载不了扩展**：`--load-extension` 被静默丢弃、AppleScript 被 macOS
  TCC 拦截、手动加载也失败。
- **`pkill` 强杀 Chrome 会丢掉标签页分组**：书签没事，但会话状态没了且不可恢复。

这个技能把坑都标出来了，并给出**唯一验证可行**的清理路径。
This skill documents those traps and gives the one verified-working cleanup path.

## 它能做什么 / What it does

1. 解析 `Bookmarks` JSON，打印书签树、重复项、从未使用/超老书签。
   Parse the Bookmarks JSON; print the tree, duplicates, never-used / very-old items.
2. 对照「已关闭/停更服务」清单，列出建议删除的失效书签（**只列出、不删除**，需你确认）。
   List dead bookmarks against a curated closed/deprecated list (**lists only, never
   deletes** — you confirm).
3. 把目标分类结构安全序列化成一份新的、合法的 `Bookmarks` JSON。
   Safely serialize a target taxonomy into a fresh, valid Bookmarks JSON.
4. 在**同步确实关闭**的前提下写入并清缓存，让整理结果持久生效。
   Write and clear cache only once Sync is confirmed OFF, so the result sticks.
5. 导出 HTML 备份，随时可再导入。
   Export an HTML backup you can re-import anywhere.

> 示例成果（真实案例，非标准答案）：547 → 414 个，顶层 6 个常用
> （Google / Gmail / YouTube / 百度 / 翻译 / Figma）+ 7 个分类文件夹
> （AI工具 / 作品集 / 设计素材 / 设计灵感 / 设计规范 / 工作项目 / 个人常用）。
> Example outcome (a real case, not a prescription): 547 → 414, with 6 pinned
> bookmarks + 7 category folders. Your numbers and structure will differ.

## 快速开始 / Quick start

```bash
# 1. 分析当前书签（树 + 重复 + 陈旧）
# 1. Analyze current bookmarks (tree + dupes + stale)
python3 scripts/analyze_bookmarks.py --tree

# 2. 列出失效/可删书签（仅供参考，不会删除）
# 2. List dead/deletable bookmarks (review only, no deletion)
python3 scripts/find_dead_bookmarks.py

# 3. 编写目标结构 target.json，然后生成干净 Bookmarks
# 3. Write a target.json, then generate a clean Bookmarks file
python3 scripts/reorganize_bookmarks.py --target target.json --output Bookmarks --backup

# 4. 写入前务必先读 references/chrome_sync_mechanics.md，确认同步已关
# 4. Before writing, read references/chrome_sync_mechanics.md and confirm Sync is OFF
```

## 关键雷区（务必先读）/ Critical gotchas (read first)

| # | 坑 / Trap | 为什么失败 / Why it fails | 正确做法 / Fix |
|---|----|-----------|---------|
| 1 | 改本地文件对抗云端同步 / Edit file vs cloud Sync | 重启被云端旧数据合并，数量翻倍 / Relaunch merges old cloud data, count doubles | 确认三个开关全 false 再写 / Confirm 3 switches false, then write |
| 2 | 用扩展调 `chrome.bookmarks` / Use extension API | 沙盒/web 加载不了未打包扩展 / Sandbox can't load unpacked ext | 直接走文件（坑1 路径）/ Go via file (Gotcha #1) |
| 3 | `pkill` / `kill -9` 强杀 Chrome / Force-kill Chrome | 跳过正常关闭，Tab Groups 等会话状态丢失且不可恢复 / Skips shutdown, Tab Groups lost | 正常退出（Cmd+Q），不要强杀 / Quit normally (Cmd+Q) |

详见 [`references/chrome_sync_mechanics.md`](references/chrome_sync_mechanics.md)。
See [`references/chrome_sync_mechanics.md`](references/chrome_sync_mechanics.md).

## 目录结构 / Structure

```
chrome-bookmark-organizer/
├── SKILL.md                       # 技能主文档（触发条件/流程/雷区，中英双语）
│                                    # Skill doc (triggers / workflow / gotchas, bilingual)
├── README.md                      # 本文件 / This file
├── scripts/
│   ├── analyze_bookmarks.py       # 解析 / 树 / 重复 / 时间戳分析
│   ├── find_dead_bookmarks.py     # 失效域名匹配（不删除）
│   └── reorganize_bookmarks.py    # 目标结构 -> 合法 Bookmarks JSON
└── references/
    ├── chrome_sync_mechanics.md   # 同步合并机制与可行修复
    └── dead_domains.md            # 已关闭/停更服务清单
```

## License

MIT — 拿去用，改了记得分享。 / MIT — use it, and share your improvements.
