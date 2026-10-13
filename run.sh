#!/bin/bash

set -e

echo "正在生成 UI..."
pyside6-uic src/ui/main_window.ui -o src/ui/main_window.py
pyside6-uic src/ui/settings_window.ui -o src/ui/settings_window.py

echo "正在启动程序..."
python3 main.py
