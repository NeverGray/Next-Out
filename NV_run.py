import multiprocessing  # When trying to make a multiprocessing
from pathlib import Path

import pandas as pd

import NV_excel as nve
import NV_file_manager as nfm
# Import of scripts
import NV_parser as nvp
import NV_visio as nvv


def single_sim(settings, multi_processor_name="", gui=""):
    # Adjustement if multiple files are being processed, simultaneously
    if multi_processor_name != "":
        settings["simname"] = multi_processor_name
    data, output_meta_data = nvp.parse_file(settings["simname"], gui)
    #TODO Update to use Paths in Settings parameters
    base_name = settings["simname"][:-4]
    file_path = Path(settings["simname"])
    file_name = file_path.name
    if len(data) == 0:
        return
    if "Excel" in settings["output"]:  # Create Excel File
        try:
            nve.create_excel(settings, data, output_meta_data)
            run_msg(gui, "Created Excel File " + file_name[:-4] + ".xlsx")
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
    """ #TODO update code to limit number of cores used by NumExpr. 
    Current error messages:
    2021-07-14 08:30:41,680 - INFO - Note: NumExpr detected 16 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
    2021-07-14 08:30:41,681 - INFO - NumExpr defaulting to 8 threads.
    """
    p = settings["simname"]
    all_names = nfm.find_all_files(pathway=p)
    """
    if settings['simname'].upper()=='ALL':
        #all_files = nfm.find_all_files(pathway = settings['simname'])
        all_files = nfm.find_all_files()
        p = "this is in the active directory"
    else:
        p = settings['simname'][:-4] #pathway
        all_files = nfm.find_all_files(pathway = p)"""
    num_files = len(all_names)
    if num_files == 0:
        run_msg(gui, "No output files found")
    elif num_files == 1:  # Catch if there is onle file
        run_msg(gui, "Started multiple files processing with only one simulation")
        settings["simname"] = p + "/" + all_names[0]
        single_sim(settings)
    else:
        num_of_p = max(
            multiprocessing.cpu_count() - 1, 1
        )  # Use all processors except 1
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
        for name in all_names:
            # Reference2 code for multiprocess https://pymotw.com/2/multiprocessing/basics.html
            # Another code for multiprocessing https://stackoverflow.com/questions/20886565/using-multiprocessing-process-with-a-maximum-number-of-simultaneous-processes
            if p != "":  # Directory is specified
                filepath = p + "/" + name
            else:
                filepath = name
            pool.apply_async(single_sim, args=(settings, filepath))
        pool.close()
        pool.join()


def run_msg(gui, text):
    if gui != "":
        gui.gui_text(text)
    else:
        print("Run msg: " + text)


if __name__ == "__main__":
    settings = {
        "simname": "sinorm-detailed.out",
        "visname": "2021-07-19 P.vsdx",
        "simtime": 9999.0,
        "version": "tbd",
        "control": "First",
        "output": ["Excel"],
    }
    single_sim(settings)
