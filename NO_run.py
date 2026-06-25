# Project Name: Next-Out
# Description: Performs simulations and post-process results one file at a time.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

import subprocess
from pathlib import Path

import NO_Excel_R01 as nve
import NO_parser
import NO_route
import NO_visio as nvv
import NO_file_tools
import NO_summary


#Function to perform a single simulation
#TODO Merge functionality of NO_run single_sim and NO_process_multiple_files single sim
def single_sim(settings, gui=""):
    if settings["file_type"] == "input_file":
        msg = "Running SES Simulation for " + Path(settings["ses_output_str"][0]).name
        run_msg(gui, msg)
        success = run_SES(settings["path_exe"], settings["ses_output_str"][0], gui)
        if success:
            settings["ses_output_str"][0] = NO_file_tools.output_from_input(settings["ses_output_str"][0], settings["path_exe"])
            settings["file_type"] = "output_file"
        else:
            msg = "Post-processing is stopped for " + settings["ses_output_str"][0] + ".\n"
            run_msg(gui, msg)
            return
    #Only parse the file if post-processing options are selected (not all blank values)
    all_blank_values = all(value == '' for value in settings['output'])
    if not all_blank_values: 
        file_path = Path(settings['ses_output_str'][0])
        file_name = file_path.name
        if settings["file_type"] == "output_file": 
            data, output_meta_data = NO_parser.parse_file(file_path, gui, settings.get('output_conversion', ''))
            #Create no file if this is selected.
            if "H5_file" in settings["output"]:
                try:
                    NO_file_tools.save_h5_file(data, output_meta_data, settings)
                    run_msg(gui, "Created H5 File for " + file_name + ".")
                except Exception as e:
                    run_msg(
                        gui,
                        f"ERROR creating H5 File for {file_name}: {str(e)}"
                    )
        elif settings["file_type"] == "H5_file":
            data, output_meta_data = NO_file_tools.read_h5_file(file_path)
        if len(data) == 0:
            run_msg(gui, "Error parsing data")
            return
    else:
        #Only simulations were selected and there is no further post processing
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
    if "Summary" in settings["output"]:  # Summary data
        try:
            NO_summary.create_excel_summary(settings, gui)
        except Exception as e:
            msg = f"Error creating Summary Excel Files: {str(e)}"
            run_msg(gui,msg)
    run_msg(gui,"DONE!")

def run_msg(gui, text):
    if gui != "":
        gui.gui_text(text)
    else:
        print("Run msg: " + text)


def run_SES(ses_exe_path, ses_input_file_path, gui =""):
    try: 
        # Set working directory to the directory containing the input file
        input_file_dir = Path(ses_input_file_path).parent
        # Check the proces is successful, see https://realpython.com/python-subprocess/ 
        subprocess.run([ses_exe_path, ses_input_file_path], check=True, cwd=input_file_dir) 
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

if __name__ == "__main__":
    directory_str = "C:\\simulations\\test\\"
    input_file_name = "test.inp"
    settings = {
        'conversion': '',
        'file_type': 'input_file',
        'output': ['Excel', 'Visio', "H5_file", '', '', '', '', '', ''],
        'path_exe': 'C:/Simulations/_Exe/SESV6_32.exe',
        'ses_output_str': [directory_str + input_file_name],
        'simtime': -1,
        'visio_template': 'C:/Simulations/Test/Test.vsdx'}
    single_sim(settings)
