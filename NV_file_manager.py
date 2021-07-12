import os
from pathlib import Path

import pyinputplus as pyip


def validate_file(
    q, e, extensions=[".OUT", ".PRN"]
):  # Q is for prompt, e is for error, ext is for extension
    invalid = True
    while invalid:  # Output File name
        # answer = pyip.inputFilename(prompt = q,blank = True, limit=5)
        answer = pyip.inputFilepath(prompt=q, blank=True, limit=5)
        if answer.upper()[-3:] != "ALL":
            path_answer = Path() / answer  # Creates a path object
            if path_answer.is_file():
                if path_answer.suffix.upper() in extensions:
                    invalid = False
                else:
                    print("Invalid file extension")
            elif answer == "":
                invalid = False
            else:
                print(e, end="")
        else:
            invalid = False
    return answer


def find_all_files(extensions=[".OUT", ".PRN"], pathway=None, character=None):
    all_files = []
    found = False
    try:
        with os.scandir(
            pathway
        ) as it:  # Return an iterator of os.DirEntr, see https://docs.python.org/3/library/os.html
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
                        all_files.append(entry.name)
                    found = False
    except:
        print("Error finding all files to process")
    return all_files
