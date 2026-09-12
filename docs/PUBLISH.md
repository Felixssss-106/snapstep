# SnapStep 发布执行手册

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

## 2. 五渠道文案

### V2EX（分享创造节点，首选，发完 1h 内自己顶一次评论补 GIF）

> 标题：SnapStep：按一次快捷键，把操作过程变成图文教程（开源）
>
> 做内部文档/给同事写操作手册时，截图-编号-写步骤太费时间。
> SnapStep 常驻托盘，按 Ctrl+Alt+S 开始，正常操作，再按一次停止，
> 自动得到带序号标注截图的 Markdown/HTML/Word 教程。
> 可选接 GLM/DeepSeek/OpenAI 把文案写得更自然，不接也能用（本地模板）。
> 全程本机处理，密码框输入自动隐藏，MIT 开源。
> GitHub：链接 → 求 star / 求反馈，Windows 优先，macOS 在路线图。

### 即刻（原文转贴 + 一张 GIF，带上 #开源# #效率工具# 话题）

### Reddit（英文）

- r/SideProject、r/selfhosted、r/opensource：
> I built an open-source Scribe alternative: press a hotkey, do your work,
> press again — get a step-by-step guide with auto-annotated screenshots.
> Runs 100% locally on Windows, exports MD/HTML/DOCX, optional AI polish
> via any OpenAI-compatible API. MIT, no telemetry.

### X / Twitter（GIF + 一句话 + GitHub 链接，可同时发中文推）

### Hacker News（Show HN，等 GIF 和对比表都满意后再发）

> Show HN: SnapStep – Open-source Scribe alternative, records clicks into guides

## 3. Awesome 列表 PR（发布后第 2~3 天）

- awesome-windows、awesome-python（Applications 分类）
- awesome-selfhosted（强调本地处理）
- 中文圈：HelloGitHub 投稿（hellogithub.com 提交入口）、GitHubDaily

PR 文案一句话即可：`| [SnapStep](link) | Record screen actions into step-by-step guides with annotated screenshots |`

## 4. 发布后跟进

- 前 48h 每条 issue 2h 内回复（冷启动期的响应速度决定口碑）
- 记录各渠道带来的 star/issue 数，第二次发布（v0.2）前复盘
- 收集 3 个真实用户案例（哪个软件的操作教程）后，把截图放进 README「用户案例」区
