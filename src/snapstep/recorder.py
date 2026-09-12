"""录制引擎：全局输入钩子（pynput）+ 事件聚合（纯逻辑，可单测）。"""

from __future__ import annotations

import ctypes
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from .config import Config, sessions_dir
from .models import Session, Step, TypedRun

# 键入停顿超过该秒数后，把已输入内容结算为一个 TypedRun
TYPING_FLUSH_SECONDS = 1.5


def active_window_title() -> str:
    """当前前台窗口标题（仅 Windows；失败返回空串）。"""
    if sys.platform != "win32":
        return ""
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except Exception:
        return ""


class EventAggregator:
    """把点击/键入事件整理成有序的 Step 列表。线程安全，不依赖输入钩子。"""

    def __init__(self) -> None:
        self.session = Session(created_at=datetime.now().isoformat(timespec="seconds"))
        self._current: Step | None = None
        self._lock = threading.Lock()

    def begin_step(
        self,
        *,
        click_x: int,
        click_y: int,
        monitor: dict,
        window_title: str = "",
    ) -> Step:
        with self._lock:
            step = Step(
                index=len(self.session.steps) + 1,
                created_at=datetime.now().isoformat(timespec="seconds"),
                window_title=window_title,
                click_x=click_x,
                click_y=click_y,
                monitor_left=monitor.get("left", 0),
                monitor_top=monitor.get("top", 0),
                monitor_width=monitor.get("width", 0),
                monitor_height=monitor.get("height", 0),
            )
            self.session.steps.append(step)
            self._current = step
            return step

    def append_text(self, text: str, is_secret: bool = False) -> None:
        if not text:
            return
        with self._lock:
            step = self._current
            if step is None:
                # 尚未有点击就开始打字：仍值得记一步
                step = Step(
                    index=len(self.session.steps) + 1,
                    created_at=datetime.now().isoformat(timespec="seconds"),
                )
                self.session.steps.append(step)
                self._current = step
            runs = step.typed_runs
            if runs and runs[-1].is_secret == is_secret:
                runs[-1].text += text
            else:
                runs.append(TypedRun(text=text, is_secret=is_secret))

    def attach_screenshot(self, step: Step, rel_path: str) -> None:
        with self._lock:
            step.screenshot = rel_path


