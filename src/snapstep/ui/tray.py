"""系统托盘 + 全局快捷键 + 录制悬浮提示。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RESOURCES = Path(__file__).resolve().parents[1] / "resources"

DEFAULT_HOTKEY = "<ctrl>+<alt>+s"

# pynput 修饰键白名单：热键串只能由这些修饰键 + 单字符/F 键组成
_MODIFIER_TOKENS = {
    "ctrl", "ctrl_l", "ctrl_r",
    "alt", "alt_l", "alt_r", "alt_gr",
    "shift", "shift_l", "shift_r",
    "cmd", "cmd_l", "cmd_r",
    "option", "option_l", "option_r",
}
_FUNCTION_KEY_RE = re.compile(r"^f([1-9]|1[0-9]|2[0-4])$")


def validate_hotkey(spec: str) -> bool:
    """校验 pynput GlobalHotKeys 热键串（如 <ctrl>+<alt>+s）。

    配置文件里的字符串不可信：先白名单校验，再交给 pynput 解析。
    """
    if not isinstance(spec, str) or not spec:
        return False
    parts = spec.split("+")
    if len(parts) < 2:
        return False
    *modifiers, key = parts
    for mod in modifiers:
        if not (mod.startswith("<") and mod.endswith(">")):
            return False
        if mod[1:-1] not in _MODIFIER_TOKENS:
            return False
    if key.startswith("<") and key.endswith(">"):
        inner = key[1:-1].lower()
        return inner in _MODIFIER_TOKENS or _FUNCTION_KEY_RE.fullmatch(inner) is not None
    return len(key) == 1 and key.isalnum()


def safe_hotkey(spec: str) -> str:
    return spec if validate_hotkey(spec) else DEFAULT_HOTKEY


def set_dpi_awareness() -> None:
    """声明 per-monitor DPI 感知，保证 pynput 物理像素与截屏一致（仅 Windows）。

    参数为固定常量，不引入任何外部输入。
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            import ctypes

            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def _tray_icon_path(recording: bool) -> str:
    name = "icon_rec.png" if recording else "icon.png"
    return str(RESOURCES / name)


class Overlay:
    """录制中的右上角悬浮提示（点击穿透）。"""

    def __init__(self) -> None:
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont
        from PySide6.QtWidgets import QLabel, QWidget

        self._widget = QWidget()
        self._widget.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowTransparentForInput
        )
        self._widget.setAttribute(Qt.WA_TranslucentBackground)
        label = QLabel("● 录制中", self._widget)
        label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        label.setStyleSheet(
            "color:#fff; background:#f53f3f; border-radius:12px; padding:6px 14px;"
        )
        self._widget.adjustSize()

    def show(self) -> None:
        from PySide6.QtGui import QGuiApplication

        self._widget.adjustSize()
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self._widget.move(screen.right() - self._widget.width() - 24, screen.top() + 24)
        self._widget.show()

    def hide(self) -> None:
        self._widget.hide()


