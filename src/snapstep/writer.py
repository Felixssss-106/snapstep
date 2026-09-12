"""教程文案生成：AI（OpenAI 兼容端点）与本地模板双路径。

- AIWriter：仅用标准库 urllib 直连 /chat/completions，不引入任何 SDK。
- TemplateWriter：零配置兜底，无 API key 也能产出可读的步骤文档。

安全边界（桌面客户端，base_url 来自用户本机配置）：
- 仅允许 http/https 协议；
- 解析主机并阻断链路本地地址（云元数据 169.254.169.254 等）；
- 私网/环回地址放行，这是 Ollama、LM Studio 等本地模型的正常用法；
- 禁止跟随重定向，防止端点被劫持后把带密钥的请求转发到别处。
"""

from __future__ import annotations

import ipaddress
import json
import socket
import urllib.error
import urllib.request
from datetime import datetime

from .models import Session, Step

# 链路本地 / 云元数据段：任何情况下都不应成为 API 目标
BLOCKED_NETWORKS = [
    ipaddress.ip_network("169.254.0.0/16"),  # IPv4 link-local（AWS/GCP/Azure 元数据）
    ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
    ipaddress.ip_network("fd00:ec2::/32"),  # AWS IPv6 元数据
]

ALLOWED_SCHEMES = ("https", "http")


class WriterError(Exception):
    pass


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ARG002
        return None  # 30x 将以 HTTPError 抛出，而非自动跟随


_OPENER = urllib.request.build_opener(_NoRedirect)


