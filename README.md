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

## 采集 LeRobot V3 / V2.1 数据集

依赖固定为 `lerobot[dataset]==0.6.1`，PyTorch 使用 CPU 版本。更新代码后先执行 `./setup.sh`，再执行 `./run.sh`。

连接主手、从手、LinkerO6 灵巧手和三路相机，从手上电并启动主从跟随后，在主界面的 **Task** 输入框填写任务描述，选择保存目录和 **Format** 数据格式：

| Format | 保存子目录 | 文件组织 |
| --- | --- | --- |
| LeRobot V3（默认） | `lerobot_v3/` | V3.0 Parquet、视频和元数据布局 |
| LeRobot V2.1 | `lerobot_v2_1/` | 每条 episode 独立 Parquet 和三路 MP4，任务及 episode 元数据使用 JSONL |

- **StartRecod**：直接使用 Task 输入框中的描述，以 20 FPS 开始采集一条 episode。
- **StopRecod**：停止采样，等待已采集帧写入临时目录。
- **Save episode**：后台编码三路视频，按所选格式保存到对应子目录；已有兼容数据集会追加 episode。
- **Discard episode**：删除本条 episode 的暂存数据。停止后也可以改选保存目录再保存。

Task 和 Format 会保留供下一条复用，开始采集后锁定，保存或丢弃本条 episode 后可修改。任务为空时，点击开始会在状态栏提示填写。两种格式保存相同的状态、动作、图像和语言任务。V2.1 复用当前依赖的流式视频编码器，随后整理为旧版文件布局，不需要切换安装 LeRobot 版本。

`observation.state` 是从手机械臂 7 维实测位置与灵巧手 6 维实测位置；`action` 是采样时刻及之前最后成功下发的 13 维绝对目标位置。机械臂使用度，手部使用 SDK 的 0～255 位置值。灵巧手目标在没有新开合指令时持续保持。三路 `observation.images.side/front/hand` 保存 RGB 视频；另外保留主手位置、NRC SDK 原始单位的 TCP、各来源单调时钟时间戳、反馈序号和样本年龄供检查。

采样以主机单调时钟进行软件对齐，不是硬件同步：图像最多落后 100 ms，状态与机械臂指令最多落后 150 ms。各设备轮询设置需要能满足这些限制。设备断开、跟随停止、反馈无效、采样漏点或写盘队列满时结束采集并标记异常，异常 episode 不能直接保存成正常固定帧率数据。录制时会禁用设置页编辑和手部测试，避免改变动作定义。

Modbus 灵巧手执行扳机动作时，会在各次串口写入后主动读取真实位置，避免动作槽阻塞定时反馈；已成功设置且没有变化的速度和力矩不会重复写入。参数发生变化时仍会重新下发，断开设备或通信失败后会清除参数缓存。数据过期日志会显示实际样本年龄与允许上限，采集的时效检查保持不变。

原始帧先写入保存目录下的 `.episode_*`，会占用额外磁盘空间，保存成功后自动清理。关闭窗口会等待采集或保存结束，未点击 Save 的完整 episode 保留在暂存目录，可用下列命令恢复保存（路径换成实际目录）：

```bash
.venv/bin/python -m src.recording.episode_recorder /path/to/.episode_xxx --output /path/to/save_parent
```

代码位于 `src/recording/`，V2.1 文件布局适配位于 `lerobot_v21.py`。恢复命令沿用暂存清单中的格式；旧暂存清单没有格式字段时默认使用 V3。数据只保存到本机，不自动上传。已有数据集追加失败时会保留 `.lerobot_v3.saving.json` 或 `.lerobot_v2_1.saving.json` 和暂存数据，并拒绝继续盲目追加；请检查失败原因和数据集完整性，或改选新的保存目录。

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

## Record LeRobot V3 / V2.1 datasets

Run `./setup.sh` after updating dependencies, then `./run.sh`. Recording uses `lerobot[dataset]==0.6.1` and CPU PyTorch.

Connect the master arm, powered slave arm, LinkerO6 hand, and all three cameras, then start following. Enter a description in the main window's **Task** field, select a parent directory and **Format**, and click **StartRecod** to record directly at 20 FPS. **LeRobot V3** (default) writes the V3.0 layout to `lerobot_v3/`. **LeRobot V2.1** writes one Parquet file and three MP4 files per episode, with JSONL metadata, to `lerobot_v2_1/`. Both formats preserve the same observations, actions, images, and language tasks. V2.1 reuses the current streaming encoder and reorganizes its output; no dependency version change is needed.

Task and Format stay available for reuse, are locked when recording starts, and can be edited after saving or discarding the current episode; an empty task produces a status-bar message. **StopRecod** stops sampling and drains pending writes. **Save episode** encodes videos in the background and appends to the matching compatible dataset. **Discard episode** removes the staged episode. The destination can also be changed after stopping.

The 13-dimensional `observation.state` contains measured slave joints and hand positions; `action` contains the last successfully sent absolute targets at or before each tick. Arm positions use degrees, hand positions use SDK values from 0 to 255. Three RGB videos, master positions, native NRC TCP values, source timestamps, feedback sequences, and source ages are also stored. Alignment uses host monotonic timestamps: images may be at most 100 ms old; state and arm commands, 150 ms. This is software alignment, not hardware synchronization. Invalid feedback, disconnects, stopped following, missed ticks, or a full disk queue end the episode as an error. Settings and manual hand tests are disabled while capturing.

For Modbus hand actions, actual position feedback is read between serial writes so the action slot does not starve feedback polling. Successfully configured speed and force are reused until changed; disconnects and communication failures invalidate this cache. Stale-data errors report the actual sample age and limit. Recording freshness limits are unchanged.

Raw frames are staged under `.episode_*`, requiring additional disk space until a successful save. Closing waits for background work; complete unsaved episodes remain staged and can be exported with `.venv/bin/python -m src.recording.episode_recorder STAGING_DIR --output SAVE_PARENT`. Recovery uses the format stored in the manifest; older manifests default to V3. Recording never uploads to the Hub. A failed append leaves `.lerobot_v3.saving.json` or `.lerobot_v2_1.saving.json` and blocks further automatic appends until the dataset is inspected; the staged episode can instead be saved to another parent directory.
