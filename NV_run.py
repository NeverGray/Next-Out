import copy
import multiprocessing  # When trying to make a multiprocessing
import subprocess
from pathlib import Path

import pandas as pd

import NV_average
import NV_compare
import NV_excel_R01 as nve
import NV_file_manager as nfm
# Import of scripts
import NV_parser
import NV_route
import NV_visio as nvv


#Function to perform a single simulation
def single_sim(settings, gui=""):
    # If using input files, run SES simulation and change output string to a suffix.
    if settings["file_type"] == "input_file":
        msg = "Running SES Simulation for " + Path(settings["ses_output_str"][0]).name
        run_msg(gui, msg)
        success = run_SES(
            settings["path_exe"], settings["ses_output_str"][0], gui
            )
        if success:
            settings["ses_output_str"][0] = output_from_input(settings["ses_output_str"][0], settings["path_exe"], gui)
        else:
            #TODO add name of simulation to MSG with f' type command
            msg = "Post-processing is stopped"
            run_msg(gui, msg)
            return
    if "Compare" in settings["output"]:
        try:
            NV_compare.compare_outputs(settings, gui)
            if "Excel" in settings["output"]:
                settings["output"].remove("Excel")
            if "Visio" in settings["output"]:
                settings["output"].remove("Visio")
                run_msg(gui, "Unselect Comparsion to create Visio Templates")
            return
        except:
            run_msg(gui, "ERROR! Could not compare files.")
    if "Average" in settings["output"]:
        try:
            NV_average.average_outputs(settings, gui)
            if "Excel" in settings["output"]:
                settings["output"].remove("Excel")
            if "Visio" in settings["output"]:
                settings["output"].remove("Visio")
                run_msg(gui, "Unselect Average to create Visio Templates")
            return
        except:
            run_msg(gui, "ERROR! Could not average files.")
            return
    #TODO Works on first file in the list
    file_path = Path(settings['ses_output_str'][0])
    data, output_meta_data = NV_parser.parse_file(file_path, gui, settings['version'])
    file_name = file_path.name
    if len(data) == 0:
        run_msg(gui, "Error parsing data")
        return
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
            NV_route.create_route_excel(settings,data,output_meta_data,gui)
        except:
            msg = "Error creating Route Data Excel Files"
            run_msg(gui,msg)
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

#Multiple_Sim is an older code for concurrent processing before the process monitor was added in 2023-04, 1.30
#Function is kept for reference if errors occur with newer concurrent process

def multiple_sim(settings, gui=""):
    num_files = len(settings["ses_output_str"])
    if num_files == 0:
        run_msg(gui, "No output files found")
    elif num_files == 1:  # Catch if there is only file
        run_msg(gui, "Started multiple files processing with only one simulation")
        settings["ses_output_str"] = settings["ses_output_str"][0]
        single_sim(settings)
    else:
        # Use all processors except 1
        num_of_p = max(multiprocessing.cpu_count() - 1, 1)  
        num_of_p = min(num_of_p, num_files)
        run_msg(
            gui,
            "Processing "
            + str(num_files)
            + " SES Output files using "
            + str(num_of_p)
            + " threads",
        )
        # TODO Add messages to GUI when processing multiple files, with multiple processors
        run_msg(
            gui,
            "Status window doesn't monitor post-processing on multiple threads.\nSee terminal window and Windows's Task Manager to watch progress.",
        )
        pool = multiprocessing.Pool(num_of_p, maxtasksperchild=1)
        for name in settings["ses_output_str"]:
            # Reference2 code for multiprocess https://pymotw.com/2/multiprocessing/basics.html
            # Another code for multiprocessing https://stackoverflow.com/questions/20886565/using-multiprocessing-process-with-a-maximum-number-of-simultaneous-processes
            single_settings = copy.copy(settings) #May not be needed after updates to NV_Visio uses file.stem instead of ses_output_str
            single_settings["ses_output_str"] = [name]
            pool.apply_async(single_sim, args=(single_settings,))
        pool.close()
        pool.join()

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
    #TODO Select suffix based on SES type
    try:
        if "SVSV6_32.exe".lower() in path_exe.lower():
            extension = ".OUT"
        else:
            extension = ".PRN"
        last_period_location = ses_output_str.rfind(".")
        new_ses_output_str = ses_output_str[:last_period_location] + extension
        return new_ses_output_str
    except:
        msg = "Error in 'output_from_input' when converting file strings"
        run_msg(gui,msg)
        return ses_output_str

if __name__ == "__main__":
    directory_str = "C:\\simulations\\Next-Vis 1p21\\SI Samples\\"
    ses_output_list = directory_str + "sinorm.inp"
    settings = {
        "ses_output_str": [ses_output_list],
        "results_folder_str": None,
        "visio_template": None,
        "simtime": 9999.0,
        "version": "",
        "control": "First",
        "output": ["Excel"],
        "file_type": "input_file",
        "path_exe": "C:\\simulations\\_EXE\\SVSV6_32.exe"
    }
    single_sim(settings)
