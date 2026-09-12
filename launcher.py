"""PyInstaller 打包入口（包内 __main__.py 的相对导入在单文件模式下不适用）。"""

from snapstep.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
