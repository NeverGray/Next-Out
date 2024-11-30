# Project Name: Next-Out
# Description: Performs simulations and post-process results one file at a time.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

import subprocess
from pathlib import Path

import pandas as pd

import NO_average
import NO_average
import NO_Excel_R01 as nve
import NO_file_manager as nfm
# Import of scripts
import NO_parser
import NO_route
import NO_visio as nvv


#Function to perform a single simulation
def single_sim(settings, gui=""):
    if "Compare" in settings["output"]:
        try:
            NO_average.compare_outputs(settings, gui)
            if "Excel" in settings["output"]:
                settings["output"].remove("Excel")
            if "Visio" in settings["output"]:
                settings["output"].remove("Visio")
                run_msg(gui, "Unselect Comparsion to create Visio Templates")
            return
        except:
            run_msg(gui, "ERROR! Could not compare files.")
            return
    if "Average" in settings["output"]:
        try:
            NO_average.average_outputs(settings, gui)
            if "Excel" in settings["output"]:
                settings["output"].remove("Excel")
            if "Visio" in settings["output"]:
                settings["output"].remove("Visio")
                run_msg(gui, "Unselect Average to create Visio Templates")
            return
        except:
            run_msg(gui, "ERROR! Could not average files.")
            return
    if settings["file_type"] == "input_file":
        msg = "Running SES Simulation for " + Path(settings["ses_output_str"][0]).name
        run_msg(gui, msg)
        success = run_SES(settings["path_exe"], settings["ses_output_str"][0], gui)
        if success:
            settings["ses_output_str"][0] = output_from_input(settings["ses_output_str"][0], settings["path_exe"], gui)
        else:
            #TODO add name of simulation to MSG with f' type command
            msg = "Post-processing is stopped"
            run_msg(gui, msg)
            return
    #TODO Parse the first file if there are post-processing options selected
    all_blank_values = all(value == '' for value in settings['output'])
    if not all_blank_values: 
        file_path = Path(settings['ses_output_str'][0])
        data, output_meta_data = NO_parser.parse_file(file_path, gui, settings['conversion'])
        file_name = file_path.name
        if len(data) == 0:
            run_msg(gui, "Error parsing data")
            return
    else:
        return
    #Post-processing options (Excel, Route, and Visio)
    if "Visio" in settings["output"]:
        try:
            nvv.create_visio(settings, data, output_meta_data, gui)
        except:
            run_msg(
                gui,
                "ERROR creating Visio file for "
                + file_name
                + ". Try closing the and process again",
            )
    if "Excel" in settings["output"]:  # Create Excel File
        try:
            nve.create_excel(settings, data, output_meta_data, gui)
            #run_msg(gui, "Created Excel File " + file_path.stem + ".xlsx")
        except:
            run_msg(
                gui,
                "ERROR creating Excel file "
                + file_name
                + ".xlsx.  Try closing this file in excel and process again",
            )
    if "Route" in settings["output"]:  # Route data
        try:
            NO_route.create_route_excel(settings,data,output_meta_data,gui)
        except:
            msg = "Error creating Route Data Excel Files"
            run_msg(gui,msg)


def run_msg(gui, text):
    if gui != "":
        gui.gui_text(text)
    else:
        print("Run msg: " + text)

def get_results_path2(settings, output_meta_data, suffix):
    output_file_path = Path(output_meta_data['file_path'])
    output_stem = output_file_path.stem
    if output_meta_data['ses_version'] == "SI from IP":
        results_name_str = output_stem + '_SI' + suffix
    elif output_meta_data['ses_version'] == "IP from SI":
        results_name_str = output_stem + '_IP' + suffix
    else:
        results_name_str = output_stem + suffix
    results_folder_str = settings.get("results_folder_str")
    if results_folder_str is None:
        results_parent = output_file_path.parent
    else:
        results_parent = Path(results_folder_str)
    results_path = results_parent/Path(results_name_str)
    return results_path

def run_SES(ses_exe_path, ses_input_file_path, gui =""):
    try: 
        # Check the proces is successful, see https://realpython.com/python-subprocess/ 
        subprocess.run([ses_exe_path, ses_input_file_path], check=True) 
        return True
    except FileNotFoundError as exc: 
        msg = (f"Process failed because the executable could not be found.\n{exc}")
        run_msg(gui,msg)
        return False
    except subprocess.CalledProcessError as exc: 
        if exc.returncode == 100:
            return True
        else:
            msg = ( 
                    f"SES Simulation failed." 
                    f"Returned {exc.returncode}\n{exc}" 
                )
            run_msg(gui,msg)
            return False 

def output_from_input(ses_output_str, path_exe, gui=""):
    #TODO Update to use file_path instead of strings, see NV_process_and_monitor_files's output_from_input
    try:
        if "SES41.exe".lower() in path_exe.lower():
            extension = ".PRN"
        else:
            extension = ".OUT"
        last_period_location = ses_output_str.rfind(".")
        new_ses_output_str = ses_output_str[:last_period_location] + extension
        return new_ses_output_str
    except:
        msg = "Error in 'output_from_input' when converting file strings"
        run_msg(gui,msg)
        return ses_output_str

#Perform SES Simulations on input files for analyses using average or compare
def average_or_compare_call_ses(settings, ses_output, gui=""):
    msg = "Running SES Simulation for " + Path(ses_output).name
    run_msg(gui, msg)
    success = run_SES(settings["path_exe"], ses_output)
    if success:
        ses_output = output_from_input(ses_output, settings["path_exe"], gui)
        return ses_output
    else:
        #Simulation Failed!
        ses_output = 'Simulation failed'
        return False

def ses_version_from_exe_string(path):
    executable_name = Path(path).name
    if executable_name.lower() in ["ses41.exe","openses.exe"]:
        version = "IP"
    else:
        version = "SI"
    return version

if __name__ == "__main__":
    directory_str = "C:\\simulations\\Iterations\\"
    ses_output_list = directory_str + "Next Iteration Sheet Rev08.xlsx"
    settings = {
        "ses_output_str": [ses_output_list],
        "results_folder_str": None,
        "visio_template": None,
        "simtime": 9999.0,
        "conversion": "",
        "control": "First",
        "output": ["Excel"],
        "file_type": "",
        "path_exe": "C:\\simulations\\_EXE\\SESV6_32.exe",
    }
    single_sim(settings)
