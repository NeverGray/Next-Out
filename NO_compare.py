# Project Name: Next-Out
# Description: Compare two SES output files.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

from io import BytesIO
from pathlib import Path

import pandas as pd

import NO_run
import NO_file_tools

def compare_outputs(settings, gui=""):
    #IF these are input files, perform SES simulations
    base_file = Path(settings["ses_output_str"][0])
    second_file = Path(settings["ses_output_str"][1])
    base_df, base_output_meta_data = NO_file_tools.read_h5_file(base_file)
    second_df, second_output_meta_data = NO_file_tools.read_h5_file(second_file)
    base_data = dictionary_to_list(base_df)
    second_data = dictionary_to_list(second_df)
    num_df = len(base_data)
    suffix = base_output_meta_data['file_path'].suffix
    base_path = NO_file_tools.get_results_path2(base_output_meta_data, suffix)
    suffix = second_output_meta_data['file_path'].suffix
    second_path = NO_file_tools.get_results_path2(second_output_meta_data, suffix)
    if num_df != len(second_data):
        msg = f"Error in Comparing two output files! {base_path.name} and {second_path.name} have different structures."
        NO_run.run_msg(gui, msg)
    else:
        msg = f'Comparing {base_path.name} and {second_path.name}.'
        NO_run.run_msg(gui, msg)
        diff = []
        diff_summary = []
        p_e = []  # percent Error
        p_e_summary = []
        base_data = remove_columns(base_data)
        second_data = remove_columns(second_data)
        for i in range(num_df):
            diff_data = second_data[i] - base_data[i]
            diff_data.name = base_data[i].name
            diff.append(diff_data)
            sum_data = diff_data.describe()
            sum_data.name = diff_data.name
            diff_summary.append(sum_data)
            p_e_data = abs(diff_data / base_data[i])
            p_e_data.name = base_data[i].name
            p_e.append(p_e_data)
            p_e_sum_data = p_e_data.describe()
            p_e_sum_data.name = diff_data.name
            p_e_summary.append(p_e_sum_data)
        try:
            # Description of Stem from https://automatetheboringstuff.com/2e/chapter9/
            file_name = base_path.stem + "_to_" + second_path.stem
            file_name = file_name[0:250] #Reduce name to acceptable length (less than 255 with .xlsx added)
            file_name_4_path = file_name + ".xlsx"
            ses_output_str = settings['ses_output_str'][0]
            parent = str(Path(ses_output_str).parent)
            compare_file_path = Path(parent + '/' + file_name_4_path)
            compare_output_meta_data = base_output_meta_data.copy()
            compare_output_meta_data['file_path'] = compare_file_path
            compare_output_meta_data['ses_version'] = 'Unconfirmed'
            compare_results_path = NO_file_tools.get_results_path2(compare_output_meta_data, ".xlsx")
            p_e_text = f"Percent Error = Absolute value of [(Difference) / ({base_path.name})]"
            diff_text = f"Difference = ({second_path.name}) - ({base_path.name})"
            bio = BytesIO()
            # with pd.ExcelWriter(file_name + ".xlsx") as writer:
            with pd.ExcelWriter(bio, engine="xlsxwriter", engine_kwargs={'options': {'strings_to_numbers': False}}) as writer:
                # Create format objects once for all sheets
                format_bold = writer.book.add_format({'bold': True})
                format_underline = writer.book.add_format({'underline': True})
                # Code based on https://stackoverflow.com/questions/32957441/putting-many-python-pandas-dataframes-to-one-excel-worksheet
                for i in range(len(p_e_summary)):
                    sum_col = len(diff[i].index.names) - 1  # Aligns summary column
                    data_col_diff = len(diff[i].index.names) + len(diff[i].columns)
                    data_col_orig = len(base_data[i].index.names) + len(base_data[i].columns)
                    s_name = p_e_summary[i].name
                    title = "Next-Out Sheet: " + s_name
                    n = 0
                    start_summary_row = 3
                    data_row = start_summary_row + 11  # Starts row
                    p_e_summary[i].to_excel(
                        writer,
                        sheet_name=s_name,
                        merge_cells=False,
                        startrow=start_summary_row,
                        startcol=sum_col,
                    )
                    p_e[i].to_excel(
                        writer,
                        sheet_name=s_name,
                        merge_cells=False,
                        startrow=data_row,
                        startcol=0,
                    )
                    ws = writer.sheets[s_name]
                    # Use xlsxwriter write methods with format objects
                    ws.write(0, 0, title, format_bold)
                    ws.write(1, 0, "Summary", format_underline)
                    ws.write(data_row - 2, 0, "Data", format_underline)
                    ws.write_string(2, sum_col, p_e_text)
                    ws.write_string(data_row - 1, 0, p_e_text)
                    
                    # Calculate column positions sequentially
                    # Section 1: Percent Error (p_e) - already written at column 0
                    col_after_pe = data_col_diff + 1  # gap after p_e
                    
                    # Section 2: Difference (diff)
                    diff_summary[i].to_excel(
                        writer,
                        sheet_name=s_name,
                        merge_cells=False,
                        startrow=start_summary_row,
                        startcol=sum_col + col_after_pe,
                    )
                    diff[i].to_excel(
                        writer,
                        sheet_name=s_name,
                        merge_cells=False,
                        startrow=data_row,
                        startcol=col_after_pe,
                    )
                    ws.write_string(2, col_after_pe + 1, diff_text)
                    ws.write_string(data_row - 1, col_after_pe + 1, diff_text)
                    col_after_diff = col_after_pe + data_col_diff + 1  # gap after diff
                    
                    # Section 3: Second file data (original columns)
                    second_data[i].to_excel(
                        writer,
                        sheet_name=s_name,
                        merge_cells=False,
                        startrow=data_row,
                        startcol=col_after_diff,
                    )
                    ws.write_string(data_row - 1, col_after_diff + 1, second_path.name)
                    col_after_second = col_after_diff + data_col_orig + 1  # gap after second
                    
                    # Section 4: Base file data (original columns)
                    base_data[i].to_excel(
                        writer,
                        sheet_name=s_name,
                        merge_cells=False,
                        startrow=data_row,
                        startcol=col_after_second,
                    )
                    ws.write_string(data_row - 1, col_after_second + 1, base_path.name)
                    # Freeze panes
                    ws.freeze_panes(data_row + 1, len(p_e[i].index.names) + 1)
                # Set workbook properties
                writer.book.set_properties({
                    'creator': 'Next Vis 1p11',
                    'title': file_name
                })
            # From https://techoverflow.net/2019/07/24/how-to-write-bytesio-content-to-file-in-python/
            # Copy the BytesIO stream to the output file (AFTER writer closes)
            with open(compare_results_path, "wb") as outfile:  
                try:
                    outfile.write(bio.getvalue())
                except:
                    NO_run.run_msg(gui, f"Error writing {compare_results_path}. Try closing file and trying again.")
                # TODO Add strings using https://stackoverflow.com/questions/43537598/write-strings-text-and-pandas-dataframe-to-excel
            msg = f"Created {compare_results_path}"
            NO_run.run_msg(gui, msg)
        except:
            msg = f"CRITICAL ERROR! Constructing (not saving) Excel File {file_name}.xlsx. Close the file if opened."
            NO_run.run_msg(gui, msg)

