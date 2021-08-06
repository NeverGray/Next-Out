import os
from pathlib import Path


def find_all_files(extensions=[".OUT", ".PRN"], pathway=None, character=None, with_path=False):
    all_files = []
    found = False
    try:
        # Return an iterator of os.DirEntr, see https://docs.python.org/3/library/os.html
        with os.scandir(pathway) as it:
            for entry in it:  # For each item in iterator
                if entry.name[-4:].upper() in extensions and entry.is_file():
                    if character is None:
                        found = True
                    else:
                        if character in entry.name:
                            found = True
                        else:
                            found = False
                    if found:
                        if not with_path:
                            all_files.append(entry.name)
                        else:
                            all_files.append(entry.path)
                    found = False
    except:
        print("Error finding all files to process")
    return all_files
