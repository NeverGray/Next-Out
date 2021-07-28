from io import BytesIO
from pathlib import Path

import pandas as pd
import pyinputplus as pyip
from openpyxl.styles import Font

import NV_file_manager as nfm
import NV_parser as nvp


def analyses_menu(settings):
    q_start = "Analyses\n"
    answer = pyip.inputMenu(["Compare Outputs", "Exit"], q_start, lettered=True)
    if answer == "Compare Outputs":
        compare_outputs()
    else:
        return


def compare_outputs(base_file="", second_file=""):
    # TODO Add ability to repeat last analysis
    if (base_file == "" and second_file ==""):
        qbase = """SES output file name with suffix (.OUT for SES v6): 
Current working directory is same as NextVis Executable.
If desired, specify abolute pathway (C:\\) or use \\ for sub-folders of working directory.
Enter "ALL" for all files in folder, 
or blank to quit. 
"""
        q1 = "Enter base " + qbase
        q2 = "Enter second " + qbase
        e = "Cannot find output file. Try again"
        base_file = nfm.validate_file(q1, e)
        second_file = nfm.validate_file(q2, e)
    base_list = nvp.parse_file(base_file)
    second_list = nvp.parse_file(second_file)
    base_data = base_list[0]
    second_data = second_list[0]
    print("Both Files post-processed")
    num_df = len(base_data)
    if num_df != len(second_data):
        print("Error - Parsed files are different")
    else:
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
            p_e_data = abs(diff_data / base_data[i]) * 100
            p_e_data.name = base_data[i].name
            p_e.append(p_e_data)
            p_e_sum_data = p_e_data.describe()
            p_e_sum_data.name = diff_data.name
            p_e_summary.append(p_e_sum_data)
        try:
            # Description of Stem from https://automatetheboringstuff.com/2e/chapter9/
            base_name = Path(base_file).stem  
            second_name = Path(second_file).stem
            file_name = second_name + "_to_" + base_name
            file_name = file_name[0:250]
            # TODO output comparison file to directory of second_file
            p_windows = Path(second_file).parent
            p = str(p_windows)
            file_name = p + "\\" + file_name
            p_e_text = (
                "Percent Error = Absolute value of [(Difference) / ("
                + base_file
                + ")] x 100%"
            )
            diff_text = "Difference = (" + second_file + ") - (" + base_file + ")"
            bio = BytesIO()
            # with pd.ExcelWriter(file_name + ".xlsx") as writer:
            with pd.ExcelWriter(bio, engine="openpyxl") as writer:
                # Code based on https://stackoverflow.com/questions/32957441/putting-many-python-pandas-dataframes-to-one-excel-worksheet
                for i in range(len(p_e_summary)):
                    sum_col = len(diff[i].index.names) - 1  # Aligns summary column
                    data_col = len(diff[i].index.names) + len(diff[i].columns)
                    s_name = p_e_summary[i].name
                    title = "Next-Vis Sheet: " + s_name
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
                    ws.cell(row=1, column=1, value=title)
                    ws.cell(row=1, column=1).font = Font(bold=True)
                    ws.cell(row=2, column=1, value="Summary")
                    ws.cell(row=2, column=1).font = Font(underline="single")
                    ws.cell(row = data_row -1, column=1, value="Data")
                    ws.cell(row = data_row -1, column=1).font = Font(underline="single")
                    ws.cell(row=3, column=sum_col, value=p_e_text)
                    ws.cell(row=data_row, column=1, value=p_e_text)
                    n += 1
                    startcol_num = data_col * n + n
                    diff_summary[i].to_excel(
                        writer,
                        sheet_name=s_name,
                        merge_cells=False,
                        startrow=start_summary_row,
                        startcol=sum_col + startcol_num,
                    )
                    diff[i].to_excel(
                        writer,
                        sheet_name=s_name,
                        merge_cells=False,
                        startrow=data_row,
                        startcol=startcol_num,
                    )
                    n = 1
                    startcol_num = (data_col * n + n) + 1
                    ws.cell(row=3, column=startcol_num, value=diff_text)
                    ws.cell(row=data_row, column=startcol_num, value=diff_text)
                    n += 1
                    startcol_num = data_col * n + n
                    second_data[i].to_excel(
                        writer,
                        sheet_name=s_name,
                        merge_cells=False,
                        startrow=data_row,
                        startcol=startcol_num,
                    )
                    startcol_num = (data_col * n + n) + 1
                    ws.cell(row=data_row, column=startcol_num, value=second_file)
                    n += 1
                    startcol_num = data_col * n + n
                    base_data[i].to_excel(
                        writer,
                        sheet_name=s_name,
                        merge_cells=False,
                        startrow=data_row,
                        startcol=startcol_num,
                    )
                    startcol_num = (data_col * n + n) + 1
                    ws.cell(row=data_row, column=startcol_num, value=base_file)
                    writer.book.properties.creator = "Next Vis Beta"
                    writer.book.properties.title = file_name
                writer.save()
                with open(
                    file_name + ".xlsx", "wb"
                ) as outfile:  # From https://techoverflow.net/2019/07/24/how-to-write-bytesio-content-to-file-in-python/
                    # Copy the BytesIO stream to the output file
                    try:
                        outfile.write(bio.getvalue())
                    except:
                        print(
                            "Error writing "
                            + file_name
                            + ".xlsx. Try closing file and trying again."
                        )
                    # TODO Speedup process by writing to memory instead of file? See https://pandas.pydata.org/docs/user_guide/io.html#io-excel-writer
                    # TODO Add strings using https://stackoverflow.com/questions/43537598/write-strings-text-and-pandas-dataframe-to-excel
            print("Created Excel File " + file_name + ".xlsx")
            # TODO Remove or enable "Repeat option"
        except:
            print(
                "CRITICAL ERROR! Constructing (not saving) Excel File"
                + file_name
                + ".xlsx."
            )

def remove_columns(df_list):
    #Removes columns that are strings so comparision can be completed.
    df_list[0].drop(['ID','Title'], axis =1, inplace = True)
    df_list[1].drop('ID', axis =1, inplace = True)
    return df_list

if __name__ == "__main__":
    base_path_str = ['4p2\\inferno.PRN','4p2\\normal.PRN']
    second_path_str = ['4p2\\inferno4p2.out','4p2\\normal4p2.out']
    for i in range(len(base_path_str)):
        #if i ==1: break #for testing one
        compare_outputs(base_file=base_path_str[i], second_file=second_path_str[i])
