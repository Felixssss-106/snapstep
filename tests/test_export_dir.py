"""自定义导出目录：解析规则与端到端导出落点。"""

from pathlib import Path

from snapstep.cli import (
    _build_demo_session,
    _render_demo_screenshots,
    generate_and_export,
    resolve_export_dir,
)
from snapstep.config import Config
from snapstep.models import Session


def test_resolve_default(tmp_path):
    session = Session(created_at="2026-09-12T10:34:20")
    cfg = Config()  # dir 为空
    assert (
        resolve_export_dir(cfg, tmp_path, session) == tmp_path / "export"
    )


def test_resolve_custom_absolute(tmp_path):
    session = Session(created_at="2026-09-12T10:34:20")
    cfg = Config()
    cfg.export.dir = str(tmp_path / "outbox")
    target = resolve_export_dir(cfg, tmp_path, session)
    assert target == tmp_path / "outbox" / "SnapStep-20260912-103420"


def test_resolve_relative_based_on_home(tmp_path):
    session = Session(created_at="2026-09-12T10:34:20")
    cfg = Config()
    cfg.export.dir = "docs/tutorials"
    target = resolve_export_dir(cfg, tmp_path, session)
    assert target == Path.home() / "docs" / "tutorials" / "SnapStep-20260912-103420"


def test_explicit_wins_over_config(tmp_path):
    session = Session(created_at="2026-09-12T10:34:20")
    cfg = Config()
    cfg.export.dir = str(tmp_path / "outbox")
    assert (
        resolve_export_dir(cfg, tmp_path, session, explicit=tmp_path / "x")
        == tmp_path / "x"
    )


def test_generate_and_export_uses_custom_dir(tmp_path):
    session = _build_demo_session()
    session.created_at = "2026-09-12T10:34:20"
    session_dir = tmp_path / "sess"
    _render_demo_screenshots(session, session_dir)
    cfg = Config()
    cfg.export.dir = str(tmp_path / "outbox")

    used, paths = generate_and_export(session, session_dir, cfg, fmt="md")

    assert used in ("ai", "template")
    target = tmp_path / "outbox" / "SnapStep-20260912-103420"
    assert (target / "guide.md").exists()
    for p in paths:
        assert str(p).startswith(str(target))
