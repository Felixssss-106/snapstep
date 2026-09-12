# Changelog

所有显著变更记录在本文件。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.2.2] - 2026-09-12

### Added

- **自定义导出目录**：设置里可指定导出目录（支持「浏览…」选择与 ~ 路径），
  录制/导出默认落到 `<导出目录>/SnapStep-<时间戳>/`，多次导出互不覆盖；
  CLI `export --out` 显式指定仍然优先

## [0.2.1] - 2026-09-12

### Fixed

- `snapstep demo` 默认输出目录改为 `~/snapstep-demo`：此前是相对当前目录的
  `snapstep-demo`，在 `C:\WINDOWS\system32` 等只读目录里运行会直接 PermissionError

## [0.2.0] - 2026-09-12

### Fixed

- **托盘菜单 QAction 被 GC 回收**：无 parent 的 QAction 在初始化返回后被回收，
  菜单实际只剩「开始录制」，用户无法打开设置/导出/退出。已为全部 QAction 挂载 parent
- 设置对话框按钮改为中文「保存 / 取消」

### Added

- **自适应截屏（双帧选片）**：每次点击拍两帧——立即帧（点击瞬间的界面，
  秒关的对话框不再漏拍）+ 稳定帧（轮询画面直至停止变化，上限可在设置调，
  慢加载页面不再截到半成品）；停止时自动选片：立即帧没有新信息而稳定帧
  有明显变化时（典型：点击后等页面加载）自动改用稳定帧
- **自动过滤无效点击**：停止录制时比对相邻步骤画面，无变化且无键入的点击
  自动剔除并重新编号（设置中可关）
- **热键三重加固**：程序单实例锁（防双开导致热键开/停互相抵消）；
  快捷键改用 Win32 RegisterHotKey 原生注册（pynput GlobalHotKeys 兜底）；
  开始/停止托盘气泡反馈 + `~/.snapstep/snapstep.log` 运行日志
- 设置界面：截屏延迟改为「界面稳定等待上限」+「自动过滤无效点击」开关

## [0.1.0] - 2026-09-12

首个公开版本。

### Added

- 全局快捷键录制（托盘 GUI + CLI `record`），左键点击自动成为步骤
- 点击自动截屏，导出时叠加高亮圈与序号徽章；键入文本自动归入步骤
- 隐私模式（不截屏）与密码框输入隐藏（UI Automation 尽力检测）
- 教程文案双路生成：OpenAI 兼容 API（GLM/DeepSeek/OpenAI/本地模型预设）+ 零配置本地模板兜底
- 导出 Markdown / 单文件 HTML（base64 内嵌截图）/ Word
- `snapstep demo` 一键生成示例教程，验证安装
- GitHub Actions：测试（3.10/3.14）+ Windows exe 自动发布
