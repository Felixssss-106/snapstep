"""屏幕截图与步骤标注。

导入本模块只需 Pillow；mss 延迟到真正截屏时才加载，
保证导出器/测试在没有屏幕的环境里也能工作。
"""

from __future__ import annotations

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
    img: Image.Image, session_dir: Path, index: int, image_format: str = "png"
) -> str:
    """保存原始截图，返回相对 session 目录的 POSIX 风格路径。"""
    images_dir = session_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    path = images_dir / f"step-{index:02d}.{image_format}"
    img.save(path)
    return path.relative_to(session_dir).as_posix()


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