def dictionary_to_list(dic):
    new_list = []
    for value in dic.values():
        new_list.append(value)
    return new_list

def remove_columns(df_list):
    """Removes columns that are strings so comparison can be completed."""
    for df in df_list:
        # Select only columns with object (string) dtype and drop them
        string_columns = df.select_dtypes(include=['object']).columns
        if len(string_columns) > 0:
            df.drop(columns=string_columns, inplace=True)
    return df_list

if __name__ == "__main__":
    directory_str = 'C:\\Simulations\\Test\\'
    ses_output_list = [
        directory_str + 'normal.no', 
        directory_str + 'normal.h5'
        ]
    settings = {
        "ses_output_str": ses_output_list,
        "visio_template": None,
        "simtime": 9999.0,
        "conversion": "",
        "output": [""],
        "file_type": "H5_file",
        "path_exe": "C:\\Simulations\\_EXE\\SESV6_32.exe"
    }
    import datetime
    now1 = datetime.datetime.now()
    print ("start date and time : ")
    print (now1.strftime("%Y-%m-%d %H:%M:%S"))
    compare_outputs(settings)
    now2 = datetime.datetime.now()
    print ("end date and time : ")
    print (now2.strftime("%Y-%m-%d %H:%M:%S"))
    print(now2-now1)

