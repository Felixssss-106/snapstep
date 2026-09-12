"""v0.2 自适应截屏：选片与无效点击过滤的逻辑测试。"""

from PIL import Image

from snapstep.capture import mean_diff, save_screenshot
from snapstep.config import Config
from snapstep.models import Step, TypedRun
from snapstep.recorder import Recorder


def _img(color, mark=False):
    img = Image.new("RGB", (400, 300), color)
    if mark:
        for x in range(0, 400, 20):
            for y in range(0, 300, 20):
                img.putpixel((x, y), (255, 255, 255))
    return img


def test_mean_diff_same_and_different(tmp_path):
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    _img((40, 40, 40)).save(a)
    _img((40, 40, 40)).save(b)
    assert mean_diff(a, b) < 0.5  # 相同画面 ≈ 0
    _img((220, 220, 220), mark=True).save(b)
    assert mean_diff(a, b) > 10  # 明显不同的画面


def _recorder(tmp_path):
    return Recorder(Config(), out_dir=tmp_path)


def test_finalize_selects_settled_when_immediate_is_stale(tmp_path):
    """立即帧与上一步几乎相同、稳定帧明显不同 → 选稳定帧（慢加载场景）。"""
    rec = _recorder(tmp_path)
    prev = save_screenshot(_img((40, 40, 40)), tmp_path, 1)
    imm = save_screenshot(_img((40, 40, 40)), tmp_path, 2, suffix="-imm")
    settled = save_screenshot(_img((230, 230, 230)), tmp_path, 2, suffix="-set")
    rec.agg.session.steps = [
        Step(index=1, screenshot=prev),
        Step(index=2, cand_immediate=imm, cand_settled=settled),
    ]
    rec.finalize_session()
    assert rec.agg.session.steps[1].screenshot == settled


def test_finalize_renumbers_after_filter(tmp_path):
    """无键入且画面无变化的点击被剔除，剩余步骤重新编号。"""
    rec = _recorder(tmp_path)
    blank = save_screenshot(_img((40, 40, 40)), tmp_path, 0)
    changed = save_screenshot(_img((220, 220, 220), mark=True), tmp_path, 0)
    rec.agg.session.steps = [
        Step(index=1, screenshot=blank),
        Step(index=2, screenshot=blank),  # 无变化且无输入 → 剔除
        Step(index=3, screenshot=changed, typed_runs=[TypedRun(text="输入内容")]),
        Step(index=4, screenshot=changed),  # 与上一步相同 → 剔除
    ]
    rec.finalize_session()
    kept = rec.agg.session.steps
    assert [s.index for s in kept] == [1, 2]
    assert kept[1].typed_text() == "输入内容"


def test_filter_disabled_keeps_all(tmp_path):
    rec = _recorder(tmp_path)
    rec.config.capture.filter_idle_clicks = False
    same = save_screenshot(_img((40, 40, 40)), tmp_path, 0)
    rec.agg.session.steps = [
        Step(index=1, screenshot=same),
        Step(index=2, screenshot=same),
    ]
    rec.finalize_session()
    assert len(rec.agg.session.steps) == 2


def test_privacy_mode_idle_filter_by_window(tmp_path):
    """隐私模式无截图：同窗口且无键入的连续点击被剔除。"""
    rec = _recorder(tmp_path)
    rec.agg.session.steps = [
        Step(index=1, window_title="记事本"),
        Step(index=2, window_title="记事本"),  # 无变化无输入 → 剔除
        Step(index=3, window_title="浏览器"),  # 窗口变了 → 保留
    ]
    rec.finalize_session()
    kept = rec.agg.session.steps
    assert [s.index for s in kept] == [1, 2]  # 保留两步并重新编号
    assert kept[-1].window_title == "浏览器"


def test_first_step_never_filtered(tmp_path):
    rec = _recorder(tmp_path)
    same = save_screenshot(_img((40, 40, 40)), tmp_path, 0)
    rec.agg.session.steps = [Step(index=1, screenshot=same)]
    rec.finalize_session()
    assert len(rec.agg.session.steps) == 1
