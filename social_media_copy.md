# 社交媒体文案 · Chrome 书签整理复盘

> 配图建议：整理前后书签栏对比截图 / 那张「547 → 923」翻车的截图最有冲击力

---

## 版本一 · 小红书（种草 + 踩坑向，带 emoji）

**标题：我把 547 个 Chrome 书签整理成 414 个，踩了 3 个坑才成功 😭**

书签栏乱成狗了好几年，终于下定决心整理。结果……比我想象中难 10 倍。

❌ 坑 1：我辛辛苦苦删到 381 个，重启浏览器——变 923 个了？？
因为 Chrome 同步是「云端主导」的，你本地删了没用，云端那堆旧书签一合并，直接翻倍。改 Preferences 关同步也没用，Chrome 一开又给你恢复了。

❌ 坑 2：想用扩展调 chrome.bookmarks API 来批量改。
结果沙盒环境里根本加载不了未打包扩展，命令行参数被静默忽略，连 AppleScript 都被系统拦了。

❌ 坑 3：图省事 pkill 强杀 Chrome。
书签没事，但我辛苦分好的「标签页分组」全没了，而且永久不可恢复 😇

✅ 唯一真管用的路：
确认同步真的关了（三个开关全 false）→ 正常退出 Chrome → 备份 → 写入干净书签 → 清同步缓存 → 再开。

最后 547 → 414，顶层钉了 6 个常用的（Google/Gmail/YouTube/百度/翻译/Figma），下面 7 个分类文件夹。清爽。

我把整套流程 + 脚本 + 踩坑文档整理成 skill 开源了，需要的自取 👇
#Chrome #书签整理 #效率工具 #AI工具

---

## 版本二 · 微博（短文案 + 话题）

折腾一晚上，把 Chrome 书签从 547 个整理到 414 个。最大的教训：Chrome 同步是云端主导的，你本地删了重启就被旧数据合并回去（实测 547→923）。改配置文件关同步、用扩展 API、pkill 强杀——三条路全翻车。唯一靠谱的是先确认同步真关了再写文件。已把完整流程和防坑脚本开源。#Chrome书签整理 #效率折腾

---

## 版本三 · 朋友圈 / 公众号（叙事向）

**关于「整理书签」这件小事，我前后翻车了三次。**

第一次，我直接改本地 Bookmarks 文件，删到 381 个，重启——923 个。后来才懂：Chrome 同步以云端为准，本地改动会被旧数据合并覆盖。

第二次，我改用「正统」做法：写个扩展调 chrome.bookmarks API 批量整理。结果沙盒里扩展根本加载不上，命令行参数被忽略，连系统自动化都被拦。

第三次，我图快 pkill 强杀浏览器，书签保住了，但标签页分组（Tab Groups）没了，且无法恢复。

真正生效的方案只有一条：确认同步彻底关闭 → 正常退出 → 备份 → 写文件 → 清缓存 → 重启。

书签栏从一堆散乱链接，变成了「6 个常用钉在最前 + 7 个分类文件夹」。顺手把整套路数打包成开源技能，含分析、失效检测、安全重写脚本和一份《同步机制避坑指南》。

如果你也受困于乱糟糟的书签栏，这套可以直接拿去用。

---

## 版本四 · GitHub Release Notes / Repo 描述

A reusable skill to clean and reorganize Chrome bookmarks — and make the result *stick* (no more reverting on restart because of Chrome Sync).

Includes analysis scripts, a dead-bookmark detector, a safe rewrite workflow, and hard-won notes on the three gotchas that break naive approaches:
1. Chrome Sync is cloud-led → local edits get merged/reverted.
2. Unpacked extensions can't load in a sandboxed/macOS env.
3. Force-killing Chrome (`pkill`/`kill -9`) destroys Tab Groups (unsaved session state).

547 → 414 bookmarks, zero data loss. MIT licensed.
