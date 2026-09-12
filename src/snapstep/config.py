"""SnapStep 配置：JSON 持久化在 ~/.snapstep/config.json。"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

# 设置界面里的 API 预设（OpenAI 兼容端点）
API_PRESETS: dict[str, dict[str, str]] = {
    "GLM 智谱": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash",
    },
    "DeepSeek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
    },
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
    },
    "自定义": {"base_url": "", "model": ""},
}


@dataclass
class CaptureConfig:
    delay_ms: int = 350  # 点击后等待再截屏，让弹窗/菜单先弹出来
    image_format: str = "png"


@dataclass
class PrivacyConfig:
    privacy_mode: bool = False  # 开启后完全不截屏，只记录步骤
    mask_passwords: bool = True  # 密码框键入不记录明文（尽力检测）


@dataclass
class ApiConfig:
    base_url: str = ""  # 为空时不调用 AI，走本地模板文案
    api_key: str = ""
    model: str = ""
    language: str = "zh"  # AI 文案语言：zh / en


@dataclass
class ExportConfig:
    format: str = "html"  # md / html / docx
    embed_images: bool = True  # HTML 单文件内嵌 base64，方便直接分享


@dataclass
class Config:
    hotkey: str = "<ctrl>+<alt>+s"  # 开始/停止录制（GUI 生效）
    capture: CaptureConfig = field(default_factory=CaptureConfig)
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)
    api: ApiConfig = field(default_factory=ApiConfig)
    export: ExportConfig = field(default_factory=ExportConfig)

    def ai_enabled(self) -> bool:
        return bool(self.api.base_url and self.api.api_key and self.api.model)


def config_dir() -> Path:
    return Path.home() / ".snapstep"


def sessions_dir() -> Path:
    return config_dir() / "sessions"


def config_path() -> Path:
    return config_dir() / "config.json"


def load_config() -> Config:
    """加载配置；文件缺失或字段不完整时按默认值补齐。"""
    path = config_path()
    cfg = Config()
    if not path.exists():
        return cfg
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return cfg
    cfg.hotkey = data.get("hotkey", cfg.hotkey)
    for section, cls in (
        ("capture", CaptureConfig),
        ("privacy", PrivacyConfig),
        ("api", ApiConfig),
        ("export", ExportConfig),
    ):
        raw = data.get(section, {})
        current = getattr(cfg, section)
        for f in cls.__dataclass_fields__:
            if f in raw:
                setattr(current, f, raw[f])
    return cfg


def save_config(cfg: Config) -> Path:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(cfg), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path
