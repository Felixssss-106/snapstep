"""文案生成器与端点校验测试。"""

import pytest

from snapstep.models import Session, Step, TypedRun
from snapstep.writer import (
    AIWriter,
    TemplateWriter,
    WriterError,
    apply_copy,
    validate_endpoint,
)


def _demo_session() -> Session:
    session = Session()
    session.steps.append(
        Step(
            index=1,
            window_title="后台管理",
            click_x=960,
            click_y=130,
            monitor_width=1920,
            monitor_height=1080,
            typed_runs=[TypedRun(text="标题文字")],
        )
    )
    session.steps.append(
        Step(
            index=2,
            window_title="后台管理",
            click_x=400,
            click_y=600,
            monitor_width=1920,
            monitor_height=1080,
            typed_runs=[TypedRun(text="••••", is_secret=True)],
        )
    )
    return session


# ---------- TemplateWriter ----------

def test_template_writer_zh():
    session = _demo_session()
    apply_copy(session, TemplateWriter("zh"), None)
    assert session.title and "操作教程" in session.title
    assert "后台管理" in session.title
    assert len(session.steps) == 2
    assert "点击" in session.steps[0].description
    assert "标题文字" in session.steps[0].description
    assert "密码" in session.steps[1].description


def test_template_writer_en():
    session = _demo_session()
    TemplateWriter("en").write(session)
    assert "Guide" in session.title


def test_template_writer_respects_existing_copy():
    session = _demo_session()
    session.steps[0].title = "自定义标题"
    TemplateWriter("zh").write(session)
    assert session.steps[0].title == "自定义标题"


# ---------- AIWriter：JSON 解析与端点校验 ----------

def test_parse_json_plain_and_fenced():
    data = {"title": "t", "steps": []}
    assert AIWriter._parse_json('{"title": "t", "steps": []}') == data
    assert AIWriter._parse_json('```json\n{"title": "t", "steps": []}\n```') == data
    assert AIWriter._parse_json('前置说明 {"title": "t", "steps": []} 后缀') == data


def test_parse_json_rejects_garbage():
    with pytest.raises(WriterError):
        AIWriter._parse_json("完全不是 JSON")
    with pytest.raises(WriterError):
        AIWriter._parse_json("[1, 2, 3]")


def test_validate_endpoint_blocks_metadata_and_bad_scheme():
    with pytest.raises(WriterError):
        validate_endpoint("ftp://example.com/v1")
    with pytest.raises(WriterError):
        validate_endpoint("http://169.254.169.254/latest/meta-data")
    with pytest.raises(WriterError):
        validate_endpoint("not a url")


def test_validate_endpoint_allows_public_and_loopback():
    validate_endpoint("https://api.deepseek.com/v1")
    validate_endpoint("http://127.0.0.1:11434/v1")  # Ollama
    validate_endpoint("http://localhost:1234/v1")  # LM Studio


def test_ai_writer_overlays_copy_on_success(monkeypatch):
    session = _demo_session()
    writer = AIWriter("https://api.example.com/v1", "sk-test", "demo-model")

    def fake_chat(self, message):  # noqa: ARG001
        return (
            '{"title": "发布文章指南", "intro": "两步发布",'
            ' "steps": [{"title": "填写标题", "description": "在后台输入文章标题"},'
            ' {"title": "提交", "description": "点击提交按钮"}]}'
        )

    monkeypatch.setattr(AIWriter, "_chat", fake_chat)
    used = apply_copy(session, TemplateWriter("zh"), writer)
    assert used == "ai"
    assert session.title == "发布文章指南"
    assert session.steps[0].title == "填写标题"


def test_ai_writer_failure_falls_back_to_template(monkeypatch):
    session = _demo_session()
    writer = AIWriter("https://api.example.com/v1", "sk-test", "demo-model")

    def fake_chat(self, message):  # noqa: ARG001
        raise WriterError("boom")

    monkeypatch.setattr(AIWriter, "_chat", fake_chat)
    used = apply_copy(session, TemplateWriter("zh"), writer)
    assert used == "template"
    assert session.title and session.steps[0].title
