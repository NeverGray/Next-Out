# Project Name: Next-Out
# Description: Create a dataframe from the average values of SES outputs. 
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

from io import BytesIO
from pathlib import Path

import pandas as pd

import NO_Excel_R01 as NV_excel
import NO_run
import NO_file_tools
import NO_GUI_multifile_monitor

def average_outputs(settings, gui=""):
    # TODO Update to use NO_GUI_multifile_monitor
    df_by_type = {}
    first_iteration = True
    # For each ses_output, add dataframes to a Dictionary organized by data type ('SSA', 'SST', etc...) 
    num = len(settings['ses_output_str'])
    msg = f'Finding mean, max, and min of {num} output files.'
    NO_run.run_msg(gui, msg)
    i = 1
    for ses_output in settings['ses_output_str']:
        ses_output_path = Path(ses_output)
        data, output_meta_data = NO_file_tools.read_h5_file(ses_output_path)
        if first_iteration:
            # Create empty lists to append values to
            for key, value in data.items():
                if not value.empty: #Prevents errors calculating values with empty data frames
                    df_by_type[key]=[]
            first_ses_output_str = ses_output #needed for Excel filename
            first_iteration = False
        for key, value in data.items():
                if not value.empty: #Prevents errors calculating values with empty data frames
                    df_by_type[key].append(value)
        msg = f'Parsed {ses_output_path.name}, {i} of {num} output files'
        NO_run.run_msg(gui, msg)
        i +=1
    # For each data type, create a data frame for mean, max, and minimum
    dfs_mean_dict = {}
    dfs_max_dict = {}
    dfs_min_dict = {}
    for key, value in df_by_type.items():
        # From https://stackoverflow.com/questions/25057835/get-the-mean-across-multiple-pandas-dataframes
        df_concat = None
        df_concat = pd.concat(value)
        by_row_index = df_concat.groupby(df_concat.index.names)
        #Select only columns that are numeric
        numeric_cols = df_concat.select_dtypes(include='number').columns
        #Calulate the mean, max, and minimum of columns with numbers
        dfs_mean_dict[key] = by_row_index[numeric_cols].mean()
        dfs_max_dict[key] = by_row_index[numeric_cols].max()
        dfs_min_dict[key] = by_row_index[numeric_cols].min()
        #Add ID, Title, and other non-numerical average dataframes
        if key in ['SSA','SST']:
            df_objects_only = value[0].select_dtypes(include=[object])
            dfs_mean_dict[key] = pd.merge(df_objects_only,dfs_mean_dict[key],how="right",on=df_concat.index.names)
            dfs_max_dict[key] =  pd.merge(df_objects_only,dfs_max_dict[key],how="right",on=df_concat.index.names)
            dfs_min_dict[key] =  pd.merge(df_objects_only,dfs_min_dict[key],how="right",on=df_concat.index.names)
        dfs_mean_dict[key].name = key
        dfs_max_dict[key].name = key
        dfs_min_dict[key].name = key
    # Create filename for Excel File
    number = str(len(settings['ses_output_str']) - 1)
    parent = str(Path(first_ses_output_str).parent)
    second_ses_output_str = (' of ' + Path(first_ses_output_str).stem
                            + " and " + number + " others" 
                            + Path(first_ses_output_str).suffix
                            )
    dict_of_dfs = {'Mean':dfs_mean_dict,
                    'Max':dfs_max_dict,
                    'Min': dfs_min_dict}
    for type, df in  dict_of_dfs.items():
        first_ses_output_str = type
        both_ses_output_str = parent + '/' + first_ses_output_str + second_ses_output_str
        output_meta_data['file_path'] = Path(both_ses_output_str)
        NV_excel.create_excel(settings, df, output_meta_data, gui)

if __name__ == "__main__":
    # Main code copied from NV_GUi
    settings={
        'ses_output_str': ['C:\\Simulations\\test\\test001.prn', 'C:\\Simulations\\test\\test002.prn'],
        'output': ['Average', 'H5_file'], 
        'file_type': 'output_file',
        'path_exe': 'C:/Simulations/SES41.exe',
        'conversion': ''
    }
    app = NO_GUI_multifile_monitor.App(settings)
    app.mainloop()
    print("app.mainloop finished")