# SnapStep 发布执行手册

> **发布状态：v0.1.0 已于 2026-09-12 正式发布** ✅
> 仓库：https://github.com/Felixssss-106/snapstep · Release（含 exe）：https://github.com/Felixssss-106/snapstep/releases/tag/v0.1.0
> CI：Test（3.10/3.14）与 Build（Windows exe）均绿。以下第 0/1 节已执行完毕，第 2~4 节（渠道推广）待发。

目标：v0.1.0 发布后 2 周内拿到第一波 star 与真实用户反馈。
打法沿用 deep-research-cn 验证过的五渠道节奏，先国内后国际。

## 0. 发布前置清单

- [x] **录 30s 演示 GIF**（2026-09-12 已完成，`docs/demo.gif`，1080px/10fps/1.7MB；
  重录思路：ffmpeg ddagrab 抓屏 + `snapstep record` 子进程 + pynput 驱动真实操作 + Chrome `--app` 模式展示成品）
- [x] `pytest` 与 `ruff check` 全绿（27 passed / All checks passed，2026-09-12）
- [x] 确认 `pyproject.toml` 的 Homepage/Issues URL 正确（全部指向 Felixssss-106/snapstep，与发布命令一致）
- [x] 备用截图：`docs/screenshots/` 下已有 guide-html.png（首屏）、guide-html-full.png（整页）、guide-md.png（Markdown 源码）
- [x] **exe 本机交互实测**（2026-09-12 全部通过，本地构建=CI 同 spec）：
  启动/托盘 ✓；托盘菜单 开始录制→记事本操作→停止录制→自动导出 HTML→气泡通知 ✓；
  设置对话框打开与中文按钮 ✓；托盘退出 ✓。
  实测中抓到并修复：QAction 未挂 parent 被 GC 回收导致菜单只剩第一项（已修复）；
  注意本机 pynput 构建的 GlobalHotKeys 忽略 injected 事件，自动化注入测不了热键，
  人工按 `Ctrl+Alt+S` 即可（物理键盘不受影响）
- [x] 备用截图：`docs/screenshots/` 下 settings.png（设置界面实机）、guide-html.png（首屏）、
  guide-html-full.png（整页）、guide-md.png（Markdown 源码）
- [ ] **安装 gh CLI**（本机未装）：`winget install GitHub.cli` 然后 `gh auth login`

## 1. 发布动作（顺序执行）

```bash
# 首次发布
cd D:\ZCodeProject\snapstep
git init && git add -A && git commit -m "feat: SnapStep v0.1.0 — 录屏自动生成图文教程"
gh repo create Felixssss-106/snapstep --public --source . --push
gh workflow run build.yml            # 或直接打 tag 触发
git tag v0.1.0 && git push origin v0.1.0   # 触发 Build workflow → exe 自动挂到 Release
```

Release notes 直接粘贴 CHANGELOG 的 0.1.0 段落 + demo GIF。

## 2. 五渠道文案（定稿，照抄即发）

> 通用素材：`docs/demo.gif`（1.7MB，Reddit/即刻直接上传原生托管）、`docs/screenshots/guide-html.png`、`settings.png`。
> 顺序建议：V2EX → 即刻（同日或隔日）→ Reddit 三连（间隔 1~2 天）→ X → Show HN。
> 美国向渠道（Reddit/X/HN）最佳时间：**北京时间 21:00~24:00**（美国早间），周末更佳。
> 每个渠道标题/开头必须不同，避免反 spam；发帖 1 小时内自己补一条评论。

### 2.1 V2EX（中文 · 分享创造节点，首选）

标题：

```
SnapStep：按一次快捷键，把屏幕操作变成图文教程（开源）
```

正文：

