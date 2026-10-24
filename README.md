# 主从遥操作与数据采集

本项目面向 Linux x86_64、glibc 2.34 及以上版本和 Python 3.12（已在 Python 3.12.13 上测试）。PySide6 需要 glibc 2.34 或更新版本；项目自带的 NRC 扩展依赖 Python 3.12。虚拟环境 `.venv` 仅供本机使用，不会提交到 Git。

## 安装与启动

先安装 Python 3.12 及其 `venv` 模块，并确认 `python3.12 --version` 可以正常运行。克隆项目后，在项目根目录执行：

```bash
./setup.sh
./run.sh
```

`setup.sh` 创建 `.venv` 并安装 `requirements.txt` 和 NRC 系统依赖；`run.sh` 只检查环境、生成 UI 并启动程序。以后启动直接运行 `./run.sh`；若 `requirements.txt` 更新或需要修复环境，重新运行 `./setup.sh`。若旧 `.venv` 使用其他 Python 版本，安装脚本会将其备份并重新创建 Python 3.12 环境。

项目自带的 NRC 扩展 `vendor/nrc/_nrc_host.so` 还需要系统提供 `libpython3.12.so.1.0`。虚拟环境不会提供这个系统库。`setup.sh` 会先检查 Python 安装目录；若仍缺失，在提供对应软件包的 apt 系统上自动安装，并可能提示输入 sudo 密码。若当前软件源没有该包，安装脚本会给出错误提示；可以运行 `ldd vendor/nrc/_nrc_host.so` 检查依赖。该扩展面向 Linux x86_64；其他系统需要使用 NRC SDK 提供的兼容版本。

RealSense 相机还需要本机具备相应硬件和系统驱动。如果在另一台电脑上启动失败，请记录其操作系统与架构、`python3.12 --version`、完整的失败命令与报错，以及 `ldd vendor/nrc/_nrc_host.so` 的输出。

界面保留 StartRecod、StopRecod、Save episode 和 Discard episode 按钮，当前未绑定功能。

---

# Master-Slave Teleoperation and Data Collection

This project targets Linux x86_64 with glibc 2.34 or newer and Python 3.12 (tested with Python 3.12.13). PySide6 requires glibc 2.34 or newer, and the bundled NRC extension depends on Python 3.12. The `.venv` virtual environment is local to each machine and is not committed to Git.

## Installation and startup

Install Python 3.12 and its `venv` module first. Confirm that `python3.12 --version` works. After cloning the repository, run these commands from the project root:

```bash
./setup.sh
./run.sh
```

`setup.sh` creates `.venv` and installs `requirements.txt` and the NRC system dependency. `run.sh` only checks the environment, generates the UI, and launches the app. For later launches, run `./run.sh`; rerun `./setup.sh` after changing `requirements.txt` or to repair the environment. If an existing `.venv` uses another Python version, the setup script backs it up and creates a Python 3.12 environment.

The bundled NRC extension, `vendor/nrc/_nrc_host.so`, also needs the system library `libpython3.12.so.1.0`. A virtual environment does not supply this library. `setup.sh` first checks the Python installation directory; if the library is still missing, it installs the corresponding package on apt systems where one is available. This may prompt for a sudo password. If the current package sources do not provide it, the setup script reports an error; run `ldd vendor/nrc/_nrc_host.so` to inspect dependencies. The extension targets Linux x86_64; other systems need a compatible build from the NRC SDK.

The RealSense camera also needs its hardware and system driver on the machine running the app. If startup fails on another computer, record its OS and architecture, `python3.12 --version`, the complete failing command and error output, and the output of `ldd vendor/nrc/_nrc_host.so`.

The StartRecod, StopRecod, Save episode, and Discard episode buttons remain visible and currently have no actions assigned.
