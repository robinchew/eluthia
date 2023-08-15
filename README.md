Example Usage
=============
First check that `apps.py` has the right configuration. Notably the `working_directory`.
```bash
cd machines/orchid-inca
BUILD_FOLDER=./build APPS_PY=../../apps.py python3 build.py
cd build
tree
```
