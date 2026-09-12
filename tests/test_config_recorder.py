"""配置与事件聚合、热键校验测试。"""

import json

from snapstep.config import Config, load_config, save_config
from snapstep.recorder import EventAggregator
from snapstep.ui.tray import DEFAULT_HOTKEY, safe_hotkey, validate_hotkey

# ---------- Config ----------

def test_config_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr("snapstep.config.config_path", lambda: tmp_path / "config.json")
    cfg = Config()
    cfg.api.base_url = "https://example.com/v1"
    cfg.privacy.privacy_mode = True
    save_config(cfg)

    loaded = load_config()
    assert loaded.api.base_url == "https://example.com/v1"
    assert loaded.privacy.privacy_mode is True
    assert loaded.hotkey == cfg.hotkey


def test_config_tolerant_load(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"hotkey": "<ctrl>+<f9>"}), encoding="utf-8")
    monkeypatch.setattr("snapstep.config.config_path", lambda: path)
    cfg = load_config()
    assert cfg.hotkey == "<ctrl>+<f9>"
    assert cfg.capture.delay_ms == 350  # 缺失字段走默认值


# ---------- EventAggregator ----------

def test_aggregator_clicks_and_typing():
    agg = EventAggregator()
    agg.begin_step(
        click_x=500, click_y=300, monitor={"left": 0, "top": 0, "width": 1920, "height": 1080},
        window_title="浏览器",
    )
    agg.append_text("关键词")
    agg.append_text("续写")
    agg.begin_step(click_x=600, click_y=400, monitor={"width": 1920, "height": 1080})
    agg.append_text("密码", is_secret=True)

    steps = agg.session.steps
    assert len(steps) == 2
    assert steps[0].typed_runs[0].text == "关键词续写"
    assert steps[0].window_title == "浏览器"
    assert steps[1].typed_runs[0].is_secret is True


def test_aggregator_typing_before_click_creates_step():
    agg = EventAggregator()
    agg.append_text("前置输入")
    assert len(agg.session.steps) == 1
    assert agg.session.steps[0].typed_text() == "前置输入"


def test_aggregator_secret_switch_creates_new_run():
    agg = EventAggregator()
    agg.begin_step(click_x=0, click_y=0, monitor={"width": 100, "height": 100})
    agg.append_text("user")
    agg.append_text("hunter2", is_secret=True)
    agg.append_text(" done")
    runs = agg.session.steps[0].typed_runs
    assert [r.is_secret for r in runs] == [False, True, False]
    assert runs[1].text == "hunter2"


# ---------- 热键校验 ----------

def test_validate_hotkey_accepts_good():
    assert validate_hotkey("<ctrl>+<alt>+s")
    assert validate_hotkey("<shift>+<f5>")
    assert validate_hotkey("<ctrl>+1")


def test_validate_hotkey_rejects_bad():
    assert not validate_hotkey("<ctrl>+<alt>+eval")
    assert not validate_hotkey("ctrl+s")  # 修饰键缺少尖括号
    assert not validate_hotkey("s")  # 单键无修饰
    assert not validate_hotkey("")
    assert not validate_hotkey("<f9>")  # 缺少修饰键
    assert not validate_hotkey(None)  # type: ignore[arg-type]


def test_safe_hotkey_fallback():
    assert safe_hotkey("<ctrl>+<alt>+q") == "<ctrl>+<alt>+q"
    assert safe_hotkey("import os") == DEFAULT_HOTKEY
