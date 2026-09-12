"""HTML 导出：Jinja2 模板 + base64 内嵌，产出可分享的单文件教程页。"""

from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .. import __version__
from ..models import Session

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "resources" / "templates"


def _template() -> Environment:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(("html",)),
    )
    return env


def export_html(
    session: Session,
    images: dict[int, Path],
    out_dir: Path,
    embed_images: bool = True,
) -> Path:
    steps = []
    for step in session.steps:
        img_path = images.get(step.index)
        image_src = None
        if img_path is not None:
            if embed_images:
                encoded = base64.b64encode(img_path.read_bytes()).decode("ascii")
                image_src = f"data:image/png;base64,{encoded}"
            else:
                image_src = (Path("images") / img_path.name).as_posix()
        steps.append(
            {
                "index": step.index,
                "title": step.title or f"步骤 {step.index}",
                "description": step.description,
                "typed": step.typed_text(),
                "image": image_src,
            }
        )

    html = _template().get_template("report.html.j2").render(
        title=session.title or "操作教程",
        intro=session.intro or "",
        generated=f"{datetime.now():%Y-%m-%d %H:%M} · SnapStep v{__version__}",
        steps=steps,
    )
    path = out_dir / "guide.html"
    path.write_text(html, encoding="utf-8")
    return path
