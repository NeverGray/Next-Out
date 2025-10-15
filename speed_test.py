import copy
import cProfile
import json
import pstats
import time
from pathlib import Path

import pandas as pd

import NO_run
from NO_constants import VERSION_NUMBER as VERSION_NUMBER

def get_output_files(directory_str):
    """
    Get all files with .out or .prn extension in the specified directory and subdirectories
    
    Args:
        directory_str (str): Path to the directory to search
        
    Returns:
        list: List of Path objects for all .out and .prn files in the directory and subdirectories,
              sorted alphabetically
    """
    directory = Path(directory_str)
    # Get both .out and .prn files recursively (case-insensitive)
    out_files = list(directory.rglob("*.out"))
    prn_files = list(directory.rglob("*.prn"))
    # Combine and sort all files
    all_files = out_files + prn_files
    all_files.sort()
    return all_files

if __name__ == "__main__":
    directory_str = "C:\\Simulations\\SI Samples"
    settings = {
        'ses_output_str':'',
        'file_type': 'output_file',
        'visio_template': '', 
        'results_folder_str': None, 
        'simtime': -1, 
        'conversion': '', 
        'output': ['Excel', "H5_file", '', '', '', '', '', '', '']
    }
    wall_time_dict = dict()
    out_files = get_output_files(directory_str)
    for path_name in out_files:
        # Create individual setting to post process each file
        settings["ses_output_str"] = [str(path_name)]
        # Start time and profile
        prof = cProfile.Profile()
        prof.enable() 
        start_post_processing = time.perf_counter() 
        NO_run.single_sim(settings)
        end_post_processing = time.perf_counter()
        prof.disable()
        # Record data for post processing
        wall_time = end_post_processing - start_post_processing
        wall_time_dict[str(path_name.relative_to(directory_str))]=wall_time
        # Create subdirectory structure for profile output
        output_dir = Path(directory_str) / VERSION_NUMBER / path_name.relative_to(directory_str).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        prof_name = output_dir / f'{path_name.stem}.prof'
        prof.dump_stats(str(prof_name))
    
    df_wall_time_dict = pd.DataFrame.from_dict(wall_time_dict, orient='index', columns=[VERSION_NUMBER])
    save_path = Path(directory_str) / f'{VERSION_NUMBER}.xlsx'
    df_wall_time_dict.to_excel(save_path)

    # Print summary to console
    print("\nSummary of wall times:")
    print(df_wall_time_dict)
