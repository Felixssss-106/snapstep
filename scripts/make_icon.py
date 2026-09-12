"""生成 SnapStep 图标资源（icon.png / icon_rec.png / icon.ico）。

用法：python scripts/make_icon.py
产物提交进仓库，打包和 CI 不需要重新生成。
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

RESOURCES = Path(__file__).resolve().parents[1] / "src" / "snapstep" / "resources"

BASE = (47, 111, 237)  # 蓝：待机
REC = (245, 63, 63)  # 红：录制中


def draw_icon(size: int, bg: tuple[int, int, int]) -> Image.Image:
    scale = size / 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    radius = int(56 * scale)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius, fill=bg + (255,))

    # 三级台阶（step motif）
    bar_w = int(44 * scale)
    bar_h = int(18 * scale)
    gap = int(10 * scale)
    origin_x = int(64 * scale)
    base_y = int(176 * scale)
    for level in range(3):
        y1 = base_y - level * (bar_h + gap)
        y0 = y1 - bar_h
        x0 = origin_x + level * int(8 * scale)
        x1 = x0 + bar_w + level * int(26 * scale)
        d.rounded_rectangle([x0, y0, x1, y1], int(8 * scale), fill=(255, 255, 255, 255))

    # 右上角圆点（录制指示）
    dot_r = int(17 * scale)
    dot_cx, dot_cy = int(192 * scale), int(74 * scale)
    d.ellipse(
        [dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r],
        fill=(255, 255, 255, 255) if bg == BASE else bg + (0,),
    )
    if bg != BASE:  # 红底版本：圆点改白色描边空心
        ring_r = int(22 * scale)
        d.ellipse(
            [dot_cx - ring_r, dot_cy - ring_r, dot_cx + ring_r, dot_cy + ring_r],
            outline=(255, 255, 255, 255),
            width=max(2, int(4 * scale)),
        )
    return img


def main() -> None:
    RESOURCES.mkdir(parents=True, exist_ok=True)
    idle = draw_icon(256, BASE)
    rec = draw_icon(256, REC)
    idle.save(RESOURCES / "icon.png")
    rec.save(RESOURCES / "icon_rec.png")
    idle.save(
        RESOURCES / "icon.ico",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print(f"icons written to {RESOURCES}")


if __name__ == "__main__":
    main()
