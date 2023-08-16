Example Usage
=============
```bash
git clone https://github.com/robinchew/eluthia.git
cd eluthia
BUILD_FOLDER=./build APPS_PY=../../apps.py python3 build.py
PYTHONPATH=. MACHINE_FOLDER=./machines/orchid-inca BUILD_FOLDER=./build APPS_PY=apps.py python3 eluthia/build.py
cd build
tree
```
