from io import BytesIO
from pathlib import Path

import pandas as pd
from openpyxl.styles import Font

import NV_excel
import NV_parser


def average_outputs(settings):
    df_by_type = {}
    first_iteration = True
    if "Excel" in settings['output']: 
        Excel = True
    # For each ses_output, add dataframes to a Dictionary organized by data type ('SSA', 'SST', etc...) 
    # TODO Use multiprocessor
    for ses_output in settings['ses_output_str']:
        ses_output_path = Path(ses_output)
        data, output_meta_data = NV_parser.parse_file(ses_output_path)
        if Excel:
            NV_excel.create_excel(settings, data, output_meta_data)
        if first_iteration:
            # Create empty lists to append values to
            for key, value in data.items():
                df_by_type[key]=[]
            first_ses_output_str = ses_output #needed for Excel filename
            first_iteration = False
        for key, value in data.items():
            df_by_type[key].append(value)
    # For each data type, create a data frame with the average
    dfs_averaged_dict = {}
    for key, value in df_by_type.items():
        # From https://stackoverflow.com/questions/25057835/get-the-mean-across-multiple-pandas-dataframes
        df_concat = None
        df_concat = pd.concat(value)
        by_row_index = df_concat.groupby(df_concat.index.names)
        dfs_averaged_dict[key] = by_row_index.mean()
        dfs_averaged_dict[key].name = key
    # Create filename for Excel File
    number = str(len(settings['ses_output_str']) - 1)
    parent = str(Path(first_ses_output_str).parent)
    average_ses_output_str = (
        "Average of " 
        + Path(first_ses_output_str).stem
        + " and " + number + " others" 
        + Path(first_ses_output_str).suffix
        )
    average_ses_output_str = parent + '/' + average_ses_output_str
    output_meta_data['file_path'] = Path(average_ses_output_str)
    NV_excel.create_excel(settings, dfs_averaged_dict, output_meta_data)

if __name__ == "__main__":
    directory_str = 'C:/Temp/Staggered/'
    ses_output_list = [
        directory_str + 'sinorm-detailed.OUT', 
        directory_str + 'sinorm-detailed018.OUT'
        #directory_str + 'sinorm-detailed062.OUT',
        #directory_str + 'sinorm-detailed080.OUT'
        ]
    settings = {
        "ses_output_str": ses_output_list,
        "results_folder_str": None,
        "visio_template": None,
        "simtime": 9999.0,
        "version": "tbd",
        "control": "First",
        "output": ["Visio","Excel"],
    }
    average_outputs(settings)
