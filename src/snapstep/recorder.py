"""录制引擎：全局输入钩子（pynput）+ 事件聚合（纯逻辑，可单测）。"""

from __future__ import annotations

import ctypes
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from .capture import mean_diff
from .config import Config, sessions_dir
from .log import log_error, log_info
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
    """组合 pynput 全局钩子、双帧截屏（立即+稳定）与隐私检测，产出 Session。

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
        self._capture_threads: list[threading.Thread] = []

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
            # 等在途的截屏线程落地（立即帧很快；稳定帧最多 settle_max_ms + 轮询间隔）
            budget = self.config.capture.settle_max_ms / 1000 + 1.0
            for thread in self._capture_threads:
                thread.join(timeout=max(budget, 0.5))
            self._capture_threads.clear()
            self.finalize_session()
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
            monitor={},
            window_title=active_window_title(),
        )
        if self.on_step_captured:
            try:
                self.on_step_captured(step)
            except Exception:
                pass
        if self.config.privacy.privacy_mode:
            return
        thread = threading.Thread(
            target=self._capture_candidates, args=(step, x, y), daemon=True
        )
        self._capture_threads.append(thread)
        thread.start()

    def _capture_candidates(self, step: Step, x: int, y: int) -> None:
        """为一步截取两帧候选：立即帧 + 稳定帧（最终选用哪帧在 finalize 时决定）。"""
        from .capture import ScreenCapture, save_screenshot, settle_grab

        try:
            capture = ScreenCapture()
            time.sleep(0.06)  # 让点击的按压反馈先画出来
            img, monitor = capture.capture_point(x, y)
            self._apply_monitor(step, monitor)
            step.cand_immediate = save_screenshot(
                img, self.session_dir, step.index, self.config.capture.image_format, "-imm"
            )
            settled, waited = settle_grab(
                capture,
                monitor,
                max_wait_ms=self.config.capture.settle_max_ms,
            )
            log_info(
                f"step {step.index}: settled after {waited}ms"
                f" (max {self.config.capture.settle_max_ms}ms)"
            )
            step.cand_settled = save_screenshot(
                settled, self.session_dir, step.index, self.config.capture.image_format, "-set"
            )
        except Exception as exc:
            log_error(f"step {step.index} capture failed: {exc}")
            # 截屏失败不致命：该步退化为纯文字步骤

    @staticmethod
    def _apply_monitor(step: Step, monitor: dict) -> None:
        step.monitor_left = monitor.get("left", 0)
        step.monitor_top = monitor.get("top", 0)
        step.monitor_width = monitor.get("width", 0)
        step.monitor_height = monitor.get("height", 0)

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

    # ---------- 收尾：选片 + 过滤无效点击 + 重编号 ----------

    # 平均像素差阈值：与上一步画面差异 < 2.0 视为「没有新信息」
    IDLE_DIFF_THRESHOLD = 2.0
    # 立即帧与稳定帧差异 > 4.0 视为「点击带来了明显的新状态」
    CHANGE_DIFF_THRESHOLD = 4.0

    def finalize_session(self) -> Session:
        """停止后统一处理：为每步选帧、剔除无效点击、重新编号。

        选帧规则：默认用立即帧（用户点击时看到的界面，Scribe 语义）；
        但若立即帧与上一步选中的画面几乎相同、而稳定帧明显不同
        （典型：点了链接等慢页面加载），说明新信息在稳定帧里，改用稳定帧。
        """

        session = self.agg.session
        kept: list[Step] = []
        prev_image: str | None = None
        for step in session.steps:
            step.screenshot = self._select_frame(step, prev_image)
            if kept and self._is_idle_click(step, kept[-1]):
                log_info(f"step {step.index}: dropped as idle click")
                continue
            kept.append(step)
            if step.screenshot:
                prev_image = step.screenshot
        for i, step in enumerate(kept, 1):
            step.index = i
        session.steps = kept
        return session

    def _select_frame(self, step: Step, prev_image: str | None) -> str | None:
        a, b = step.cand_immediate, step.cand_settled
        if a is None and b is None:
            # 旧会话或隐私模式：保持已有选片，绝不能覆盖成 None
            return step.screenshot
        if a is None:
            return b
        if b is None:
            return a
        if prev_image is not None:
            try:

                prev = self.session_dir / prev_image
                if prev.exists():
                    diff_prev_a = mean_diff(prev, self.session_dir / a)
                    diff_a_b = mean_diff(
                        self.session_dir / a, self.session_dir / b
                    )
                    if (
                        diff_prev_a < self.IDLE_DIFF_THRESHOLD
                        and diff_a_b > self.CHANGE_DIFF_THRESHOLD
                    ):
                        return b
            except Exception as exc:
                log_error(f"step {step.index} frame select failed: {exc}")
        return a

    def _is_idle_click(self, step: Step, prev: Step) -> bool:
        """无效点击判定：本步无键入、无密码输入，且画面与上一步基本相同。"""
        if not self.config.capture.filter_idle_clicks:
            return False
        if step.typed_runs:
            return False
        if step.screenshot and prev.screenshot:
            try:

                return (
                    mean_diff(
                        self.session_dir / prev.screenshot,
                        self.session_dir / step.screenshot,
                    )
                    < self.IDLE_DIFF_THRESHOLD
                )
            except Exception:
                return False
        if not step.screenshot and not prev.screenshot:
            # 隐私模式下没有图像可比：窗口相同且没有任何输入视为无效
            return step.window_title == prev.window_title
        return False
