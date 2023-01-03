import copy
import cProfile
import json
import pstats
import time
from pathlib import Path

import pandas as pd

import NV_run
from NV_CONSTANTS import VERSION_NUMBER as VERSION_NUMBER

if __name__ == "__main__":
    directory_str = "C:\\Simulations\\SpeedTest"
    ses_output_list = [
        directory_str + '\\normal.prn'
        ]
    ses_output_str = [
        'C:/Simulations/SpeedTest/coolpipe.OUT',
        'C:/Simulations/SpeedTest/DemoLargeSI.OUT',
        'C:/Simulations/SpeedTest/siinfern.OUT',
        'C:/Simulations/SpeedTest/sinorm.OUT',
        'C:/Simulations/SpeedTest/Test01.OUT',
        'C:/Simulations/SpeedTest/Test02R01.OUT',
        'C:/Simulations/SpeedTest/Test03.OUT',
        'C:/Simulations/SpeedTest/Test04.OUT',
        'C:/Simulations/SpeedTest/Test05.OUT',
        'C:/Simulations/SpeedTest/Test06.OUT',
        'C:/Simulations/SpeedTest/Test08.OUT'
    ]
    settings = {
        'ses_output_str': ses_output_str,
        'visio_template': '', 
        'results_folder_str': None, 
        'simtime': -1, 
        'version': '', 
        'control': 'First', 
        'output': ['Excel', '', '', '', '', '', '', '', '']
    }
    wall_time_dict = dict()
    for name in settings["ses_output_str"]:
        # Create individual setting to post process each file
        single_settings = copy.copy(settings)
        single_settings["ses_output_str"] = [name]
        path_name = Path(name)
        folder = str(path_name.parent)
        # Start time and profile
        prof = cProfile.Profile()
        prof.enable() 
        start_post_processing = time.perf_counter() 
        NV_run.single_sim(single_settings)
        end_post_processing = time.perf_counter()
        prof.disable()
        # Record data for post processing
        wall_time = end_post_processing - start_post_processing
        wall_time_dict[path_name.name]=wall_time
        prof_name = folder+'\\'+VERSION_NUMBER+'\\'+str(path_name.stem)+'.prof'
        prof.dump_stats(prof_name)
    print('hello world')
    df_wall_time_dict = pd.DataFrame.from_dict(wall_time_dict, orient='index', columns=[VERSION_NUMBER])
    folder = str(path_name.parent)
    save_path = folder + '\\' + VERSION_NUMBER + '.xlsx'
    df_wall_time_dict.to_excel(save_path)

    
    
    
