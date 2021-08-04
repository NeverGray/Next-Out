from io import BytesIO
from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font

SHEET_NAMES ={
    "SSA" :"Second-by-second Aerodynamic Data (SSA)",
    "SST" :"Second-by-second Thermodynamic data (SST)",
    "TRA" :"Second-by-second Train data (TRA)",
    "SA"  :"Summary of Aerodynamic Data (SA)",
    "ST"  :"Summary of Thermodynamic Data (ST)",
    "PER" :"Percentage of Time Temperature is Above (PER)",
    "TES" :"Train Energy Summary (TES)",
    "HSA" :"Heat Sink Analysis (for uncontrolled zones) (HSA)",
    "ECS" :"Environmental Control System Load Estimates (ECS)"
}

def create_excel(settings, data, output_meta_data):
    # TODO Add error checker if excel file is open
    # TODO Write to memory first, then to file to speed up process (especially for multiple simulations)
    file_path = Path(settings['ses_output_str'])
    base_name = file_path.stem
    file_name = file_path.name
    excel_file_name = base_name + ".xlsx"
    TITLES = {
        "File Name:" : file_name,
        "File Time:" : output_meta_data['file_time'],
        "Data:": "From worksheet name"
        }
    try:
        bio = BytesIO()
        with pd.ExcelWriter(bio, engine="openpyxl") as writer:
            for item in data:
                item.to_excel(writer, sheet_name=item.name, merge_cells=False)
                worksheet = writer.sheets[item.name]
                # Create title rows and format
                df_startrow = len(TITLES)+1
                worksheet.insert_rows(0,df_startrow - 1)
                i = 1
                for x, y in TITLES.items():
                    worksheet.cell(row=i,column = 1, value=x).font = Font(size=10)
                    worksheet.cell(row=i,column = 2, value=y)
                    i +=1
                worksheet.cell(row=df_startrow-1, column =2, value = SHEET_NAMES.get(item.name))
                # Create filters from https://stackoverflow.com/questions/51566349/openpyxl-how-to-add-filters-to-all-columns
                df_dimensions = 'A'+ str(df_startrow) + worksheet.dimensions[2:]
                worksheet.auto_filter.ref = df_dimensions
                # Freeze cells from https://stackoverflow.com/questions/25588918/how-to-freeze-entire-header-row-in-openpyxl
                freeze_column = len(item.index.names)
                freeze_cell = worksheet.cell(row=df_startrow + 1, column=freeze_column + 1)
                worksheet.freeze_panes = freeze_cell
                #Rotate Header rows
                for col in worksheet.iter_cols(min_row=df_startrow, max_row=df_startrow, min_col=len(item.index.names)+1):
                    for cell in col:
                        cell.alignment = Alignment(textRotation= 45)
            # Add properties to Excel File.  Following https://stackoverflow.com/questions/52120125/how-to-edit-core-properties-of-xlsx-file-with-python
            writer.book.properties.creator = "Next Vis"
            writer.book.properties.title = file_name
            writer.save()
            # From https://techoverflow.net/2019/07/24/how-to-write-bytesio-content-to-file-in-python/
            with open(excel_file_name, "wb") as outfile:  
                    # Copy the BytesIO stream to the output file
                    try:
                        outfile.write(bio.getvalue())
                    except:
                        print(
                            "Error writing "
                            + file_name
                            + ".xlsx. Try closing file and trying again."
                        )
        print("Created Excel File " + base_name + ".xlsx")
    except:
        print("ERROR creating Excel file "+ base_name + ".xlsx.  Try closing this file in excel and process again")

if __name__ == "__main__":
    file_path_string = "C:/Users/msn/OneDrive - Never Gray/Software Development/Next-Vis/Python2021/coolpipe.out"
    settings = {
        "ses_output_str": file_path_string,
        "visname": "2021-07-19 P.vsdx",
        "simtime": 9999.0,
        "version": "tbd",
        "control": "First",
        "output": ["Excel"],
    }
    import NV_run
    NV_run.single_sim(settings)
