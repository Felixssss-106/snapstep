# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 打包配置：单文件 exe（GUI 无控制台）
#   pyinstaller snapstep.spec

a = Analysis(
    ["launcher.py"],
    pathex=["src"],
    binaries=[],
    datas=[("src/snapstep/resources", "snapstep/resources")],
    hiddenimports=[
        "pynput.keyboard",
        "pynput.mouse",
        "pynput._util.win32",
        "uiautomation",
        "comtypes",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SnapStep",
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon="src/snapstep/resources/icon.ico",
)
