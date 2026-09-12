"""SnapStep 会话数据模型。

一次录制 = 一个 Session，其中每个「点击」开启一个 Step，
点击之后键入的文本归入该 Step（TypedRun）。
数据结构与 session.json 一一对应，可无损往返。
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class TypedRun:
    """一段连续键入的文本。is_secret=True 表示来自密码框，内容已脱敏。"""

    text: str
    is_secret: bool = False


@dataclass
class Step:
    """一个操作步骤：一次左键点击 + 其后紧随的键入。"""

    index: int = 0
    created_at: str = ""
    window_title: str = ""
    # 点击位置：虚拟屏幕绝对像素
    click_x: int = 0
    click_y: int = 0
    # 点击所在显示器的边界（mss 风格），用于导出时按比例标注
    monitor_left: int = 0
    monitor_top: int = 0
    monitor_width: int = 0
    monitor_height: int = 0
    # 截图候选：立即帧（点击瞬间的界面，秒关的对话框也能截到）
    # 与稳定帧（界面停止变化后的界面，慢加载页面等它加载完），
    # 相对 session 目录的路径。screenshot 是最终选用的帧（见 recorder.finalize_session）。
    cand_immediate: str | None = None
    cand_settled: str | None = None
    screenshot: str | None = None
    typed_runs: list[TypedRun] = field(default_factory=list)
    # 由 writer（AI 或模板）生成的文案
    title: str | None = None
    description: str | None = None

    @property
    def rel_x(self) -> float:
        return (self.click_x - self.monitor_left) / max(self.monitor_width, 1)

    @property
    def rel_y(self) -> float:
        return (self.click_y - self.monitor_top) / max(self.monitor_height, 1)

    def typed_text(self) -> str:
        """非密码输入的拼接文本，用于展示与 AI 提示。"""
        return "".join(run.text for run in self.typed_runs if not run.is_secret)

    def has_secret(self) -> bool:
        return any(run.is_secret for run in self.typed_runs)


@dataclass
class Session:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(default_factory=_now)
    title: str | None = None
    intro: str | None = None
    steps: list[Step] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Session:
        steps = []
        for raw in data.get("steps", []):
            runs = [TypedRun(**run) for run in raw.pop("typed_runs", [])]
            steps.append(Step(**raw, typed_runs=runs))
        return cls(
            id=data.get("id", uuid.uuid4().hex[:12]),
            created_at=data.get("created_at", _now()),
            title=data.get("title"),
            intro=data.get("intro"),
            steps=steps,
        )

    def save(self, session_dir: Path) -> Path:
        path = session_dir / "session.json"
        path.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return path

    @classmethod
    def load(cls, session_dir: Path) -> Session:
        path = session_dir / "session.json"
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))
