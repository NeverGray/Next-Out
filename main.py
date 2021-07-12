# Import of standard modules
import hashlib
import json
import logging
import multiprocessing
from os import startfile
from sys import exit as system_exit
from tkinter import *
from uuid import getnode as get_mac

import pandas as pd
import pyinputplus as pyip
import requests

import NV_file_manager as nfm
import NV_gui as nvg

# Import of scripts
import NV_parser as nvp
import NV_visio as nvv


def read_lic():
    # TODO Error checking if file doesn't exist
    license_files = nfm.find_all_files(extensions=[".LIC"], character="@")
    if len(license_files) > 1:
        print(
            "License ERROR! Too many license files with @ symbol and .lic suffix) in the directory. Only include one valid license and try again."
        )
        system_exit(
            "License ERROR! Too many license files (*.lic) in the directory. Only include one valid license and try again."
        )
    elif len(license_files) == 0:
        print(
            "License Error! Cannot find license file (*.lic). Add valid license in directory or request license from Justin@NeverGray.biz and try again."
        )
        system_exit(
            "License Error! Cannot find license file (*.lic). Add valid license in directory or request license form Justin@NeverGray.biz and try again."
        )
    else:
        filepath = license_files[0]
    with open(filepath, "r") as file_object:
        lines = file_object.readlines()
    for line in lines:
        if line.startswith("license_key ="):
            license_key = line[14:].strip()
        elif line.startswith("keygen_account_id ="):
            keygen_account_id = line[19:].strip()
        elif line.startswith("keygen_activation_token"):
            keygen_activation_token = line[25:].strip()
    return license_key, keygen_account_id, keygen_activation_token


def activate_license(license_key, keygen_account_id, kegen_activation_token):
    logging.getLogger("urllib3").setLevel(
        logging.WARNING
    )  # Remove debugging screen from request, see https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
    machine_fingerprint = hashlib.sha256(str(get_mac()).encode("utf-8")).hexdigest()
    validation = requests.post(
        "https://api.keygen.sh/v1/accounts/{}/licenses/actions/validate-key".format(
            keygen_account_id
        ),
        headers={
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
        },
        data=json.dumps(
            {
                "meta": {
                    "scope": {"fingerprint": machine_fingerprint},
                    "key": license_key,
                }
            }
        ),
    ).json()

    if "errors" in validation:
        errs = validation["errors"]

        return (
            False,
            "license validation failed: {}".format(
                map(lambda e: "{} - {}".format(e["title"], e["detail"]).lower(), errs)
            ),
        )

    # If the license is valid for the current machine, that means it has
    # already been activated. We can return early.
    if validation["meta"]["valid"]:
        return True, "license has already been activated on this machine"

    # Otherwise, we need to determine why the current license is not valid,
    # because in our case it may be invalid because another machine has
    # already been activated, or it may be invalid because it doesn't
    # have any activated machines associated with it yet and in that case
    # we'll need to activate one.
    #
    # NOTE: the "NO_MACHINE" status is unique to *node-locked* licenses. If
    #       you need to implement a floating license, you may also need to
    #       check for the "NO_MACHINES" status (note: plural) and also the
    #       "FINGERPRINT_SCOPE_MISMATCH" status.
    if validation["meta"]["constant"] != "NO_MACHINE":
        return False, "license {}".format(validation["meta"]["detail"])

    # If we've gotten this far, then our license has not been activated yet,
    # so we should go ahead and activate the current machine.
    activation = requests.post(
        "https://api.keygen.sh/v1/accounts/{}/machines".format(keygen_account_id),
        headers={
            "Authorization": "Bearer {}".format(kegen_activation_token),
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
        },
        data=json.dumps(
            {
                "data": {
                    "type": "machines",
                    "attributes": {"fingerprint": machine_fingerprint},
                    "relationships": {
                        "license": {
                            "data": {"type": "licenses", "id": validation["data"]["id"]}
                        }
                    },
                }
            }
        ),
    ).json()

    # If we get back an error, our activation failed.
    if "errors" in activation:
        errs = activation["errors"]

        return (
            False,
            "license activation failed: {}".format(
                map(lambda e: "{} - {}".format(e["title"], e["detail"]).lower(), errs)
            ),
        )

    return True, "Next-VIS Beta license activated"


# Run from the command line:
#   python main.py some_license_key
# status, msg = activate_license(sys.argv[1])
"""Old line input manager"""


def get_input(settings=None):
    Welcome = "Next Vis - Proprocessing SES Output files"
    q_start = "Select the type of post-processing to perform or exit program: \n"
    q_repeat = "Repeat last processing Y/N: "
    q_simname = """Enter SES output file name with suffix (.OUT for SES v6): 
  Current working directory is same as NextVis Executable.
  If desired, specify abolute pathway (C:\\) or simply \\ for sub-folders of working directory.
  Enter "ALL" for all files in folder, 
  or blank to quit. 
"""
    ext_simname = [".OUT", ".PRN"]
    e = "Cannot find file, please try again or enter blank to quit. \n"
    q_visname = "Visio template with suffix (*.vsdx) or blank to quit: "
    ext_visname = [".VSDX"]
    q_simtime = "Enter simulation time for Visio template or -1 for last time: "
    repeat = "no"
    if settings["control"] != "First":
        repeat = pyip.inputYesNo(q_repeat, yesVal="yes", noVal="no")
    else:
        settings["control"] = "Single"
    if repeat == "no":
        # TODO determine version type from simname
        print(Welcome)
        settings["output"] = pyip.inputMenu(
            ["Visio", "Excel", "Both", "Analyses", "Exit"], q_start, numbered=True
        )
        if settings["output"] in ["Visio", "Excel", "Both"]:
            # Get name of output file
            settings["simname"] = nfm.validate_file(q_simname, e, ext_simname)
            if settings["simname"][-3:].upper() == "ALL":
                settings["control"] = "ALL"
            elif settings["simname"] == "":
                settings["control"] = "Stop"
            else:
                settings["control"] = "Single"
        if settings["output"] in ["Visio", "Both"]:
            settings["visname"] = nfm.validate_file(q_visname, e, ext_visname)
            if settings["visname"] != "":
                settings["simtime"] = pyip.inputNum(q_simtime, min=-1)
            else:
                settings["control"] = "Stop"
        elif settings["output"] == "Analyses":
            settings["control"] = "Analyses"
        elif settings["output"] == "Exit":
            settings["control"] = "Stop"
    return settings


def main(testing=False):
    # TODO Update security to allow entering license key only once?
    try:
        [license_key, keygen_account_id, keygen_activation_token] = read_lic()
    except:
        print(
            "Your license is not valid. Please contact Justin@NeverGray.biz to continue using the program."
        )
        input("Program will exit when you hit enter")
        return
    legit, msg = activate_license(
        license_key, keygen_account_id, keygen_activation_token
    )
    # Confirm license is activated
    # initialize variable
    print(legit, msg)
    if not legit:
        print(
            "Your license is not valid. Please contact Justin@NeverGray.biz to continue using the program."
        )
        input("Program will exit when you hit enter")
        return
    elif legit:
        root = Tk()
        gui = nvg.start_screen(root)
        root.mainloop()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main(testing=False)
