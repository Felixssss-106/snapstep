"""静态导入健全性检查：所有包内相对导入必须能解析到真实模块。

背景：ui/tray.py 曾把 ..config 误写成 .config（解析到不存在的
snapstep.ui.config），纯单测发现不了，直到 exe 冒烟才暴露。
本测试用 AST 扫出全部 from ./. import 语句并验证目标文件存在。
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "snapstep"


def _relative_import_targets(tree: ast.AST, module_file: Path):
    """产出 (层级数, 模块路径片段, 行号)。"""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level > 0:
            yield node.level, node.module or "", node.lineno


def test_all_relative_imports_resolve():
    problems: list[str] = []
    for py_file in SRC.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        package_parts = py_file.parent.relative_to(SRC.parent).parts
        for level, module, lineno in _relative_import_targets(tree, py_file):
            # level=1 → 当前包；level=2 → 上一级包
            base = package_parts[: len(package_parts) - (level - 1)]
            target_parts = base + (tuple(module.split(".")) if module else ())
            if not target_parts:
                continue
            target_dir = SRC.parent.joinpath(*target_parts)
            is_package = (target_dir / "__init__.py").exists()
            is_module = SRC.parent.joinpath(*target_parts).with_suffix(".py").exists()
            if not (target_dir.is_dir() and is_package or is_module):
                problems.append(f"{py_file}:{lineno} 找不到包 {module!r}（level={level}）")
    assert not problems, "\n".join(problems)


def test_every_module_importable():
    """全部模块可导入（Qt/pynput 仅在函数内导入，模块级导入必须无副作用）。"""
    import importlib

    for py_file in SRC.rglob("*.py"):
        rel = py_file.relative_to(SRC.parent).with_suffix("")
        name = ".".join(rel.parts)
        if name.endswith("__main__"):
            continue
        importlib.import_module(name)
