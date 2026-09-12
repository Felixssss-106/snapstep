"""SnapStep 轻量日志：追加写入 ~/.snapstep/snapstep.log，方便用户反馈问题时排查。"""

from __future__ import annotations

import logging
from pathlib import Path

_LOGGER: logging.Logger | None = None


def config_dir() -> Path:
    return Path.home() / ".snapstep"


def get_logger() -> logging.Logger:
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER
    logger = logging.getLogger("snapstep")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    try:
        log_dir = config_dir()
        log_dir.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_dir / "snapstep.log", encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%H:%M:%S")
        )
        logger.addHandler(handler)
    except OSError:
        pass  # 日志不可用时静默降级为内存日志
    _LOGGER = logger
    return logger


def log_info(msg: str) -> None:
    get_logger().info(msg)


def log_error(msg: str) -> None:
    get_logger().error(msg)
