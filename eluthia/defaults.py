import os
import shutil

def app_working_folder(full_path, package_name, apps):
    shutil.copytree(
        apps[package_name].working_folder,
        os.path.join(*full_path))

def control(full_path, package_name, apps):
    return f'''\
Package: {package_name}
Version: {apps[package_name].version}'''
