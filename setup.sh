#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

fail() {
    echo "错误：$*" >&2
    exit 1
}

if [ -x .venv/bin/python ] && ! .venv/bin/python -c 'import sys; sys.exit(sys.version_info[:2] != (3, 12))'; then
    command -v python3.12 >/dev/null || fail "现有 .venv 不是 Python 3.12，且系统未找到 python3.12。"
    backup=".venv.backup.$(date +%Y%m%d%H%M%S).$$"
    mv .venv "$backup"
    echo "原虚拟环境不是 Python 3.12，已备份到 $backup"
fi

if [ ! -x .venv/bin/python ]; then
    command -v python3.12 >/dev/null || fail "请先安装 Python 3.12 及其 venv 模块。"
    echo "正在创建 Python 3.12 虚拟环境..."
    python3.12 -m venv .venv || fail "创建虚拟环境失败，请确认已安装 python3.12-venv。"
fi

.venv/bin/python -c 'import sys; sys.exit(sys.version_info[:2] != (3, 12))' || fail ".venv 必须使用 Python 3.12。"

echo "正在安装 requirements.txt 中的依赖..."
.venv/bin/python -m pip install -r requirements.txt
[ -x .venv/bin/pyside6-uic ] || fail "PySide6 的 pyside6-uic 未安装成功。"

nrc_extension=vendor/nrc/_nrc_host.so
[ -f "$nrc_extension" ] || fail "找不到 $nrc_extension，请检查代码是否完整。"
rm -f .venv/.nrc_lib_dir
dependencies=$(ldd "$nrc_extension") || fail "无法检查 $nrc_extension 的系统依赖。"
if [[ "$dependencies" == *"libpython3.12.so.1.0 => not found"* ]]; then
    python_lib_dir=$(.venv/bin/python -c 'import sysconfig; print(sysconfig.get_config_var("LIBDIR") or "")')
    if [ -n "$python_lib_dir" ] && [ -f "$python_lib_dir/libpython3.12.so.1.0" ]; then
        printf '%s\n' "$python_lib_dir" > .venv/.nrc_lib_dir
        export LD_LIBRARY_PATH="$python_lib_dir${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    else
        command -v apt-get >/dev/null && command -v apt-cache >/dev/null || fail "缺少 libpython3.12.so.1.0，当前系统无法使用 apt 自动安装；请安装 Python 3.12 共享库。"
        if [ "$(id -u)" -eq 0 ]; then
            apt_command=(apt-get)
        else
            command -v sudo >/dev/null || fail "缺少 libpython3.12.so.1.0，自动安装需要 sudo。"
            apt_command=(sudo apt-get)
        fi
        echo "正在更新软件包索引以查找 Python 3.12 共享库（可能需要输入 sudo 密码）..."
        "${apt_command[@]}" update
        package=""
        for candidate in libpython3.12t64 libpython3.12; do
            if apt-cache show "$candidate" >/dev/null 2>&1; then
                package="$candidate"
                break
            fi
        done
        [ -n "$package" ] || fail "当前 apt 软件源没有 Python 3.12 共享库；请先配置提供 Python 3.12 的软件源。"
        echo "正在安装 $package..."
        "${apt_command[@]}" install -y "$package"
    fi
fi

dependencies=$(ldd "$nrc_extension") || fail "无法检查 $nrc_extension 的系统依赖。"
[[ "$dependencies" != *"libpython3.12.so.1.0 => not found"* ]] || fail "仍找不到 libpython3.12.so.1.0。"
.venv/bin/python -c 'from vendor.nrc import nrc_interface' || fail "NRC 扩展加载失败，请检查上方错误和 ldd $nrc_extension 的输出。"

sha256sum requirements.txt | cut -d ' ' -f 1 > .venv/.requirements.sha256
echo "依赖环境安装完成。现在运行 ./run.sh 启动程序。"
