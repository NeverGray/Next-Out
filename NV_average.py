from io import BytesIO
from pathlib import Path

import pandas as pd

import NV_excel_R01 as NV_excel
import NV_parser
import NV_run


def average_outputs(settings, gui=""):
    df_by_type = {}
    first_iteration = True
    if "Excel" in settings['output']: 
        Excel = True
    else:
        Excel = False
    # For each ses_output, add dataframes to a Dictionary organized by data type ('SSA', 'SST', etc...) 
    num = len(settings['ses_output_str'])
    msg = f'Finding mean, max, and min of {num} output files.'
    NV_run.run_msg(gui, msg)
    i = 1
    for ses_output in settings['ses_output_str']:
        #Perform SES simulation if using an input file
        if settings["file_type"] == "input_file":
            ses_output = NV_run.average_or_compare_call_ses(settings, ses_output, gui)
            if ses_output == 'Simulation failed':
                msg = 'Simulation failed'
                NV_run.run_msg(gui, msg)
                return
        ses_output_path = Path(ses_output)
        data, output_meta_data = NV_parser.parse_file(ses_output_path, gui, settings['conversion'])
        if Excel:
            NV_excel.create_excel(settings, data, output_meta_data, gui)
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
        NV_run.run_msg(gui, msg)
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
    directory_str = 'C:/Simulations/Never Gray Way/'
    ses_output_list = [
        directory_str + 'NG02-N001.inp', 
        directory_str + 'NG02-N002.inp',
        #directory_str + 'NG02-N003.inp',
        #directory_str + 'NG02-N004.inp',
        #directory_str + 'NG02-N005.inp', 
        #directory_str + 'NG02-N006.inp',
        #directory_str + 'NG02-N007.inp',
        #directory_str + 'NG02-N008.inp',
        #directory_str + 'NG02-N009.inp',
        #directory_str + 'NG02-N010.inp',
        #directory_str + 'NG02-N011.inp',   
        #directory_str + 'NG02-N012.inp',    
        ]
    settings = {
        "ses_output_str": ses_output_list,
        "results_folder_str": None,
        "visio_template": None,
        "simtime": 9999.0,
        "conversion": "tbd",
        "control": "First",
        "output": ["Average"],
        "file_type": "input_file",
        "path_exe": "C:\\simulations\\_EXE\\SVSV6_32.exe"
    }
    average_outputs(settings)
