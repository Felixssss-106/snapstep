"""命令行入口。

    snapstep            启动托盘 GUI（默认）
    snapstep record     命令行录制，回车结束
    snapstep export     导出已有会话
    snapstep config     查看/修改配置
    snapstep demo       生成一份示例教程（无需录制，验证安装）
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import fields as dc_fields
from pathlib import Path

from . import __version__
from .config import Config, load_config, save_config
from .models import Session
from .writer import AIWriter, TemplateWriter, apply_copy


def resolve_export_dir(
    cfg: Config, session_dir: Path, session: Session, explicit: Path | None = None
) -> Path:
    """决定导出目录：显式指定 > 配置项 > 默认 <会话目录>/export。

    配置的自定义目录按会话建子文件夹（SnapStep-<时间戳>），避免多次导出互相覆盖。
    """
    if explicit is not None:
        return explicit
    raw = (cfg.export.dir or "").strip()
    if not raw:
        return session_dir / "export"
    base = Path(raw).expanduser()
    if not base.is_absolute():
        base = Path.home() / base
    ts = session.created_at or ""
    slug = ts[:10].replace("-", "") + "-" + ts[11:19].replace(":", "")
    if not slug.strip("-"):
        slug = session.id
    return base / f"SnapStep-{slug}"


def generate_and_export(
    session: Session,
    session_dir: Path,
    cfg: Config,
    fmt: str | None = None,
    use_ai: bool | None = None,
    out_dir: Path | None = None,
) -> tuple[str, list[Path]]:
    """生成文案并导出。CLI 与 GUI 共用。返回 (writer 名称, 导出文件列表)。"""
    from .export import export_session

    use_ai = cfg.ai_enabled() if use_ai is None else (use_ai and cfg.ai_enabled())
    ai = (
        AIWriter(cfg.api.base_url, cfg.api.api_key, cfg.api.model, cfg.api.language)
        if use_ai
        else None
    )
    used = apply_copy(session, TemplateWriter(cfg.api.language), ai)
    session.save(session_dir)
    target = resolve_export_dir(cfg, session_dir, session, out_dir)
    paths = export_session(
        session,
        session_dir,
        fmt or cfg.export.format,
        target,
        cfg.export.embed_images,
    )
    return used, paths


# ---------- 子命令 ----------


def cmd_record(args, cfg: Config) -> int:
    from .recorder import Recorder

    privacy = "开启" if cfg.privacy.privacy_mode else "关闭"
    ai = "已配置" if cfg.ai_enabled() else "未配置（使用本地模板）"
    print(f"SnapStep v{__version__} 开始录制")
    print(f"  隐私模式：{privacy}（截屏{'被跳过' if cfg.privacy.privacy_mode else '正常'}）")
    print(f"  AI 文案：{ai}")
    print("  进行你的操作，回到本窗口按回车结束录制。\n")

    recorder = Recorder(cfg, out_dir=Path(args.out) if args.out else None)
    recorder.on_step_captured = lambda step: print(
        f"  [步骤 {step.index}] {step.window_title or '未知窗口'}"
    )
    recorder.start()
    try:
        input()
    except KeyboardInterrupt:
        pass
    session, session_dir = recorder.stop_and_save()
    print(f"\n录制完成：{len(session.steps)} 个步骤 → {session_dir}")

    used, paths = generate_and_export(
        session, session_dir, cfg, fmt=args.format, use_ai=not args.no_ai
    )
    _print_export_result(used, paths)
    return 0


def cmd_export(args, cfg: Config) -> int:
    session_dir = Path(args.session_dir)
    if not (session_dir / "session.json").exists():
        print(f"错误：{session_dir} 下没有 session.json", file=sys.stderr)
        return 1
    session = Session.load(session_dir)
    used, paths = generate_and_export(
        session, session_dir, cfg, fmt=args.format, use_ai=not args.no_ai
    )
    _print_export_result(used, paths)
    return 0


def _print_export_result(used: str, paths: list[Path]) -> None:
    if used == "ai":
        print("文案：AI 生成")
    else:
        print("文案：本地模板（AI 未配置或调用失败，已自动兜底）")
    for path in paths:
        print(f"已导出：{path}")


def cmd_config(args, cfg: Config) -> int:
    if args.config_action == "list" or args.key is None:
        print(json.dumps(_config_to_dict(cfg), ensure_ascii=False, indent=2))
        return 0
    if args.config_action == "get":
        print(_get_key(cfg, args.key))
        return 0
    # set
    _set_key(cfg, args.key, args.value)
    save_config(cfg)
    print(f"已保存 {args.key} = {args.value}")
    return 0


def _config_to_dict(cfg: Config) -> dict:
    return {
        "hotkey": cfg.hotkey,
        "capture": {f.name: getattr(cfg.capture, f.name) for f in dc_fields(cfg.capture)},
        "privacy": {f.name: getattr(cfg.privacy, f.name) for f in dc_fields(cfg.privacy)},
        "api": {f.name: getattr(cfg.api, f.name) for f in dc_fields(cfg.api)},
        "export": {f.name: getattr(cfg.export, f.name) for f in dc_fields(cfg.export)},
    }


def _get_key(cfg: Config, key: str) -> object:
    target: object = cfg
    for part in key.split("."):
        target = getattr(target, part)
    return target


def _set_key(cfg: Config, key: str, value: str) -> None:
    parts = key.split(".")
    target: object = cfg
    for part in parts[:-1]:
        target = getattr(target, part)
    leaf = parts[-1]
    if not hasattr(target, leaf):
        valid = _valid_keys(cfg)
        raise SystemExit(f"未知配置项 {key}。可用项：\n  " + "\n  ".join(valid))
    current = getattr(target, leaf)
    if isinstance(current, bool):
        setattr(target, leaf, value.lower() in ("1", "true", "yes", "on"))
    elif isinstance(current, int):
        setattr(target, leaf, int(value))
    else:
        setattr(target, leaf, value)


def _valid_keys(cfg: Config) -> list[str]:
    keys = ["hotkey"]
    for section in ("capture", "privacy", "api", "export"):
        obj = getattr(cfg, section)
        keys += [f"{section}.{f.name}" for f in dc_fields(obj)]
    return keys


def cmd_demo(args, cfg: Config) -> int:
    session = _build_demo_session()
    # 默认输出到用户主目录：相对路径会在 system32 等只读目录里炸掉
    session_dir = (
        Path(args.out).expanduser() if args.out else Path.home() / "snapstep-demo"
    )
    _render_demo_screenshots(session, session_dir)
    used, paths = generate_and_export(
        session, session_dir, cfg, fmt=args.format, use_ai=not args.no_ai
    )
    print(f"示例会话已生成：{session_dir}")
    _print_export_result(used, paths)
    return 0


def _build_demo_session() -> Session:
    from .models import Step, TypedRun

    session = Session(title=None, intro=None)
    demo_steps = [
        ("发布新文章 - 后台管理", (0.5, 0.12), [("操作手册", False)]),
        ("发布新文章 - 后台管理", (0.32, 0.45), []),
        ("确认发布 - 后台管理", (0.5, 0.62), [("文章已就绪，点击确认", False)]),
    ]
    for i, (win, (rx, ry), runs) in enumerate(demo_steps, 1):
        step = Step(
            index=i,
            created_at=f"2026-01-01T10:0{i}:00",
            window_title=win,
            click_x=int(rx * 1920),
            click_y=int(ry * 1080),
            monitor_width=1920,
            monitor_height=1080,
            typed_runs=[TypedRun(text=t, is_secret=s) for t, s in runs],
        )
        session.steps.append(step)
    return session


def _render_demo_screenshots(session: Session, session_dir: Path) -> None:
    """用 Pillow 画出假窗口截图，让 demo 无需真实录屏。"""
    from PIL import Image, ImageDraw, ImageFont

    from .capture import save_screenshot

    def font(size: int):
        for name in ("msyh.ttc", "arial.ttf"):
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()

    for step in session.steps:
        img = Image.new("RGB", (1280, 800), (247, 248, 250))
        d = ImageDraw.Draw(img)
        # 假窗口
        win = [120, 90, 1160, 700]
        d.rounded_rectangle(win, 12, fill=(255, 255, 255), outline=(229, 230, 235), width=2)
        d.rounded_rectangle([win[0], win[1], win[2], win[1] + 44], 12, fill=(242, 243, 245))
        d.rectangle([win[0], win[1] + 30, win[2], win[1] + 44], fill=(242, 243, 245))
        for k, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            x0, x1 = win[0] + 18 + k * 26, win[0] + 32 + k * 26
            d.ellipse([x0, win[1] + 15, x1, win[1] + 29], fill=color)
        d.text(
            (win[0] + 110, win[1] + 10),
            step.window_title or "示例窗口",
            font=font(17),
            fill=(31, 35, 41),
        )
        # 几行假正文
        for k in range(4):
            y = win[1] + 80 + k * 46
            x1 = win[2] - 40 - k * 130
            d.rounded_rectangle([win[0] + 40, y, x1, y + 22], 6, fill=(240, 241, 244))
        # 点击处的假按钮
        cx = win[0] + step.rel_x * (win[2] - win[0])
        cy = win[1] + step.rel_y * (win[3] - win[1])
        d.rounded_rectangle([cx - 80, cy - 22, cx + 80, cy + 22], 8, fill=(245, 63, 63))
        d.text((cx - 32, cy - 11), "确 定", font=font(16), fill=(255, 255, 255))
        step.screenshot = save_screenshot(img, session_dir, step.index)


# ---------- 入口 ----------


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        prog="snapstep",
        description="录屏自动生成图文教程 / Record your screen, get a step-by-step guide.",
    )
    parser.add_argument("--version", action="version", version=f"SnapStep {__version__}")
    sub = parser.add_subparsers(dest="command")

    p_record = sub.add_parser("record", help="开始录制，回车结束")
    p_record.add_argument("--out", help="会话输出目录（默认 ~/.snapstep/sessions/<时间戳>）")
    p_record.add_argument("--format", choices=["md", "html", "docx", "all"], help="导出格式")
    p_record.add_argument("--no-ai", action="store_true", help="跳过 AI 文案，直接用本地模板")

    p_export = sub.add_parser("export", help="导出已有会话")
    p_export.add_argument("session_dir", help="会话目录（含 session.json）")
    p_export.add_argument("--format", choices=["md", "html", "docx", "all"])
    p_export.add_argument("--out", help="导出目录（默认 <会话>/export）")
    p_export.add_argument("--no-ai", action="store_true")

    p_config = sub.add_parser("config", help="查看/修改配置")
    p_config.add_argument(
        "config_action", nargs="?", choices=["list", "get", "set"], default="list"
    )
    p_config.add_argument("key", nargs="?", help="如 api.api_key、privacy.privacy_mode、hotkey")
    p_config.add_argument("value", nargs="?", help="set 时的新值")

    p_demo = sub.add_parser("demo", help="生成示例教程，验证安装")
    p_demo.add_argument("--out", help="输出目录（默认 ~/snapstep-demo）")
    p_demo.add_argument("--format", choices=["md", "html", "docx", "all"])
    p_demo.add_argument("--no-ai", action="store_true")

    args = parser.parse_args(argv)
    cfg = load_config()

    if args.command == "record":
        return cmd_record(args, cfg)
    if args.command == "export":
        return cmd_export(args, cfg)
    if args.command == "config":
        return cmd_config(args, cfg)
    if args.command == "demo":
        return cmd_demo(args, cfg)

    from .ui.tray import run_gui

    run_gui()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
