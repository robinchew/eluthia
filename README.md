Example Usage
=============
With the included configuration in `apps.py`, the app Git repositories `badtrack` and `fueltrack` need to be siblings to this `eluthia` folder.
```bash
git clone https://github.com/robinchew/eluthia.git
cd eluthia
PYTHONPATH=. MACHINE_FOLDER=./machines/orchid-inca APPS_PY=./apps.py python3 eluthia/build.py
cd build
tree
```
Build folder defaults to an auto-generated temporary directory. Use `BUILD_FOLDER=` to specify a folder.

