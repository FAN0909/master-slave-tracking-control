# Master-Slave Tracking Control

The current setup is for Linux x86_64 with glibc 2.34 or newer and Python 3.12 (tested with 3.12.13). The PySide6 wheel requires glibc 2.34 or newer, and the bundled NRC extension links to Python 3.12. The `.venv` directory is local to each machine and is not committed to Git.

Install Python 3.12 and its `venv` module first. Check that `python3.12 --version` works before following the commands below.

After cloning the repository, run these commands from the project root:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./run.sh
```

Run `./run.sh` on subsequent launches. It uses the Python and Qt UI compiler installed in `.venv`.

The bundled NRC extension, `vendor/nrc/_nrc_host.so`, also requires the system library `libpython3.12.so.1.0`. A Python virtual environment does not supply this library. On Linux, run `ldd vendor/nrc/_nrc_host.so` and check for `not found` before starting the app. The bundled extension is built for Linux x86_64; other systems need a compatible build from the NRC SDK.

The RealSense camera also needs its hardware and system driver to be available on the machine running the application. If setup fails on another computer, record its OS and architecture, `python3.12 --version`, the complete failing command and error output, and the output of `ldd vendor/nrc/_nrc_host.so`.