class TrayApp:
    def __init__(self) -> None:
        from PySide6.QtGui import QAction, QIcon
        from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

        from ..config import load_config

        self.app = QApplication.instance() or QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName("SnapStep")

        self.config = load_config()
        self.recorder = None
        self.last_session_dir: Path | None = None
        self._hotkey = None  # pynput GlobalHotKeys 实例
        self.overlay = Overlay()

        self.tray = QSystemTrayIcon(QIcon(_tray_icon_path(False)))
        self.menu = QMenu()
        self.action_toggle = QAction("开始录制")
        self.action_toggle.triggered.connect(self.toggle)
        action_folder = QAction("打开会话文件夹")
        action_folder.triggered.connect(self._open_sessions_dir)
        action_export = QAction("导出上次会话")
        action_export.triggered.connect(self._export_last)
        action_settings = QAction("设置…")
        action_settings.triggered.connect(self._open_settings)
        action_quit = QAction("退出")
        action_quit.triggered.connect(self._quit)

        for item in (
            self.action_toggle,
            None,
            action_folder,
            action_export,
            None,
            action_settings,
            None,
            action_quit,
        ):
            if item is None:
                self.menu.addSeparator()
            else:
                self.menu.addAction(item)

        self.tray.setContextMenu(self.menu)
        self.tray.setToolTip("SnapStep — 录屏生成图文教程")
        self.tray.show()
        self._start_hotkey()
        self.tray.showMessage(
            "SnapStep 已启动",
            f"按 {self.config.hotkey} 或点击托盘图标开始录制",
            QSystemTrayIcon.Information,
            4000,
        )

    # ---------- 录制 ----------

    def toggle(self) -> None:
        if self.recorder is None:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self) -> None:
        from ..config import load_config
        from ..recorder import Recorder

        self.config = load_config()
        self.recorder = Recorder(self.config)
        self.recorder.on_step_captured = self._on_step
        self.recorder.start()
        self.action_toggle.setText("停止录制")
        self.tray.setToolTip("SnapStep — 录制中")
        self.overlay.show()

    def _stop_recording(self) -> None:
        if self.recorder is None:
            return
        from PySide6.QtGui import QIcon
        from PySide6.QtWidgets import QSystemTrayIcon

        session, session_dir = self.recorder.stop_and_save()
        self.recorder = None
        self.last_session_dir = session_dir
        self.action_toggle.setText("开始录制")
        self.tray.setIcon(QIcon(_tray_icon_path(False)))
        self.tray.setToolTip("SnapStep — 录屏生成图文教程")
        self.overlay.hide()
        try:
            from ..cli import generate_and_export

            used, paths = generate_and_export(session, session_dir, self.config)
            note = "AI 文案" if used == "ai" else "本地模板"
            self.tray.showMessage(
                "教程已生成",
                f"{len(session.steps)} 步 · {note} · {paths[0].name}",
                QSystemTrayIcon.Information,
                5000,
            )
        except Exception as exc:  # 导出失败也不丢会话
            self.tray.showMessage(
                "导出失败",
                f"{exc}\n会话已保存在 {session_dir}",
                QSystemTrayIcon.Critical,
                8000,
            )

    def _on_step(self, step) -> None:
        self.tray.setToolTip(f"SnapStep — 已捕获 {step.index} 步")

    # ---------- 快捷键 ----------

    def _start_hotkey(self) -> None:
        """启动全局快捷键监听（独立线程，可 stop 后重建）。"""
        try:
            from pynput import keyboard
        except Exception:
            return  # 快捷键不可用时仅托盘菜单可用

        combo = safe_hotkey(self.config.hotkey)
        old = self._hotkey
        if old is not None:
            old.stop()
        self._hotkey = keyboard.GlobalHotKeys({combo: self._hotkey_fired})
        self._hotkey.daemon = True
        self._hotkey.start()

    def _hotkey_fired(self) -> None:
        # pynput 线程里触发，转回 Qt 主线程执行
        from PySide6.QtCore import QTimer

        QTimer.singleShot(0, self.toggle)

    # ---------- 菜单动作 ----------

    def _open_sessions_dir(self) -> None:
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices

        from ..config import sessions_dir

        sessions_dir().mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(sessions_dir())))

    def _find_last_session(self) -> Path | None:
        if self.last_session_dir is not None:
            return self.last_session_dir
        from ..config import sessions_dir

        candidates = sorted(sessions_dir().glob("*/session.json"))
        return candidates[-1].parent if candidates else None

    def _export_last(self) -> None:
        from PySide6.QtWidgets import QSystemTrayIcon

        target = self._find_last_session()
        if target is None:
            self.tray.showMessage("SnapStep", "还没有可导出的会话", QSystemTrayIcon.Warning, 4000)
            return
        from ..cli import generate_and_export
        from ..models import Session

        session = Session.load(target)
        used, paths = generate_and_export(session, target, self.config)
        note = "AI 文案" if used == "ai" else "本地模板"
        self.tray.showMessage(
            "导出完成",
            f"{note} · " + "、".join(p.name for p in paths),
            QSystemTrayIcon.Information,
            5000,
        )

    def _open_settings(self) -> None:
        from PySide6.QtWidgets import QSystemTrayIcon

        if self.recorder is not None:
            self.tray.showMessage(
                "SnapStep", "录制中，请先停止再修改设置", QSystemTrayIcon.Warning, 4000
            )
            return
        from ..config import load_config
        from .settings import SettingsDialog

        dialog = SettingsDialog()
        if dialog.run():
            self.config = load_config()
            self._start_hotkey()

    def _quit(self) -> None:
        if self.recorder is not None:
            self.recorder.stop_and_save()
        if self._hotkey is not None:
            self._hotkey.stop()
        self.app.quit()


def run_gui() -> int:
    set_dpi_awareness()
    from PySide6.QtWidgets import QApplication

    QApplication(sys.argv)
    TrayApp()
    return QApplication.instance().exec()
