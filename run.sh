#!/bin/bash

set -e

cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ] || [ ! -x .venv/bin/pyside6-uic ]; then
    echo "请先按照 README.md 创建 .venv 并安装 requirements.txt 中的依赖。" >&2
    exit 1
fi

echo "正在生成 UI..."
.venv/bin/pyside6-uic src/ui/main_window.ui -o src/ui/main_window.py
.venv/bin/pyside6-uic src/ui/settings_window.ui -o src/ui/settings_window.py

echo "正在启动程序..."
.venv/bin/python main.py
