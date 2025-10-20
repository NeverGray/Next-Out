# Project Name: Next-Out
# Description: Creates Excel files from the 
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

from io import BytesIO
from pathlib import Path

import pandas as pd

import NO_constants
import NO_run
import NO_file_tools
import xlsxwriter #Selected engine for pd.ExcelWriter

SHEET_NAMES ={
    "SSA" :"Second-by-second Aerodynamic Data (SSA)",
    "SST" :"Second-by-second Thermodynamic data (SST)",
    "SSP" : "Second-by-second Section Preassure Change Data (SSP)",
    "TRA" :"Second-by-second Train Data (TRA)",
    "SA"  :"Summary of Aerodynamic Data (SA)",
    "ST"  :"Summary of Thermodynamic Data (ST)",
    "PER" :"Percentage of Time Temperature is Above (PER)",
    "TES" :"Train Energy Summary (TES)",
    "HSA" :"Heat Sink Analysis (for uncontrolled zones) (HSA)",
    "ECS" :"Environmental Control System Load Estimates (ECS)",
    "SA-" :"Summary of Aerodynamic Data (SA)",
    "ST-" :"Summary of Thermodynamic Data (ST)"
}

def create_excel(settings, data, output_meta_data, gui=""):
    file_name = str(output_meta_data['file_path'].name)
    excel_results_path = NO_file_tools.get_results_path2(output_meta_data, ".xlsx")
    # TODO Add error checker if excel file is open
    NO_run.run_msg(gui, "Creating Excel file " + excel_results_path.name)
    TITLES = {
        "File Name:" : output_meta_data['file_path'].name,
        "File Time:" : output_meta_data['file_time'],
        "Data:": "From worksheet name",
        "Units:": output_meta_data['ses_version']
        }
    df_startrow = len(TITLES)
    #Select index for units in NO_constants.COLUMN_UNITS value
    if output_meta_data['ses_version'] in ['IP','IP from SI']:
        unit_index = 1
    else:
        unit_index = 0
    try:
        #Write the excel file to memory, then later in a file
        bio = BytesIO()
        with pd.ExcelWriter(bio, engine="xlsxwriter", engine_kwargs={'options': {'strings_to_numbers': False}}) as writer:
            # Set color based on SES Version of IP or SI
            if output_meta_data['ses_version'] == "SI from IP":
                color_code = "#4BACC6" #Blue
            elif output_meta_data['ses_version'] == "IP from SI":
                color_code = "#8064A2" #Purple
            else:
                color_code = "#F07F09" #Orange
            # Format options for title and headers - create once for all sheets
            format_titles = writer.book.add_format() #For Titles on top
            format_titles.set_bold()
            format_index_header = writer.book.add_format() #Index on lefthand side
            format_index_header.set_bold()
            format_index_header.set_bg_color(color_code)
            format_value_header = writer.book.add_format() #Values to right of index
            format_value_header.set_bold()
            format_value_header.set_bg_color(color_code)
            format_units = writer.book.add_format()
            format_units.set_align('center')
            
            for item in data.values():
                item.to_excel(writer, sheet_name=item.name, merge_cells=False, startrow=df_startrow)
                worksheet = writer.sheets[item.name]
                # Create title rows and format
                i = 0
                for x, y in TITLES.items():
                    worksheet.write(i, 0, x, format_titles)
                    worksheet.write(i, 1, y)
                    i += 1
                # Get name of "Data:" column from worksheet name
                worksheet.write(df_startrow-2, 1, SHEET_NAMES.get(item.name[:3]))
                # Freeze cells
                freeze_column_max = len(item.index.names)
                worksheet.freeze_panes(df_startrow + 1,freeze_column_max)
                # Add autofilters to header row only (more efficient than entire dataset)
                max_col = freeze_column_max + len(item.columns) - 1
                worksheet.autofilter(df_startrow, 0, df_startrow, max_col)
                # Format headers of index of dataframe - use row formatting for efficiency
                for i in range(len(item.index.names)):
                    worksheet.write(df_startrow, i, item.index.names[i], format_index_header)
                # Format the entire header row for value columns at once
                if len(item.columns) > 0:
                    worksheet.set_row(df_startrow, None, format_value_header)
                # Write headers of values and add unit names
                unit_row = df_startrow - 1
                for i in range(len(item.columns)):
                    column = i + freeze_column_max
                    # Write column name (row format already applied above)
                    worksheet.write_string(df_startrow, column, item.columns[i])
                    if item.columns[i] in NO_constants.COLUMN_UNITS:
                        value = NO_constants.COLUMN_UNITS[item.columns[i]][unit_index]
                        worksheet.write(unit_row, column, value, format_units)
            # set propertes to Excel file
            writer.book.set_properties({
                'title':    file_name,
                'subject':  "SES Output in Next-Out Format",
                'author':   ("Next Out " + NO_constants.VERSION_NUMBER)
            })
    except:
        NO_run.run_msg(gui, f"ERROR creating Excel file {excel_results_path.name} in MEMORY before writing. Contact Justin@NeverGray.biz for this strange error.")
    try:
        # TODO Detect if file can be removed or not
        with open(excel_results_path, "wb") as outfile:  
                # Copy the BytesIO stream to the output file
                try:
                    outfile.write(bio.getvalue())
                except:
                    print(f"Error writing {file_name}.xlsx. Try closing file and trying again.")
        NO_run.run_msg(gui, f"Created Excel file {excel_results_path.name}")
    except:
        NO_run.run_msg(gui, f"ERROR writing Excel file {excel_results_path.name}. Try closing file and process again.")

if __name__ == "__main__":
    file_path_string = "C:/Simulations/Test/Test.PRN"
    visio_template = "C:/Simulations/2022-01-22/Next Vis Samples1p21.vsdx"
    settings = {
        "ses_output_str": [file_path_string],
        "visio_template": visio_template,
        "simtime": 9999.0,
        "conversion": "SI_TO_IP",
        "control": "First",
        "output": ["Excel"],
    }
    import cProfile
    import time

    import NO_parser
    conversion_setting = settings["conversion"]
    file_path = Path(settings['ses_output_str'][0])
    data, output_meta_data = NO_parser.parse_file(file_path, gui="", conversion_setting=conversion_setting)
    file_name = file_path.name
    start_create_excel = time.perf_counter()
    prof = cProfile.Profile()
    prof.enable()    
    create_excel(settings, data, output_meta_data)
    prof.disable()
    end_create_excel = time.perf_counter()
    print(f"OPTIMIZED VERSION - Time for create_excel {end_create_excel - start_create_excel:0.4f} seconds")
    # NO_run.single_sim(settings)
    # prof.print_stats()
    prof.dump_stats("C:/Simulations/Test/xlsxwriter_optimized.prof")