def validate_endpoint(base_url: str) -> None:
    """校验用户配置的 API 端点，不合法则抛 WriterError。"""
    from urllib.parse import urlparse

    parsed = urlparse(base_url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise WriterError(f"不支持的协议 {parsed.scheme!r}（仅允许 http/https）")
    host = parsed.hostname
    if not host:
        raise WriterError(f"无法从地址中解析主机名：{base_url}")
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError as exc:
        raise WriterError(f"无法解析主机 {host}：{exc}") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if any(ip in net for net in BLOCKED_NETWORKS):
            raise WriterError(
                f"目标地址 {ip} 属于链路本地/云元数据段，已阻止（防止密钥泄露）"
            )


class TemplateWriter:
    """确定性模板文案：无需任何配置。"""

    def __init__(self, language: str = "zh") -> None:
        self.language = language

    def write(self, session: Session) -> None:
        first_window = next(
            (s.window_title for s in session.steps if s.window_title), ""
        )
        if self.language == "en":
            session.title = session.title or f"Guide · {first_window or 'Recorded steps'}"
            session.intro = session.intro or (
                f"A {len(session.steps)}-step guide recorded by SnapStep"
                f" on {datetime.now():%Y-%m-%d}."
            )
        else:
            session.title = session.title or f"操作教程 · {first_window or '屏幕操作'}"
            session.intro = session.intro or (
                f"共 {len(session.steps)} 个步骤，"
                f"由 SnapStep 于 {datetime.now():%Y-%m-%d} 录制生成。"
            )
        for step in session.steps:
            self._fill_step(step)

    def _fill_step(self, step: Step) -> None:
        step.title = step.title or f"步骤 {step.index}"
        if step.description:
            return
        if self.language == "en":
            parts = []
            if step.window_title:
                parts.append(f'In "{step.window_title}"')
            parts.append("click the target")
            typed = step.typed_text()
            if typed:
                parts.append(f'and type "{typed}"')
            if step.has_secret():
                parts.append("and enter the password (hidden)")
            step.description = " ".join(parts) + "."
        else:
            parts = []
            if step.window_title:
                parts.append(f"在「{step.window_title}」中")
            parts.append("点击目标位置")
            typed = step.typed_text()
            if typed:
                parts.append(f"输入「{typed}」")
            if step.has_secret():
                parts.append("输入密码（已隐藏）")
            step.description = "，".join(parts) + "。"


class AIWriter:
    """调用 OpenAI 兼容 /chat/completions 生成更自然的文案。"""

    SYSTEM_PROMPT_ZH = (
        "你是软件操作教程的写手。用户会给出一段屏幕操作记录"
        "（每步含窗口标题、输入内容、点击位置比例）。"
        "请输出严格的 JSON，不要输出其它任何文字：\n"
        '{"title": "整篇教程标题", "intro": "一句话说明这篇教程做什么",'
        ' "steps": [{"title": "步骤小标题(祈使句,10字内)",'
        ' "description": "一句话描述这步做了什么"}]}\n'
        "要求：steps 数量与输入步骤数完全一致；"
        "只基于记录内容描述，不要编造按钮名称等未提供的细节；"
        "描述里不要出现坐标百分比；语言：中文。"
    )
    SYSTEM_PROMPT_EN = (
        "You write software how-to documentation. The user gives a record of"
        " screen actions (each step: window title, typed text, click position"
        " as a fraction of the screen). Reply with STRICT JSON only:\n"
        '{"title": "Guide title", "intro": "One sentence about this guide",'
        ' "steps": [{"title": "Imperative step title (<8 words)",'
        ' "description": "One sentence describing the action"}]}\n'
        "The steps array length MUST equal the number of input steps."
        " Never invent details not present in the record. Language: English."
    )

    def __init__(
        self, base_url: str, api_key: str, model: str, language: str = "zh"
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.language = language

    # -- 对外 ------------------------------------------------------

    def write(self, session: Session) -> None:
        payload = self._chat(self._build_user_message(session))
        data = self._parse_json(payload)
        steps = data.get("steps") or []
        if session.title is None:
            session.title = data.get("title") or None
        if session.intro is None:
            session.intro = data.get("intro") or None
        for step, copy in zip(session.steps, steps, strict=False):
            if isinstance(copy, dict):
                step.title = step.title or str(copy.get("title") or "").strip() or None
                step.description = (
                    step.description
                    or str(copy.get("description") or "").strip()
                    or None
                )

    # -- 内部 ------------------------------------------------------

    def _build_user_message(self, session: Session) -> str:
        items = []
        for step in session.steps:
            typed = step.typed_text()
            item = {
                "step": step.index,
                "window": step.window_title,
                "typed": typed or None,
                "password_typed": step.has_secret() or None,
                "click": f"({step.rel_x:.0%}, {step.rel_y:.0%}) of screen",
            }
            items.append({k: v for k, v in item.items() if v is not None})
        return json.dumps(
            {"total_steps": len(session.steps), "actions": items},
            ensure_ascii=False,
        )

    def _chat(self, user_message: str) -> str:
        validate_endpoint(self.base_url)
        url = f"{self.base_url}/chat/completions"
        body = json.dumps(
            {
                "model": self.model,
                "temperature": 0.3,
                "messages": [
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user", "content": user_message},
                ],
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        try:
            with _OPENER.open(request, timeout=90) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            raise WriterError(f"API 返回 {exc.code}：{detail}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise WriterError(f"无法连接 {self.base_url}：{exc}") from exc
        try:
            return payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise WriterError(f"API 响应格式异常：{payload}") from exc

    def _system_prompt(self) -> str:
        return self.SYSTEM_PROMPT_ZH if self.language == "zh" else self.SYSTEM_PROMPT_EN

    @staticmethod
    def _parse_json(text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise WriterError("AI 返回内容中找不到 JSON")
        try:
            data = json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            raise WriterError(f"AI 返回的 JSON 无法解析：{exc}") from exc
        if not isinstance(data, dict):
            raise WriterError("AI 返回的 JSON 不是对象")
        return data


def apply_copy(
    session: Session, base_writer: TemplateWriter, ai_writer: AIWriter | None
) -> str:
    """AI 优先填写文案，模板只补齐 AI 没给的部分。

    返回实际使用的 writer 名称（"ai" / "template"）。
    """
    if ai_writer is not None:
        try:
            ai_writer.write(session)
            base_writer.write(session)  # 补缺：对已有 title/description 不覆盖
            return "ai"
        except WriterError:
            pass  # 网络失败、JSON 异常等：整体退回本地模板
    base_writer.write(session)
    return "template"
