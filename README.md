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

## 采集 LeRobot v3 episode

依赖已包含在 `requirements.txt` 中。连接主手、从手、LinkerO6 灵巧手及三路相机，启动主从跟随，填写 **Task**，再选择数据集的上级目录。

1. **StartRecod** 开始一条 episode，默认 20 FPS；状态栏显示已录帧数和时长。
2. **StopRecod** 停止采样并等待写盘结束。
3. **Save episode** 在后台编码并追加到 `保存路径/lerobot_v3/`。
4. **Discard episode** 删除这条尚未保存的原始采集数据。

采集使用独立线程和固定时间轴，默认延迟 50 ms 查询历史缓存；短暂调度延迟会按顺序补采，不跳过 tick，也不会压缩时间轴。设备断流、样本过期或磁盘跟不上时自动停止，已经写好的连续有效前缀仍可保存。录制期间禁用灵巧手测试及手动位置、速度命令，避免混入其他操作。

`config/recording.json` 可设置 FPS、默认任务、对齐延迟、样本年龄上限和队列大小，修改后重启程序。Task 可在界面逐条修改，写入每条 episode 的任务标签。一个数据集内必须保持 FPS、字段和每路相机分辨率一致。

- `observation.state`：13 维实测状态，前 7 维是从手关节角（度），后 6 维是灵巧手反馈位置（0～255）。
- `action`：同一顺序的 13 维绝对目标位置，使用采样时刻之前最近一次成功下发的命令；不是关节增量。
- 三路 `observation.images.side/front/hand`：RGB 视频，新数据集默认 H.264；追加已有数据集时沿用其编码参数。
- 另保留主手关节、从手 TCP 和 `observation.source_ages_ms`。每条 episode 的原始单调时钟时间戳及时间戳来源保存在 `meta/capture/<UUID>.npz`，任务、单位和采集中断原因保存在对应 JSON。

Gello 使用实际总线反馈时间，CAN 灵巧手查询必须收到新反馈。RealSense 优先将全局/系统帧时间映射到单调时钟，不支持时明确标记为 `host_arrival`。这是软件时间对齐，不等同于三路相机硬件同步；真实设备的延迟和各路样本年龄仍需检查。[RealSense 时间戳域说明](https://realsenseai.github.io/librealsense/doxygen/rs__frame_8h_source.html)

保存先在隔离目录完成编码，成功后通过提交日志追加新文件；相同 UUID 重试不会重复追加。未完成的 `.lerobot_v3.pending` 会在下次保存时恢复，请保留该目录。原始暂存为无损 BGR NPZ；三路 640×480、20 FPS 时约需 55 MB/s 写入、3.3 GB/分钟临时空间，保存成功后自动清理。

程序中断或退出时，未保存数据留在 `.episode_*`。确认程序已停止录制后，可以恢复其中的连续完整帧（重复执行不会重复追加）：

```bash
.venv/bin/python -m src.recording.recover /保存路径/.episode_xxxxx
```

运行硬件无关测试及真实 LeRobot 编码/读回测试：

```bash
.venv/bin/python -m unittest discover -s tests -v
```

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

## Record LeRobot v3 episodes

Connect both arms, the LinkerO6 hand and all three cameras, start teleoperation, enter a **Task**, then select the dataset's parent directory.

1. **StartRecod** records one episode at 20 FPS by default; the UI displays frame count and duration.
2. **StopRecod** stops sampling and drains queued frames to disk.
3. **Save episode** encodes and appends the episode to `lerobot_v3/` in the background.
4. **Discard episode** deletes the unsaved staging data.

A dedicated thread samples a fixed timeline with a 50 ms alignment delay. Brief scheduling delays are reconstructed from history without skipping ticks. Missing or stale feedback and disk backpressure stop recording; the contiguous valid prefix can still be saved. Hand test actions and manual hand position/speed commands are blocked during recording.

Edit `config/recording.json` and restart to change FPS, the default task, age limits, alignment delay or queue size. The Task field is editable between episodes. FPS, feature definitions and each camera's resolution must remain compatible when appending.

`observation.state` contains seven measured slave joint angles in degrees followed by six measured hand positions in 0–255. `action` uses the same order and stores the latest successfully sent absolute position targets at or before the sample time. Images are RGB; new datasets use H.264, while resumed datasets retain their encoding settings. Master joints, slave TCP and source ages are also retained. Original timestamps and clock sources are stored in `meta/capture/<UUID>.npz`, with task, units and capture errors in the matching JSON.

Gello timestamps track actual bus updates; CAN hand queries require a fresh reply. RealSense global/system frame times are mapped to the host monotonic clock, with an explicit `host_arrival` fallback. Software alignment does not provide hardware camera synchronization; inspect actual source ages on your hardware.

Encoding runs in an isolated directory. A recoverable commit journal and episode UUID prevent duplicate appends on retries. Preserve `.lerobot_v3.pending` if saving is interrupted. Lossless BGR staging needs approximately 55 MB/s and 3.3 GB/minute for three 640×480 cameras at 20 FPS; it is removed after successful saving.

Unsaved recordings remain in `.episode_*`. After stopping recording, recover a staged episode with:

```bash
.venv/bin/python -m src.recording.recover /save/path/.episode_xxxxx
```

Run hardware-free regression tests and actual LeRobot encode/readback tests with:

```bash
.venv/bin/python -m unittest discover -s tests -v
```
