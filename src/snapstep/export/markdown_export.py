"""Markdown 导出。"""

from __future__ import annotations

import os
from pathlib import Path

from ..models import Session


def _inline_code(text: str) -> str:
    return f"`{text.replace('`', chr(39))}`"


def export_markdown(
    session: Session, images: dict[int, Path], out_dir: Path
) -> Path:
    lines = [f"# {session.title or '操作教程'}", ""]
    if session.intro:
        lines += [session.intro, ""]
    for step in session.steps:
        lines += [f"## {step.index}. {step.title or f'步骤 {step.index}'}", ""]
        if step.description:
            lines += [step.description, ""]
        typed = step.typed_text()
        if typed:
            lines += [f"输入：{_inline_code(typed)}", ""]
        img = images.get(step.index)
        if img:
            rel = Path(os.path.relpath(img, out_dir)).as_posix()
            lines += [f"![步骤 {step.index} 截图]({rel})", ""]
    path = out_dir / "guide.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
