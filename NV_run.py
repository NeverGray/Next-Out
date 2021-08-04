import copy
import multiprocessing  # When trying to make a multiprocessing
from pathlib import Path

import pandas as pd

import NV_excel as nve
import NV_file_manager as nfm
# Import of scripts
import NV_parser as nvp
import NV_visio as nvv


def single_sim(settings, gui=""):
    # Adjustement if multiple files are being processed, simultaneously
    file_path = Path(settings['ses_output_str'])
    data, output_meta_data = nvp.parse_file(file_path, gui)
    file_name = file_path.name
    base_name = file_path.stem
    if len(data) == 0:
        return
    if "Excel" in settings["output"]:  # Create Excel File
        try:
            nve.create_excel(settings, data, output_meta_data)
            run_msg(gui, "Created Excel File " + file_path.stem + ".xlsx")
        except:
            run_msg(
                gui,
                "ERROR creating Excel file "
                + file_name
                + ".xlsx.  Try closing this file in excel and process again",
            )
 
    if "Visio" in settings["output"]:
        df_dict = {}  # Store data frames in dictionary
        for df in data:
            df_dict.update({df.name: df})
        try:
            settings["simtime"] = nvv.valid_simtime(settings["simtime"], df_dict["SSA"])
            time_4_name = int(settings["simtime"])
            settings["new_visio"] = base_name + "-" + str(time_4_name) + ".vsdx"
            nvv.update_visio(settings, df_dict, output_meta_data)
            run_msg(
                gui,
                "Created Visio File " + file_name + "-" + str(time_4_name) + ".vsdx",
            )
        except:
            run_msg(gui, "ERROR creating Visio file in NV_run.")


def multiple_sim(settings, gui=""):
    num_files = len(settings["ses_output_str"])
    if num_files == 0:
        run_msg(gui, "No output files found")
    elif num_files == 1:  # Catch if there is onle file
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
            "Status window doesn't monitor post-processing.\n See terminal window and Windows's Task Manager to watch progress",
        )
        pool = multiprocessing.Pool(num_of_p, maxtasksperchild=1)
        for name in settings["ses_output_str"]:
            # Reference2 code for multiprocess https://pymotw.com/2/multiprocessing/basics.html
            # Another code for multiprocessing https://stackoverflow.com/questions/20886565/using-multiprocessing-process-with-a-maximum-number-of-simultaneous-processes
            single_settings = copy.copy(settings)
            single_settings["ses_output_str"] = name
            pool.apply_async(single_sim, args=(single_settings,))
        pool.close()
        pool.join()


def run_msg(gui, text):
    if gui != "":
        gui.gui_text(text)
    else:
        print("Run msg: " + text)


if __name__ == "__main__":
    single = False
    ses_output_str = "C:/Users/msn/OneDrive - Never Gray/Software Development/Next-Vis/Python2021/siinfern.out"
    settings = {
        "ses_output_str": ses_output_str,
        "visname": "2021-07-19 P.vsdx",
        "simtime": 9999.0,
        "version": "tbd",
        "control": "First",
        "output": ["Excel","Visio"],
    }
    if single:
        single_sim(settings)
    else:
        settings["ses_output_str"] = ['C:/Users/msn/OneDrive - Never Gray/Software Development/Next-Vis/Python2021/siinfern.out', 'C:/Users/msn/OneDrive - Never Gray/Software Development/Next-Vis/Python2021/siinfern - copy.out']
        multiple_sim(settings)
