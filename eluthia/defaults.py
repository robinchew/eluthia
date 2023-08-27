import os
import shutil

def app_working_folder(full_path, package_name, apps):
    shutil.copytree(
        apps[package_name].working_folder,
        os.path.join(*full_path))

def control(full_path, package_name, apps):
    try: 
        version = apps[package_name]['version']
    except KeyError:
        version = 0
    return {
        'Package': package_name,
        'Version': version,
        'Architecture': 'all',
    }
