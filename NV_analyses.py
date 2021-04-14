import pyinputplus as pyip
import NV_file_manager as nfm
import NV_parser as nvp
from pathlib import Path
import pandas as pd

def analyses_menu(settings):
    q_start='Analyses\n'
    answer = pyip.inputMenu(['Compare Outputs', 'Future Features'],q_start,lettered=True)
    if answer == 'Compare Outputs':
        compare_outputs()
    else:
        return

def compare_outputs():
    qbase = '''SES output file name with suffix (.OUT for SES v6): 
  Current working directory is same as NextVis Executable.
  If desired, specify abolute pathway (C:\\) or use \\ for sub-folders of working directory.
  Enter "ALL" for all files in folder, 
  or blank to quit. 
'''
    q1 = 'Enter base ' + qbase
    q2 = 'Enter second ' + qbase
    e = 'Cannot find output file. Try again'
    base_file = nfm.validate_file(q1,e)
    #TODO check if base_file or second_file is zero
    second_file = nfm.validate_file(q2,e)
    base_data = nvp.parse_file(base_file)
    second_data = nvp.parse_file(second_file)
    print('Both Files post-processed')
    num_df = len(base_data)
    if num_df != len(second_data):
        print("Error - Parsed files are different")
    else:
        diff = []
        summary =[]
        for i in range(num_df):
            diff_data = second_data[i] - base_data[i]
            diff_data.name = base_data[i].name
            diff.append(diff_data)
            sum_data = diff_data.describe()
            sum_data.name = diff_data.name 
            summary.append(sum_data)
        try:
            base_name = Path(base_file).stem #Description of Stem from https://automatetheboringstuff.com/2e/chapter9/
            second_name = Path(second_file).stem

            file_name = second_name + '_to_' + base_name
            file_name = file_name[0:250]
            #TODO output comparison file to directory of second_file

            p_windows = Path(second_file).parent
            p = str(p_windows)
            file_name = p + '\\' + file_name
            diff_text = 'Difference = '+ second_file + ' - ' + base_file
            with pd.ExcelWriter(file_name + ".xlsx") as writer:
                #Code based on https://stackoverflow.com/questions/32957441/putting-many-python-pandas-dataframes-to-one-excel-worksheet
                for i in range(len(summary)):
                    sum_col = len (diff[i].index.names) - 1 #Aligns summary column
                    data_col = len (diff[i].index.names) + len (diff[i].columns)
                    data_row = 11 #Starts row 
                    s_name = summary[i].name
                    summary[i].to_excel(writer, sheet_name = s_name, merge_cells=False, startrow=0 , startcol=sum_col)
                    diff[i].to_excel(writer, sheet_name = s_name, merge_cells=False, startrow= data_row, startcol=0)
                    second_data[i].to_excel(writer, sheet_name = s_name, merge_cells=False, startrow= data_row, startcol = (data_col + 1))
                    base_data[i].to_excel(writer, sheet_name = s_name, merge_cells=False, startrow= data_row, startcol = (data_col*2 + 2))
                    ws = writer.sheets[s_name]
                    ws.cell(row=1, column = 1, value = "Next-Vis")
                    ws.cell(row=1, column = sum_col + 1, value = s_name)
                    ws.cell(row=data_row, column= 1, value = diff_text)
                    ws.cell(row=data_row, column= data_col + 2, value = second_file)
                    ws.cell(row=data_row, column= (data_col * 2 + 3), value = base_file)
                    #TODO Speedup process by writing to memory instead of file? See https://pandas.pydata.org/docs/user_guide/io.html#io-excel-writer
                    #TODO Add strings using https://stackoverflow.com/questions/43537598/write-strings-text-and-pandas-dataframe-to-excel
            print("Created Excel File " + file_name +".xlsx")
            #TODO Remove or enable "Repeat option"
        except:
            print("ERROR! Try closing Excel file " + file_name + ".xlsx.  Try closing this file in excel and process again")
