"""隐私处理：密码框检测（尽力而为）。

通过 Windows UI Automation 询问「当前焦点控件是否为密码框」。
任何失败（非 Windows、被策略阻止、控件树异常）都返回 False，
绝不因为隐私检测而中断录制本身。
"""

from __future__ import annotations

import sys


def focused_control_is_password() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import uiautomation as auto

        ctrl = auto.GetFocusedControl()
        if ctrl is None:
            return False
        if getattr(ctrl, "IsPassword", False):
            return True
        # 部分应用把密码标记挂在子 Edit 控件上
        return "password" in (getattr(ctrl, "ClassName", "") or "").lower()
    except Exception:
        return False
