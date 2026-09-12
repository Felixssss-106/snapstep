"""设置窗口。"""

from __future__ import annotations

from ..config import API_PRESETS, Config, load_config, save_config


class SettingsDialog:
    """QDialog 表单。用法：

        dialog = SettingsDialog()
        if dialog.run():  # 返回 True 表示已保存
            ...
    """

    def __init__(self, parent=None) -> None:
        from PySide6.QtWidgets import (
            QCheckBox,
            QComboBox,
            QDialog,
            QDialogButtonBox,
            QFormLayout,
            QGroupBox,
            QLineEdit,
            QSpinBox,
            QVBoxLayout,
        )

        self.cfg: Config = load_config()
        self.hotkey_changed = False
        self._preset_names = list(API_PRESETS)

        dialog = QDialog(parent)
        dialog.setWindowTitle("SnapStep 设置")
        dialog.setMinimumWidth(460)
        root = QVBoxLayout(dialog)

        # ---- 录制 ----
        box_record = QGroupBox("录制")
        form_record = QFormLayout(box_record)
        self.edit_hotkey = QLineEdit(self.cfg.hotkey)
        self.edit_hotkey.setPlaceholderText("<ctrl>+<alt>+s")
        form_record.addRow("全局快捷键", self.edit_hotkey)
        self.spin_delay = QSpinBox()
        self.spin_delay.setRange(0, 2000)
        self.spin_delay.setSuffix(" ms")
        self.spin_delay.setValue(self.cfg.capture.delay_ms)
        self.spin_delay.setToolTip("点击后等待片刻再截屏，让弹窗/菜单先弹出来")
        form_record.addRow("截屏延迟", self.spin_delay)
        self.check_privacy = QCheckBox("隐私模式（完全不截屏，只记录步骤）")
        self.check_privacy.setChecked(self.cfg.privacy.privacy_mode)
        form_record.addRow(self.check_privacy)
        self.check_mask = QCheckBox("密码框输入自动隐藏（尽力检测）")
        self.check_mask.setChecked(self.cfg.privacy.mask_passwords)
        form_record.addRow(self.check_mask)
        root.addWidget(box_record)

        # ---- AI 文案 ----
        box_ai = QGroupBox("AI 文案（OpenAI 兼容接口，留空则使用本地模板）")
        form_ai = QFormLayout(box_ai)
        self.combo_preset = QComboBox()
        self.combo_preset.addItems(self._preset_names)
        form_ai.addRow("预设", self.combo_preset)
        self.edit_base_url = QLineEdit(self.cfg.api.base_url)
        self.edit_base_url.setPlaceholderText("https://open.bigmodel.cn/api/paas/v4")
        form_ai.addRow("Base URL", self.edit_base_url)
        self.edit_model = QLineEdit(self.cfg.api.model)
        self.edit_model.setPlaceholderText("glm-4-flash / deepseek-chat / gpt-4o-mini")
        form_ai.addRow("模型", self.edit_model)
        self.edit_key = QLineEdit(self.cfg.api.api_key)
        self.edit_key.setEchoMode(QLineEdit.Password)
        form_ai.addRow("API Key", self.edit_key)
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["zh", "en"])
        self.combo_lang.setCurrentText(self.cfg.api.language)
        form_ai.addRow("文案语言", self.combo_lang)
        root.addWidget(box_ai)

        # ---- 导出 ----
        box_export = QGroupBox("导出")
        form_export = QFormLayout(box_export)
        self.combo_format = QComboBox()
        self.combo_format.addItems(["html", "md", "docx"])
        self.combo_format.setCurrentText(self.cfg.export.format)
        form_export.addRow("默认格式", self.combo_format)
        self.check_embed = QCheckBox("HTML 内嵌截图（单文件，方便分享）")
        self.check_embed.setChecked(self.cfg.export.embed_images)
        form_export.addRow(self.check_embed)
        root.addWidget(box_export)


        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        root.addWidget(buttons)

        # 预设切换 → 填充 base_url / model（用户改过就不覆盖）
        self._initial = (self.edit_base_url.text(), self.edit_model.text())
        self.combo_preset.currentTextChanged.connect(self._apply_preset)

        self._dialog = dialog

    def _apply_preset(self, name: str) -> None:
        preset = API_PRESETS.get(name)
        if not preset:
            return
        if (self.edit_base_url.text(), self.edit_model.text()) != self._initial:
            return
        self.edit_base_url.setText(preset["base_url"])
        self.edit_model.setText(preset["model"])

    def run(self) -> bool:
        """打开对话框；返回 True 表示用户保存了设置。"""
        if self._dialog.exec() != self._dialog.Accepted:
            return False
        from .tray import safe_hotkey

        new_hotkey = safe_hotkey(self.edit_hotkey.text().strip())
        self.hotkey_changed = new_hotkey != self.cfg.hotkey
        self.cfg.hotkey = new_hotkey
        self.cfg.capture.delay_ms = self.spin_delay.value()
        self.cfg.privacy.privacy_mode = self.check_privacy.isChecked()
        self.cfg.privacy.mask_passwords = self.check_mask.isChecked()
        self.cfg.api.base_url = self.edit_base_url.text().strip()
        self.cfg.api.model = self.edit_model.text().strip()
        self.cfg.api.api_key = self.edit_key.text().strip()
        self.cfg.api.language = self.combo_lang.currentText()
        self.cfg.export.format = self.combo_format.currentText()
        self.cfg.export.embed_images = self.check_embed.isChecked()
        save_config(self.cfg)
        return True