class Recorder:
    """组合 pynput 全局钩子、延迟截屏与隐私检测，产出 Session。

    用法：
        recorder = Recorder(config)
        recorder.start()
        ...  # 用户操作
        session, session_dir = recorder.stop_and_save()
    """

    def __init__(self, config: Config, out_dir: Path | None = None) -> None:
        self.config = config
        self.agg = EventAggregator()
        self.session_dir = out_dir or (
            sessions_dir() / datetime.now().strftime("%Y%m%d-%H%M%S")
        )
        self.on_step_captured = None  # 可选回调：step -> None（GUI/CLI 提示用）

        self._keyboard_listener = None
        self._mouse_listener = None
        self._typing = ""  # 当前明文缓冲
        self._secret_len = 0  # 当前密码缓冲字符数
        self._run_is_secret = False  # 当前键入段是否始于密码框
        self._modifiers: set[str] = set()
        self._flush_timer: threading.Timer | None = None
        self._lock = threading.Lock()
        self._stopped = threading.Event()

    # ---------- 生命周期 ----------

    def start(self) -> None:
        from pynput import keyboard, mouse

        self.session_dir.mkdir(parents=True, exist_ok=True)
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press, on_release=self._on_key_release
        )
        self._mouse_listener = mouse.Listener(on_click=self._on_click)
        self._keyboard_listener.start()
        self._mouse_listener.start()

    def stop_and_save(self) -> tuple[Session, Path]:
        if not self._stopped.is_set():
            self._stopped.set()
            self._flush_typing()
            self._cancel_flush_timer()
            for listener in (self._keyboard_listener, self._mouse_listener):
                if listener is not None:
                    listener.stop()
            # 给在途的延迟截屏线程一点时间落盘（最多 delay_ms + 0.3s）
            time.sleep(self.config.capture.delay_ms / 1000 + 0.3)
            self.agg.session.save(self.session_dir)
        return self.agg.session, self.session_dir

    # ---------- 鼠标 ----------

    def _on_click(self, x: int, y: int, button, pressed: bool) -> None:
        from pynput import mouse

        if not pressed or button != mouse.Button.left:
            return
        self._flush_typing()
        step = self.agg.begin_step(
            click_x=x,
            click_y=y,
            monitor={},  # 稍后由截屏线程补全
            window_title=active_window_title(),
        )
        if self.on_step_captured:
            try:
                self.on_step_captured(step)
            except Exception:
                pass
        if self.config.privacy.privacy_mode:
            return
        threading.Thread(
            target=self._delayed_capture, args=(step, x, y), daemon=True
        ).start()

    def _delayed_capture(self, step: Step, x: int, y: int) -> None:
        from .capture import ScreenCapture, save_screenshot

        time.sleep(max(self.config.capture.delay_ms, 0) / 1000)
        try:
            capture = ScreenCapture()
            img, monitor = capture.capture_point(x, y)
            # 截屏线程里补全显示器边界（begin_step 时拿不到 mss monitors）
            step.monitor_left = monitor.get("left", 0)
            step.monitor_top = monitor.get("top", 0)
            step.monitor_width = monitor.get("width", 0)
            step.monitor_height = monitor.get("height", 0)
            rel = save_screenshot(
                img,
                self.session_dir,
                step.index,
                self.config.capture.image_format,
            )
            self.agg.attach_screenshot(step, rel)
        except Exception:
            # 截屏失败不致命：该步退化为纯文字步骤
            pass

    # ---------- 键盘 ----------

    def _on_key_press(self, key) -> None:
        from pynput import keyboard

        name = self._modifier_name(key)
        if name:
            self._modifiers.add(name)
            return
        if key in (keyboard.Key.enter, keyboard.Key.tab):
            self._flush_typing()
            return
        if key == keyboard.Key.backspace:
            with self._lock:
                if self._run_is_secret:
                    self._secret_len = max(0, self._secret_len - 1)
                else:
                    self._typing = self._typing[:-1]
            return
        char = getattr(key, "char", None)
        if not char:
            return
        if {"ctrl", "alt"} & self._modifiers:
            return  # 快捷键（Ctrl+C 等）不当作输入内容
        with self._lock:
            if not self._typing and not self._run_is_secret and self._secret_len == 0:
                # 键入段起点：判断是否密码框
                from .privacy import focused_control_is_password

                self._run_is_secret = (
                    self.config.privacy.mask_passwords and focused_control_is_password()
                )
            if self._run_is_secret:
                self._secret_len += 1
            else:
                self._typing += char
        self._arm_flush_timer()

    def _on_key_release(self, key) -> None:
        name = self._modifier_name(key)
        if name:
            self._modifiers.discard(name)

    @staticmethod
    def _modifier_name(key) -> str | None:
        from pynput import keyboard

        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.ctrl):
            return "ctrl"
        if key in (keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt):
            return "alt"
        return None

    # ---------- 键入段结算 ----------

    def _arm_flush_timer(self) -> None:
        self._cancel_flush_timer()
        timer = threading.Timer(TYPING_FLUSH_SECONDS, self._flush_typing)
        timer.daemon = True
        timer.start()
        self._flush_timer = timer

    def _cancel_flush_timer(self) -> None:
        if self._flush_timer is not None:
            self._flush_timer.cancel()
            self._flush_timer = None

    def _flush_typing(self) -> None:
        self._cancel_flush_timer()
        with self._lock:
            if self._run_is_secret:
                text = "•" * self._secret_len
                secret = True
            else:
                text = self._typing
                secret = False
            self._typing = ""
            self._secret_len = 0
            self._run_is_secret = False
        if text:
            self.agg.append_text(text, is_secret=secret)
