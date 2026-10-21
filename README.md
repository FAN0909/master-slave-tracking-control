# Master-Slave Tracking Control

Use Python 3.10 or newer. The `.venv` directory is local to each machine and is not committed to Git.

After cloning the repository, run these commands from the project root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./run.sh
```

Run `./run.sh` on subsequent launches. It uses the Python and Qt UI compiler installed in `.venv`.

The RealSense camera also needs its hardware and system driver to be available on the machine running the application.
