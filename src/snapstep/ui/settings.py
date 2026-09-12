"""设置窗口。"""

from __future__ import annotations

from pathlib import Path

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
            QFormLayout,
            QGroupBox,
            QHBoxLayout,
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
        self.spin_settle = QSpinBox()
        self.spin_settle.setRange(0, 5000)
        self.spin_settle.setSuffix(" ms")
        self.spin_settle.setValue(self.cfg.capture.settle_max_ms)
        self.spin_settle.setToolTip(
            "点击后持续比对画面，界面停止变化即取「稳定帧」；这里是等待上限。\n"
            "加载慢的界面调大，操作快的场景调小。"
        )
        form_record.addRow("界面稳定等待上限", self.spin_settle)
        self.check_privacy = QCheckBox("隐私模式（完全不截屏，只记录步骤）")
        self.check_privacy.setChecked(self.cfg.privacy.privacy_mode)
        form_record.addRow(self.check_privacy)
        self.check_mask = QCheckBox("密码框输入自动隐藏（尽力检测）")
        self.check_mask.setChecked(self.cfg.privacy.mask_passwords)
        form_record.addRow(self.check_mask)
        self.check_filter = QCheckBox("自动过滤无变化的无效点击")
        self.check_filter.setChecked(self.cfg.capture.filter_idle_clicks)
        self.check_filter.setToolTip(
            "停止录制时比对相邻步骤的画面，没点出任何变化且没有输入的点击会被剔除"
        )
        form_record.addRow(self.check_filter)
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
        self.edit_export_dir = QLineEdit(self.cfg.export.dir)
        self.edit_export_dir.setPlaceholderText("默认：<会话目录>\\export")
        from PySide6.QtWidgets import QPushButton

        row_dir = QHBoxLayout()
        row_dir.addWidget(self.edit_export_dir)
        btn_browse = QPushButton("浏览…")
        btn_browse.clicked.connect(self._browse_export_dir)
        row_dir.addWidget(btn_browse)
        form_export.addRow("导出目录", row_dir)
        self.check_embed = QCheckBox("HTML 内嵌截图（单文件，方便分享）")
        self.check_embed.setChecked(self.cfg.export.embed_images)
        form_export.addRow(self.check_embed)
        root.addWidget(box_export)


        from PySide6.QtWidgets import QPushButton

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        btn_save = QPushButton("保存")
        btn_save.setDefault(True)
        btn_save.clicked.connect(dialog.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(dialog.reject)
        buttons.addWidget(btn_save)
        buttons.addWidget(btn_cancel)
        root.addLayout(buttons)

        # 预设切换 → 填充 base_url / model（用户改过就不覆盖）
        self._initial = (self.edit_base_url.text(), self.edit_model.text())
        self.combo_preset.currentTextChanged.connect(self._apply_preset)

        self._dialog = dialog

    def _browse_export_dir(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        chosen = QFileDialog.getExistingDirectory(
            self._dialog, "选择导出目录", self.edit_export_dir.text() or str(Path.home())
        )
        if chosen:
            self.edit_export_dir.setText(chosen)

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
        self.cfg.capture.settle_max_ms = self.spin_settle.value()
        self.cfg.capture.filter_idle_clicks = self.check_filter.isChecked()
        self.cfg.privacy.privacy_mode = self.check_privacy.isChecked()
        self.cfg.privacy.mask_passwords = self.check_mask.isChecked()
        self.cfg.api.base_url = self.edit_base_url.text().strip()
        self.cfg.api.model = self.edit_model.text().strip()
        self.cfg.api.api_key = self.edit_key.text().strip()
        self.cfg.api.language = self.combo_lang.currentText()
        self.cfg.export.format = self.combo_format.currentText()
        self.cfg.export.embed_images = self.check_embed.isChecked()
        self.cfg.export.dir = self.edit_export_dir.text().strip()
        save_config(self.cfg)
        return True
