Example Usage
=============
With the included configuration in `apps.py`, the app Git repositories `badtrack` and `fueltrack` need to be siblings to this `eluthia` folder.
```bash
git clone https://github.com/robinchew/eluthia.git
cd eluthia
EMAIL_USER=. EMAIL_PASSWORD=. PYTHONPATH=. MACHINE=orchid-inca MACHINE_FOLDER=./machines/orchid-inca APPS_PY=./apps.py python3 eluthia/build.py
```
Build folder defaults to an auto-generated temporary directory. Use `BUILD_FOLDER=my_build` to specify a folder.

You can look at the content of the build folder by:
```bash
cd my_build
tree
```
