"""导出器与 demo 流程冒烟测试。"""

from snapstep.cli import _build_demo_session, _render_demo_screenshots
from snapstep.export import export_session
from snapstep.writer import TemplateWriter, apply_copy


def _prepare(tmp_path):
    session = _build_demo_session()
    _render_demo_screenshots(session, tmp_path)
    apply_copy(session, TemplateWriter("zh"), None)
    return session


def test_export_all_formats(tmp_path):
    session = _prepare(tmp_path)
    paths = export_session(session, tmp_path, "all", tmp_path / "export")
    names = {p.name for p in paths}
    assert names == {"guide.md", "guide.html", "guide.docx"}
    for p in paths:
        assert p.exists() and p.stat().st_size > 500


def test_markdown_contains_steps_and_images(tmp_path):
    session = _prepare(tmp_path)
    (path,) = export_session(session, tmp_path, "md", tmp_path / "export")
    text = path.read_text(encoding="utf-8")
    assert session.title in text
    assert "images/step-01.png" in text
    assert text.count("## ") == 3


def test_html_embeds_base64_images(tmp_path):
    session = _prepare(tmp_path)
    (path,) = export_session(session, tmp_path, "html", tmp_path / "export", embed_images=True)
    html = path.read_text(encoding="utf-8")
    assert "data:image/png;base64," in html
    assert html.count('class="step"') == 3


def test_html_without_embed_uses_relative_paths(tmp_path):
    session = _prepare(tmp_path)
    (path,) = export_session(session, tmp_path, "html", tmp_path / "export", embed_images=False)
    html = path.read_text(encoding="utf-8")
    assert "data:image" not in html
    assert "images/step-01.png" in html


def test_annotate_draws_badge(tmp_path):
    """截图里应出现红色高亮（点击标注）——验证 annotate 真正落笔。"""
    from PIL import Image

    session = _prepare(tmp_path)
    paths = export_session(session, tmp_path, "md", tmp_path / "export")
    img = Image.open(tmp_path / "export" / "images" / "step-01.png")
    reds = sum(
        1
        for px in img.getdata()
        if px[0] > 200 and px[1] < 120 and px[2] < 120
    )
    assert reds > 50, paths
