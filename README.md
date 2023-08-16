Example Usage
=============
First check that `apps.py` has the right configuration. Notably the `working_directory`.
```bash
git clone https://github.com/robinchew/eluthia.git
cd eluthia
PYTHONPATH=. MACHINE_FOLDER=./machines/orchid-inca BUILD_FOLDER=./build APPS_PY=./apps.py python3 eluthia/build.py
cd build
tree
```
