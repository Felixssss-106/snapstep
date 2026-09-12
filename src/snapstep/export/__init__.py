"""导出器包：Markdown / HTML / Word + 标注图准备。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from ..models import Session

FORMATS = ("md", "html", "docx")


def prepare_images(
    session: Session, session_dir: Path, out_dir: Path
) -> dict[int, Path]:
    """为每一步生成带点击高亮和序号徽章的标注图。

    返回 {step.index: 标注图路径}；没有截图或原始文件缺失的步骤跳过。
    """
    from ..capture import annotate

    images_dir = out_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    mapping: dict[int, Path] = {}
    for step in session.steps:
        if not step.screenshot:
            continue
        raw = session_dir / step.screenshot
        if not raw.exists():
            continue
        img = Image.open(raw)
        annotated = annotate(img, step.rel_x, step.rel_y, step.index)
        path = images_dir / f"step-{step.index:02d}.png"
        annotated.save(path)
        mapping[step.index] = path
    return mapping


def export_session(
    session: Session,
    session_dir: Path,
    fmt: str,
    out_dir: Path | None = None,
    embed_images: bool = True,
) -> list[Path]:
    """把 Session 导出为指定格式（fmt=all 时导出全部三种）。"""
    from .docx_export import export_docx
    from .html_export import export_html
    from .markdown_export import export_markdown

    out_dir = out_dir or session_dir / "export"
    out_dir.mkdir(parents=True, exist_ok=True)
    fmts = list(FORMATS) if fmt == "all" else [fmt]
    unknown = set(fmts) - set(FORMATS)
    if unknown:
        raise ValueError(f"未知导出格式：{'、'.join(sorted(unknown))}（支持 {FORMATS}）")

    images = prepare_images(session, session_dir, out_dir)
    results: list[Path] = []
    for f in fmts:
        if f == "md":
            results.append(export_markdown(session, images, out_dir))
        elif f == "html":
            results.append(export_html(session, images, out_dir, embed_images))
        elif f == "docx":
            results.append(export_docx(session, images, out_dir))
    return results
