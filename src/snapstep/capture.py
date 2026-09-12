"""屏幕截图与步骤标注。

导入本模块只需 Pillow；mss 延迟到真正截屏时才加载，
保证导出器/测试在没有屏幕的环境里也能工作。
"""

from __future__ import annotations

import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# 点击高亮圈颜色（快照红）
ACCENT = (245, 63, 63)


class ScreenCapture:
    """基于 mss 的截屏器。线程注意：mss 实例不跨线程，按线程懒加载。"""

    def __init__(self) -> None:
        self._sct = None

    def _client(self):
        if self._sct is None:
            import mss

            self._sct = mss.mss()
        return self._sct

    def monitor_for_point(self, x: int, y: int) -> dict:
        """返回包含该点显示器的 mss monitor 字典；找不到时退回主显示器。"""
        monitors = self._client().monitors
        for mon in monitors[1:]:
            if (
                mon["left"] <= x < mon["left"] + mon["width"]
                and mon["top"] <= y < mon["top"] + mon["height"]
            ):
                return dict(mon)
        return dict(monitors[1] if len(monitors) > 1 else monitors[0])

    def capture_point(self, x: int, y: int) -> tuple[Image.Image, dict]:
        """截取包含 (x, y) 的显示器，返回 (PIL 图像, monitor 字典)。"""
        mon = self.monitor_for_point(x, y)
        shot = self._client().grab(mon)
        img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
        return img, mon


def save_screenshot(
    img: Image.Image,
    session_dir: Path,
    index: int,
    image_format: str = "png",
    suffix: str = "",
) -> str:
    """保存原始截图，返回相对 session 目录的 POSIX 风格路径。

    suffix 用于区分同一步骤的候选帧（如 "-imm" / "-set"）。
    """
    images_dir = session_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    path = images_dir / f"step-{index:02d}{suffix}.{image_format}"
    img.save(path)
    return path.relative_to(session_dir).as_posix()


# 图片相似度：缩到 96x54 灰度后逐像素求平均绝对差（0~255）。
# < 2.0 视为「画面没变」，> 4.0 视为「明显变化」。
_SIMILARITY_SIZE = (96, 54)


def mean_diff(a: Path | Image.Image, b: Path | Image.Image) -> float:
    """两张截图的平均像素差（0~255），越小越相似。"""
    pa = a if isinstance(a, Image.Image) else Image.open(a)
    pb = b if isinstance(b, Image.Image) else Image.open(b)
    ga = pa.convert("L").resize(_SIMILARITY_SIZE)
    gb = pb.convert("L").resize(_SIMILARITY_SIZE)
    da = list(ga.getdata())
    db = list(gb.getdata())
    total = sum(abs(x - y) for x, y in zip(da, db, strict=True))
    return total / len(da)


def settle_grab(
    capture: ScreenCapture,
    monitor: dict,
    max_wait_ms: int,
    poll_ms: int = 150,
    stable_diff: float = 1.5,
) -> tuple[Image.Image, int]:
    """轮询截屏直到画面连续两帧几乎不变（界面稳定），或超时。

    返回 (稳定帧图像, 实际等待毫秒数)。
    """
    deadline = time.monotonic() + max(max_wait_ms, 0) / 1000
    last = capture.grab_monitor(monitor)
    waited = 0
    while True:
        if time.monotonic() >= deadline:
            return last, waited
        time.sleep(poll_ms / 1000)
        waited += poll_ms
        current = capture.grab_monitor(monitor)
        if mean_diff(last, current) < stable_diff:
            return current, waited
        last = current


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("msyh.ttc", "arial.ttf"):  # 优先微软雅黑，回退 Arial
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def annotate(
    img: Image.Image, rel_x: float, rel_y: float, number: int, radius: int = 28
) -> Image.Image:
    """在截图上标注点击位置：红色高亮圈 + 序号徽章，返回新图。"""
    out = img.convert("RGBA")
    overlay = Image.new("RGBA", out.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    cx, cy = rel_x * out.width, rel_y * out.height
    ring_w = max(3, out.width // 450)
    # 外圈柔光 + 内圈实线
    d.ellipse(
        [cx - radius - 8, cy - radius - 8, cx + radius + 8, cy + radius + 8],
        outline=ACCENT + (80,),
        width=ring_w + 3,
    )
    d.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        outline=ACCENT + (255,),
        width=ring_w,
    )

    # 序号徽章放在圈右上，越界时往里收
    badge_r = max(14, int(radius * 0.62))
    bx = min(max(cx + radius + 6, badge_r), out.width - badge_r - 2)
    by = max(min(cy - radius - 6, out.height - badge_r - 2), badge_r + 2)
    d.ellipse(
        [bx - badge_r, by - badge_r, bx + badge_r, by + badge_r],
        fill=ACCENT + (235,),
    )
    out = Image.alpha_composite(out, overlay)

    dd = ImageDraw.Draw(out)
    text = str(number)
    font = _load_font(badge_r * 2 - 4)
    left, top, right, bottom = dd.textbbox((0, 0), text, font=font)
    dd.text(
        (bx - (right - left) / 2 - left, by - (bottom - top) / 2 - top),
        text,
        font=font,
        fill=(255, 255, 255, 255),
    )
    return out.convert("RGB")
