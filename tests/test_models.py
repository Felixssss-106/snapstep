"""模型层测试：Session/Step 序列化与脱敏。"""

from snapstep.models import Session, Step, TypedRun


def test_step_typed_text_and_secret():
    step = Step(
        typed_runs=[
            TypedRun(text="操作手册", is_secret=False),
            TypedRun(text="••••", is_secret=True),
            TypedRun(text=" 后续", is_secret=False),
        ]
    )
    assert step.typed_text() == "操作手册 后续"
    assert step.has_secret()


def test_rel_position():
    step = Step(click_x=960, click_y=540, monitor_width=1920, monitor_height=1080)
    assert step.rel_x == 0.5
    assert step.rel_y == 0.5


def test_session_roundtrip(tmp_path):
    session = Session()
    session.steps.append(
        Step(
            index=1,
            window_title="记事本",
            click_x=100,
            click_y=200,
            monitor_width=1920,
            monitor_height=1080,
            typed_runs=[TypedRun(text="hello")],
        )
    )
    session.save(tmp_path)
    loaded = Session.load(tmp_path)
    assert loaded.steps[0].window_title == "记事本"
    assert loaded.steps[0].typed_runs[0].text == "hello"
    assert loaded.steps[0].rel_x == 100 / 1920