```
各位好，分享一个刚开源的小工具 SnapStep（MIT）。

场景：给同事写操作手册、给家人写软件教程、给自己留 SOP——传统流程是
「截图 → 编号 → 粘进文档 → 写步骤」，一篇 10 步的教程起码半小时。
SnapStep 把它压缩成：按快捷键 → 正常操作 → 再按一次。

- 常驻托盘，Ctrl+Alt+S 随时开始/停止
- 每次左键点击自动成为一步：延迟截屏（等菜单/弹窗先弹出来），导出时自动叠加
  点击高亮圈和步骤序号；键入的文字自动归进步骤
- 停止后自动导出 Markdown / 单文件 HTML（截图 base64 内嵌，发微信就是成品页）/ Word
- 可选 AI 润色文案：任何 OpenAI 兼容接口都行（GLM / DeepSeek / OpenAI / 本地 Ollama）；
  不配 key 也能用——本地模板兜底，教程永远能生成
- 隐私：全程本机处理、零遥测；密码框输入自动隐藏（UI Automation 尽力检测）；
  隐私模式一键停截屏

30 秒演示 GIF 就在 README 第一屏——那条 GIF 也是这个工具自己录自己生成的。

仓库：https://github.com/Felixssss-106/snapstep
免安装 exe：https://github.com/Felixssss-106/snapstep/releases/tag/v0.1.0（63MB，Win10/11）
Python 3.10+ / PySide6，MIT，欢迎 issue 和 PR。

求 star，更求真实场景反馈：你最想拿它写哪类教程？
```

### 2.2 即刻（中文）

正文（配 `demo.gif` + `guide-html.png` 两张图，带话题 #开源# #效率工具#）：

```
做了个开源小工具 SnapStep 📸

按一次快捷键正常干活，再按一次——刚才的操作自动变成带标注截图的图文教程，
Markdown / 单文件 HTML / Word 三种格式，截图自动加点击高亮圈和步骤编号。

全程本机运行，密码框自动隐藏，零遥测；
可选接 GLM/DeepSeek/OpenAI 润色文案，不接也能用（本地模板兜底）。

开源版 Scribe 平替，MIT，Windows 先行（macOS 在路线图）。
GitHub 搜 Felixssss-106/snapstep，求 star 求反馈 🙏
```

### 2.3 X / Twitter

英文（主帖）：

```
Open-source Scribe alternative 📸

Press a hotkey → do your work → press again.
Get a step-by-step guide with auto-annotated screenshots.
100% local, MIT, exports MD/HTML/DOCX, optional AI polish.

https://github.com/Felixssss-106/snapstep
```

中文（可同日另发一条）：

```
开源小工具 SnapStep：按一次快捷键正常干活，再按一次，
操作自动变成带标注截图的图文教程（Markdown/HTML/Word）。
全程本机、MIT、可选 AI 润色。

https://github.com/Felixssss-106/snapstep
```

### 2.4 Reddit（英文三篇，间隔 1~2 天；r/selfhosted 不发——只收自托管服务器）

**① r/SideProject**（Text 帖 + 原生上传 demo.gif）

Title:

```
I built an open-source Scribe alternative — press a hotkey, do your work, press again, get a step-by-step guide with annotated screenshots (MIT, Windows)
```

Body:

```
Scribe/Tango work great but are paid per seat and everything goes through their cloud. I wanted the same workflow running 100% locally, so I built SnapStep (MIT, Python/Qt).

How it works:
1. Press Ctrl+Alt+S (lives in the system tray)
2. Do your thing — every left click becomes a step: auto screenshot, click position highlighted, typed text captured into the step
3. Press the hotkey again → a polished guide is generated: Markdown, single-file HTML, or Word

Highlights:
- 100% local, zero telemetry. Password fields are masked (best effort) + a privacy mode that skips screenshots entirely
- Optional AI copywriting via any OpenAI-compatible API (GLM / DeepSeek / OpenAI / local Ollama) — but it works with zero config too (local template fallback, the guide always gets generated)
- 30s demo in the README — the GIF was actually recorded by the app itself

Repo (MIT): https://github.com/Felixssss-106/snapstep
Portable exe: https://github.com/Felixssss-106/snapstep/releases/tag/v0.1.0

Windows first, macOS on the roadmap. What would you use it for — onboarding docs, SOPs, tutorials for family?
```

**② r/opensource**（Text 帖，按右侧 flair 选项选一个）

Title:

```
SnapStep — MIT Scribe alternative for Windows (Python/Qt): recorded clicks become step-by-step guides with annotated screenshots
```

Body:

