from io import BytesIO
from pathlib import Path
from tkinter import messagebox

import pandas as pd

import NV_CONSTANTS
import NV_run

SHEET_NAMES ={
    "SSA" :"Second-by-second Aerodynamic Data (SSA)",
    "SST" :"Second-by-second Thermodynamic data (SST)",
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
    excel_results_path = NV_run.get_results_path2(settings, output_meta_data, ".xlsx")
    # TODO Add error checker if excel file is open
    NV_run.run_msg(gui, "Creating Excel file " + excel_results_path.name)
    TITLES = {
        "File Name:" : output_meta_data['file_path'].name,
        "File Time:" : output_meta_data['file_time'],
        "Data:": "From worksheet name",
        "Units:": output_meta_data['ses_version']
        }
    df_startrow = len(TITLES)
    #Select index for units in NV_CONSTANTS.COLUMN_UNITS value
    if output_meta_data['ses_version'] in ['IP','IP from SI']:
        unit_index = 1
    else:
        unit_index = 0
    try:
        #Write the excel file to memory, then later in a file
        bio = BytesIO()
        with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
            # Set color based on SES Version of IP or SI
            if output_meta_data['ses_version'] == "SI from IP":
                color_code = "#4BACC6" #Blue
            elif output_meta_data['ses_version'] == "IP from SI":
                color_code = "#8064A2" #Purple
            else:
                color_code = "#F07F09" #Orange
            # Format options for title and headers
            format_titles = writer.book.add_format() #For Titles on top
            format_titles.set_bold()
            format_index_header = writer.book.add_format() #Index on lefthand side
            format_index_header.set_bold()
            format_index_header.set_bg_color(color_code)
            format_index_header.set_border(1)
            format_titles = writer.book.add_format()
            format_titles.set_bold()
            format_value_header = writer.book.add_format() #Values to right of index
            format_value_header.set_bold()
            format_value_header.set_bg_color(color_code)
            format_value_header.set_border(1)
            format_value_header.set_rotation(45)
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
                # Add autofilters to header data
                worksheet.autofilter(df_startrow,0,worksheet.dim_rowmax,worksheet.dim_colmax)
                # Freeze cells
                freeze_column_max = len(item.index.names)
                worksheet.freeze_panes(df_startrow + 1,freeze_column_max)
                # Format headers of index of dataframe
                for i in range(len(item.index.names)):
                    worksheet.write(df_startrow, i, item.index.names[i], format_index_header)
                # Format headers of values and add unit name
                unit_row = df_startrow -1
                for i in range(len(item.columns)):
                    column = i + freeze_column_max
                    worksheet.write(df_startrow, column, item.columns[i], format_value_header)
                    if item.columns[i] in NV_CONSTANTS.COLUMN_UNITS: 
                        value = NV_CONSTANTS.COLUMN_UNITS[item.columns[i]][unit_index]        
                        worksheet.write(unit_row, column, value, format_units)
            # set propertes to Excel file
            writer.book.set_properties({
                'title':    file_name,
                'subject':  "SES Output in Next-Vis Format",
                'author':   ("Next Vis " + NV_CONSTANTS.VERSION_NUMBER)
            })
    except:
        NV_run.run_msg(gui, "ERROR creating Excel file "+ excel_results_path.name + " in MEMORY before writing. Contact Justin@NeverGray.biz for this strange error.")
    try:
        # TODO Detect if file can be removed or not
        with open(excel_results_path, "wb") as outfile:  
                # Copy the BytesIO stream to the output file
                try:
                    outfile.write(bio.getvalue())
                except:
                    print(
                        "Error writing "
                        + file_name
                        + ".xlsx. Try closing file and trying again."
                    )
        NV_run.run_msg(gui, "Created Excel file " + excel_results_path.name)
    except:
        NV_run.run_msg(gui, "ERROR writing Excel file "+ excel_results_path.name + ". Try closing file and process again.")

if __name__ == "__main__":
    file_path_string = "C:/Simulations/SI_TO_IP/sinorm-detailed.out"
    visio_template = "C:/Simulations/2022-01-22/Next Vis Samples1p21.vsdx"
    results_folder_str = "C:/Simulations/SI_TO_IP"
    settings = {
        "ses_output_str": [file_path_string],
        "visio_template": visio_template,
        "results_folder_str": results_folder_str,
        "simtime": 9999.0,
        "conversion": "SI_TO_IP",
        "control": "First",
        "output": ["Excel"],
    }
    import cProfile
    import time

    import NV_parser
    conversion_setting = settings["conversion"]
    file_path = Path(settings['ses_output_str'][0])
    data, output_meta_data = NV_parser.parse_file(file_path, gui="", conversion_setting=conversion_setting)
    file_name = file_path.name
    start_create_excel = time.perf_counter()
    prof = cProfile.Profile()
    prof.enable()    
    create_excel(settings, data, output_meta_data)
    prof.disable()
    end_create_excel = time.perf_counter()
    print(f"Time for create_excel {end_create_excel - start_create_excel:0.4f} seconds")
    # NV_run.single_sim(settings)
    # prof.print_stats()
    prof.dump_stats(results_folder_str + "/NV 1p16 xlsxwriter.prof")
