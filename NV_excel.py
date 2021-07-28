from pathlib import Path

import pandas as pd


def create_excel(settings, data):
    # TODO Add error checker if excel file is open
    # TODO Write to memory first, then to file to speed up process (especially for multiple simulations)
    base_name = settings["simname"][:-4]
    file_path = Path(settings["simname"])
    file_name = file_path.name
    try:
        with pd.ExcelWriter(base_name + ".xlsx", engine="openpyxl") as writer:
            for item in data:
                item.to_excel(writer, sheet_name=item.name, merge_cells=False)
                # Add code to create filters
                # https://stackoverflow.com/questions/51566349/openpyxl-how-to-add-filters-to-all-columns
                worksheet = writer.sheets[item.name]
                worksheet.auto_filter.ref = worksheet.dimensions
                # Freeze cells from https://stackoverflow.com/questions/25588918/how-to-freeze-entire-header-row-in-openpyxl
                freeze_column = len(item.index.names)
                freeze_cell = worksheet.cell(row=2, column=freeze_column + 1)
                worksheet.freeze_panes = freeze_cell
            # Add properties to Excel File.  Following https://stackoverflow.com/questions/52120125/how-to-edit-core-properties-of-xlsx-file-with-python
            writer.book.properties.creator = "Next Vis Beta"
            writer.book.properties.title = file_name
        #TODO Update status message. 
        print("Created Excel File " + file_name[:-4] + ".xlsx")
    except:
        print("ERROR creating Excel file "+ file_name + ".xlsx.  Try closing this file in excel and process again")
