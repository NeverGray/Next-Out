# Import of standard modules
import datetime
import hashlib
import multiprocessing
import os
from pathlib import Path
from sys import exit as system_exit
from tkinter import *
from tkinter import messagebox
from uuid import getnode as get_mac

import keygen
import NV_gui as nvg


def read_license_file(folder_path=''):
    folder_path = Path(folder_path)
    files_lic = list(folder_path.glob('*.lic'))
    dict_data = {}
    for file in files_lic:
        with open(file, 'r') as text_file:
            lines = text_file.readlines()
            if len(lines) > 0:
                if "Next Vis" in lines[0]:  # This is a valid Next-Vis license
                    for line in lines:
                        if ":" in line:
                            key, value = line.strip().split(':', 1)
                            dict_data[key.strip()] = value.strip()
    if len(dict_data) > 0:
        return dict_data
    else:
        msg = 'Error reading in license file (*.lic).'
        messagebox.showinfo(message=msg)
    system_exit(msg)

def check_authorized_computer(license_info):
    machine_fingerprint = license_info['machine_fingerprint']
    # Check if this is an Authorized Computer. Authorize if desired.
    activation_is_required = ["NO_MACHINE",
                              "NO_MACHINES", "FINGERPRINT_SCOPE_MISMATCH"]
    try:
        validation_code, license_id, validation_info = keygen.validate_license_key_with_fingerprint(
            license_info["authorized_computer_key"], machine_fingerprint)
    except:
        answer = messagebox.askyesno(message=
            "ERROR! The program cannot communicate over the internet.\n"
            + "Do you want to generate a file to request an offline license key?")
        if answer:
            create_offline_gatekeeper(license_info)
            msg = "Email 'Gatekeeper.txt' to Justin@NeverGray.biz to request Offline License."
            messagebox.showinfo(message=msg)
            system_exit(0)
        else:
            msg = "Program will Exit. Try connecting to the internet."
            messagebox.showinfo(message=msg)
            system_exit(0)
    available = validation_info['data']['attributes']['maxMachines']
    in_use = validation_info['data']['relationships']['machines']['meta']['count']
    organization = validation_info['data']['attributes']['metadata']['organization']
    if validation_code == "VALID":
        return True, organization
    elif validation_code == 'NOT_FOUND':
        messagebox.showinfo(message=("Never Gray has no record of this license"))
        system_exit("There is no record of authorized_computer_key")
    elif validation_code in activation_is_required:
        if in_use >= available:
            msg = (f"Currently, {organization} is using {in_use} of {available} Authorized Computers.\n"
                   "Please purchase additional licenses.")
            messagebox.showinfo(message=msg)
            system_exit("This not an Authorized Computer")
        elif in_use < available:
            msg = (f"Currently, {organization} is using {in_use} of {available} Authorized Computers.\n"
                   "Do you want use a License to make this an Authorized Computer?")
            answer = messagebox.askyesno(
                message=msg, icon='question', title='Authorize Computer?')
            if answer == False:
                messagebox.showinfo(
                    message="Next-Vis only runs on Authorized Computers.")
                system_exit()
            else:
                machine_id = keygen.activate_machine_for_license(
                    license_id, machine_fingerprint, license_info["authorized_computer_token"])
                if machine_id == None:
                    messagebox.showinfo(
                        message="Could not Authorize this Computer. Contact Never Gray for help")
                    system_exit("Cannot activate license")
                else:
                    return check_authorized_computer(license_info)
    else:
        msg = f'ERROR with Check of Authorized Computer: {validation_code}'
        messagebox.showinfo(message=msg)
        system_exit("Cannot Check of Authorized Computer Status")

