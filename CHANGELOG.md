# Changelog

所有显著变更记录在本文件。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

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
