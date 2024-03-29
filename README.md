Requirements
============
Only runs in Ubuntu 20.04 LTS Focal and newer version. But stay in Focal because most apps are old and only works in Focal.

Example Usage
=============
With the included configuration in `apps.py`, the app Git repositories `badtrack` and `fueltrack` need to be siblings to this `eluthia` folder.
```bash
git clone https://github.com/robinchew/eluthia.git

# robin.com.au.git is being cloned because example_apps.py is configured to build it.
# example_apps.py will also refer to the build.py file that lives in robin.com.au/build.py
git clone https://github.com/robinchew/robin.com.au.git

cd eluthia
PYTHONPATH=. MACHINE=orchid-inca APPS_PY=./example_apps.py python3 eluthia/build.py
```
Build folder defaults to an auto-generated temporary directory. Use `BUILD_FOLDER=my_build` to specify a folder.

You can look at the content of the build folder by:
```bash
cd my_build
tree
```