def checkout_floating_license(license_info):
    machine_fingerprint = license_info['machine_fingerprint']
    activation_is_required = ["NO_MACHINE",
                              "NO_MACHINES", "FINGERPRINT_SCOPE_MISMATCH"]
    validation_code, license_id, validation_info = keygen.validate_license_key_with_fingerprint(
        license_info["floating_key"], machine_fingerprint)
    organization = validation_info['data']['attributes']['metadata']['organization']
    expiry = validation_info['data']['attributes']['expiry']
    if validation_code == 'VALID':
        return True, organization, expiry
    elif validation_code == 'NOT_FOUND':
        msg = "No floating license found"
        messagebox.showinfo(message=msg)
        system_exit("No floating license found")
    elif validation_code in activation_is_required:
        available = validation_info['data']['attributes']['maxMachines']
        in_use = validation_info['data']['relationships']['machines']['meta']['count']
        organization = validation_info['data']['attributes']['metadata']['organization']
        # TODO Add check for number of licenses available
        machine_id = keygen.activate_machine_for_license(
            license_id, machine_fingerprint, license_info["floating_token"])
        if machine_id == None and available >= in_use:
            msg = (f"Currently, {organization} is using all {available} Floating Licenses.\n"
                    "Wait for a floating license to become free or purchase additional licenses.")
            messagebox.showinfo(message=msg)
            system_exit("Maximum Floating Licenses in Use")
        else:
            return checkout_floating_license(license_info)
    else:
        msg = (f"ERROR in checkout_floating_license: {validation_code}")
        messagebox.showinfo(message=msg)
        system_exit(msg)

def create_offline_gatekeeper(license_info):
    string_list = []
    try:
        environ_values = os.environ
        environ_variables = ['COMPUTERNAME','USERDOMAIN','USERNAME']
        for items in environ_variables:
            try:
                license_info[items] = environ_values[items]
            except:
                license_info[items] = "unavailable"
    except:
        license_info['environ_values'] = 'empty' 
    for items, values in license_info.items():
        string_list.append('{"' + items +'" : "'+ values + '"}')   
    text = '\n'.join(string_list)
    with open("Gatekeeper.txt", "w") as outfile:
        outfile.write(text)

def main(testing=False):
    machine_fingerprint = hashlib.sha256(
        str(get_mac()).encode('utf-8')).hexdigest()
    license_info = read_license_file()
    license_info['machine_fingerprint'] = machine_fingerprint
    if 'offline_key' in license_info:
        #TODO add code for offline license
        try:
            ok, key_info = keygen.verify_offline_license_key(license_info['offline_key'])
            today = datetime.date.today()
            expiry = datetime.date.fromisoformat(key_info['expiry'])
            license_info['expiry'] = expiry
        except:
            msg = "Error with Verifying Offline License Key."
            messagebox.showinfo(message=msg)
            system_exit(msg)
        if not ok:
            msg = "Offline License Key is not valid."
            messagebox.showinfo(message=msg)
            system_exit(msg)
        elif license_info['machine_fingerprint'] != key_info['machine_fingerprint']:
            msg = "Machine fingerprint do not match. Contact Never Gray for more information."
            messagebox.showinfo(message=msg)
            system_exit(msg)
        elif expiry - today < datetime.timedelta(0):
            msg = "License is Expired! Contact Never Gray to purchase a license"
            messagebox.showinfo(message=msg)
            system_exit(msg)
        else:
            license_info['type'] = 'Offline'
    elif 'floating_key' in license_info:
        authorized_computer_status, organization = check_authorized_computer(
            license_info)
        license_info['organization'] = organization
        if not authorized_computer_status:
            system_exit("This is not an Authorized Computer. See License Terms.")
        # FLOATING LICENSE. Validate the license key scoped to the current machine fingerprint
        floating_computer_status, floating_organization, expiry = checkout_floating_license(
            license_info)
        if floating_organization != license_info['organization']:
            msg = "Organizations don't match between Authorized Computer and Floating License."
            messagebox.showinfo(message=msg)
            system_exit(msg)
        license_info['expiry'] = datetime.date.fromisoformat(expiry[:10])
        license_info['type'] = 'Floating'
        # Start a heartbeat ping loop
        if not floating_computer_status:
            system_exit("Error checking out Floating License")
        keygen.maintain_hearbeat_for_machine(
            machine_fingerprint, license_info["floating_token"])
    else:
        system_exit("Error with license file (*.lic)")
    root = Tk()
    nvg.start_screen(root, license_info)
    # Passing variable to closing function from https://stackoverflow.com/questions/49220464/passing-arguments-in-tkinters-protocolwm-delete-window-function-on-python
    root.mainloop()
    if license_info['type'] == 'Floating':
        keygen.deactivate_machine_on_exit(
            machine_fingerprint, license_info["floating_token"])

if __name__ == "__main__":
    multiprocessing.freeze_support() #TODO Experiement if this command is necessary
    main(testing=False)
 