# SnapStep 发布执行手册

目标：v0.1.0 发布后 2 周内拿到第一波 star 与真实用户反馈。
打法沿用 deep-research-cn 验证过的五渠道节奏，先国内后国际。

## 0. 发布前置清单

- [ ] **录 30s 演示 GIF**（最重要的一项，README 的转化率全靠它）：
  1. Win+G 或用 ScreenToGif 录制
  2. 脚本：托盘点「开始录制」→ 打开一个真实软件（如 微信设置/浏览器书签整理）做 5~6 步操作（含一次输入）→ 停止 → 展示生成的 HTML 教程滚动浏览
  3. 导出 GIF，压缩到 < 8MB（gifski / ezgif），存为 `docs/demo.gif`，替换 README 中的 TODO 注释
- [ ] 用 GitHub Actions 打的 exe 本机实测：安装、录制、导出、设置四件事
- [ ] `pytest` 与 `ruff check` 全绿
- [ ] 确认 `pyproject.toml` 的 Homepage/Issues URL 正确
- [ ] 准备 3~5 张截图备用（设置界面、HTML 成品、Markdown 成品）

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
