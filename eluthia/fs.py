import os
from eluthia.decorators import chmod, file

FILE = lambda: None

def pick_file(path):
    @file
    def wrap(full_path_list, package_name, apps):
        with open(path, 'rb') as f:
            return f.read()
    return wrap

def pick(folder, d, last=''):
    return {
        k: pick(folder, v, k) if type(v) is dict else pick_file(os.path.join(folder, last, k))
        for k, v in d.items()
    }

@chmod(0o755)
@file
def cp_if_not_exist(*args, **kwargs):
    return '''\
        #!/bin/sh
        # Check if the number of arguments is correct
        if [ "$#" -ne 2 ]; then
            echo "Usage: $0 <source_file> <destination_directory>"
            exit 1
        fi

        source_file="$1"
        destination_directory="$2"
        destination_file="$destination_directory/$(basename "$source_file")"

        # Check if the destination file already exists
        if [ -e "$destination_file" ]; then
            echo "File already exists in the destination directory. No need to copy."
            exit 0
        fi

        # Copy the file to the destination directory
        cp "$source_file" "$destination_directory"

        echo "File copied successfully to $destination_directory"
    '''

def empty_file(full_path, *args, **kwargs):
    os.makedirs(os.path.join(*full_path[0:-1]), exist_ok=True)
    with open(os.path.join(*full_path), 'w'):
        pass