```
Repo: https://github.com/Felixssss-106/snapstep (MIT)

SnapStep records on-screen actions and generates documentation. A global hotkey starts/stops a session; each left click becomes a step (delayed capture so menus/popups settle, click position highlighted with a ring + step number at export), and typed text is attached to the step. Export to Markdown, single-file HTML (base64-embedded images, shareable as one file), or DOCX.

- Copywriting is pluggable: deterministic local template by default, or any OpenAI-compatible endpoint (GLM / DeepSeek / OpenAI / Ollama) for natural text; if the API fails it silently falls back to the template, so a guide is always produced
- Privacy: everything runs locally, no telemetry; password fields masked via UI Automation (best effort); privacy mode disables screenshots entirely; the API endpoint is validated (scheme allowlist, metadata/link-local ranges blocked, redirects rejected) so the key can't be redirected
- Packaging: PyInstaller one-file exe, built automatically by GitHub Actions on every tag; tests run on 3.10/3.14 (27 tests)

Known limitations: Windows first (macOS planned), UI is Chinese-first with English UI on the roadmap (README is bilingual), hotkeys are validated-then-parsed from a config file.

Feedback especially welcome on the HTML export template and the AI prompt design.
```

**③ r/coolgithubprojects**（Link 帖，链接填仓库）

Title:

```
SnapStep – open-source Scribe alternative: record screen actions, get step-by-step guides with annotated screenshots (Python/Qt, MIT)
```

### 2.5 Hacker News（Show HN，最后发）

标题：

```
Show HN: SnapStep – Open-source Scribe alternative, records clicks into guides
```

首评模板（HN 发帖没有正文区，技术细节自己抢首评）：

```
Hi HN! I built SnapStep because writing SOPs and software tutorials by hand
(screenshot → number → paste → describe) was eating hours.

It's a Windows tray app: global hotkey starts recording, every left click
becomes a step with an auto-captured screenshot, typed text is attached,
and stopping produces a Markdown / single-file HTML / Word guide.

Design decisions you might care about:
- Copy generation is pluggable: deterministic local template by default,
  or any OpenAI-compatible API; AI failure degrades to the template
- Screenshots are taken ~350ms after each click so menus settle, and the
  click ring + step number are drawn at export, not at capture
- Password fields are masked via UI Automation (best effort); API endpoints
  are validated (scheme allowlist, metadata ranges blocked, no redirects)

MIT, Python 3.10+, source: https://github.com/Felixssss-106/snapstep
```

### 2.6 渠道受阻备案（2026-09-12 实测）

- **Reddit 帖被站级过滤器删**：给版组发消息求放行——收件人填版块名（如 r/SideProject）：
  `Subject: Post removed by filter — genuine open-source project, requesting approval`
  `Hi mods, my post about SnapStep was auto-removed by the spam filter. It's a MIT-licensed`
  `open-source tool I built myself (repo: https://github.com/Felixssss-106/snapstep), not`
  `commercial promotion. Could you approve it, or let me know if I should repost differently? Thanks!`
  同时：改发 r/coolgithubprojects（几乎不过滤）；新号先在 r/Python 等版评论几天攒 karma；
  发帖间隔拉开 1~2 天。
- **V2EX 注册要邀请码**：只能找有账号的老用户要；拿不到就跳过，改用下面 2.7 的国内无门槛渠道。
- **国内无门槛替代**：
  - 掘金（手机号注册，发文章，标题《我开源了一个工具：按一次快捷键，把屏幕操作自动变成图文教程》，
    正文要点同 §2.1 V2EX 定稿，展开成文章体并配 demo.gif / guide-html.png / settings.png 三图）
  - HelloGitHub：hellogithub.com 登录后「提交项目」，描述一句话：
    `按一次快捷键，把屏幕操作自动变成带标注截图的图文教程`
  - 酷安：手机号注册，用 §2.2 即刻文案，结尾改「酷安的兄弟们帮忙测测 Win11 兼容性」
  - 即刻：手机号注册即可（§2.2）

## 3. Awesome 列表 PR（发布后第 2~3 天）

- awesome-windows、awesome-python（Applications 分类）
- awesome-selfhosted（强调本地处理）
- 中文圈：HelloGitHub 投稿（hellogithub.com 提交入口）、GitHubDaily

PR 文案一句话即可：`| [SnapStep](link) | Record screen actions into step-by-step guides with annotated screenshots |`

## 4. 发布后跟进

- 前 48h 每条 issue 2h 内回复（冷启动期的响应速度决定口碑）
- 记录各渠道带来的 star/issue 数，第二次发布（v0.2）前复盘
- 收集 3 个真实用户案例（哪个软件的操作教程）后，把截图放进 README「用户案例」区
