# Chrome Bookmark Organizer

把一团乱的 Chrome 书签整理干净，并**让它真的保持住**——而不是重启浏览器后被同步还原。

> Repo: 一个可直接复用的「书签整理」技能（Skill），含分析脚本、失效检测、安全重写流程，以及踩坑雷区文档。

## 为什么需要它

直接改 `Bookmarks` 文件、或者用扩展调 `chrome.bookmarks` API，在真实环境里几乎都会失败：

- **Chrome 同步是云端主导的**：你本地删干净了，一重启，云端那 547 个旧书签又被合并回来，数量直接翻倍（实测 547 → 923）。
- **沙盒里根本加载不了扩展**：`--load-extension` 被静默丢弃、AppleScript 被 macOS TCC 拦截、`chrome://extensions` 加载也失败。
- **`pkill` 强杀 Chrome 会丢掉标签页分组（Tab Groups）**：书签没事，但会话状态没了，且无法从磁盘恢复。

这个技能把这些坑都标出来了，并给出**唯一验证可行**的清理路径。

## 它能做什么

1. 解析 `Bookmarks` JSON，打印书签树、重复项、从未使用/超老书签。
2. 对照「已关闭/停更服务」清单，列出建议删除的失效书签（**只列出、不删除**，需你确认）。
3. 把目标分类结构安全序列化成一份新的、合法的 `Bookmarks` JSON。
4. 在**同步确实关闭**的前提下写入并清缓存，让整理结果持久生效。
5. 导出 HTML 备份，随时可再导入。

最终结果示例：547 → 414 个，顶层 6 个常用（Google / Gmail / YouTube / 百度 / 翻译 / Figma）+ 7 个分类文件夹（AI工具 / 作品集 / 设计素材 / 设计灵感 / 设计规范 / 工作项目 / 个人常用）。

## 快速开始

```bash
# 1. 分析当前书签（树 + 重复 + 陈旧）
python3 scripts/analyze_bookmarks.py --tree

# 2. 列出失效/可删书签（仅供参考，不会删除）
python3 scripts/find_dead_bookmarks.py

# 3. 编写目标结构 target.json，然后生成干净 Bookmarks
python3 scripts/reorganize_bookmarks.py --target target.json --output Bookmarks --backup

# 4. 写入前务必先读 references/chrome_sync_mechanics.md，确认同步已关
```

## 关键雷区（务必先读）

| # | 坑 | 为什么失败 | 正确做法 |
|---|----|-----------|---------|
| 1 | 改本地文件对抗云端同步 | 重启被云端旧数据合并，数量翻倍 | 确认 `consented_to_sync / sync.requested / bookmarks` 全为 false 再写 |
| 2 | 用扩展调 `chrome.bookmarks` | 沙盒/web 加载不了未打包扩展 | 直接走文件（坑1 的路径） |
| 3 | `pkill` / `kill -9` 强杀 Chrome | 跳过正常关闭，Tab Groups 等会话状态丢失且不可恢复 | 正常退出（Cmd+Q），不要强杀 |

详见 [`references/chrome_sync_mechanics.md`](references/chrome_sync_mechanics.md)。

## 目录结构

```
chrome-bookmark-organizer/
├── SKILL.md                       # 技能主文档（触发条件、流程、雷区）
├── README.md                      # 本文件
├── scripts/
│   ├── analyze_bookmarks.py       # 解析 / 树 / 重复 / 时间戳分析
│   ├── find_dead_bookmarks.py     # 失效域名匹配（不删除）
│   └── reorganize_bookmarks.py    # 目标结构 -> 合法 Bookmarks JSON
└── references/
    ├── chrome_sync_mechanics.md   # 同步合并机制与可行修复
    └── dead_domains.md            # 已关闭/停更服务清单
```

## License

MIT — 拿去用，改了记得分享。
