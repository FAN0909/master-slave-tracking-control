#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

fail() {
    echo "错误：$*" >&2
    exit 1
}

[ -x .venv/bin/python ] && [ -x .venv/bin/pyside6-uic ] || fail "依赖环境不存在，请先运行 ./setup.sh。"
.venv/bin/python -c 'import sys; sys.exit(sys.version_info[:2] != (3, 12))' || fail ".venv 不是 Python 3.12，请运行 ./setup.sh。"

requirements_hash=$(sha256sum requirements.txt | cut -d ' ' -f 1)
[ -f .venv/.requirements.sha256 ] && [ "$(cat .venv/.requirements.sha256)" = "$requirements_hash" ] || fail "依赖环境尚未安装或 requirements.txt 已更新，请运行 ./setup.sh。"

if [ -f .venv/.nrc_lib_dir ]; then
    IFS= read -r python_lib_dir < .venv/.nrc_lib_dir
    [ -f "$python_lib_dir/libpython3.12.so.1.0" ] || fail "Python 3.12 共享库路径已失效，请运行 ./setup.sh。"
    export LD_LIBRARY_PATH="$python_lib_dir${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi

.venv/bin/python -c 'from vendor.nrc import nrc_interface' || fail "NRC 扩展加载失败，请运行 ./setup.sh。"

echo "正在生成 UI..."
.venv/bin/pyside6-uic src/ui/main_window.ui -o src/ui/main_window.py
.venv/bin/pyside6-uic src/ui/settings_window.ui -o src/ui/settings_window.py

echo "正在启动程序..."
.venv/bin/python main.py
