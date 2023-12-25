"""Populate the output summary sheet for iterative files created with next-in
"""
from pathlib import Path

import next_in
import NV_CONSTANTS
import NV_parser
import openpyxl

TIME_SEGMENT = ["SSA", "SA"]
TIME_SEGMENT_SUB = ["SST", "ST", "PER"]
COMBINED_TIME = TIME_SEGMENT + TIME_SEGMENT_SUB


class Next_In_Output:
    def __init__(self, next_in_instance):
        # Read in next-in excel to a dataframe
        self.next_in = next_in_instance
        self.iteration_output = self.next_in.iteration_output
        self.create_file_name_rows()
        self.create_time_parameters_dict()

    def create_file_name_rows(self):
        self.file_name_2_rows = {}
        row_limit = len(self.iteration_output)
        for i in range(0, row_limit):
            file_name = self.iteration_output.iloc[i, 1].lower()
            self.file_name_2_rows[file_name] = i

    def create_time_parameters_dict(self):
        # Determine which units to use in Constants
        if self.next_in.ses_version == "IP":
            unit_index = 1
        else:
            unit_index = 0
        df_index = 2  # Index number to determine which dataframe
        self.parameters_dict = {}
        temp_dict = {}
        output_starts = self.iteration_output.columns.get_loc("Output_Starts")
        column_limit = len(self.iteration_output.columns)
        i = output_starts + 1
        # For each column, write a parameter
        while i < column_limit:
            column_name = self.iteration_output.columns[i]
            if type(column_name) is str:
                if column_name.capitalize() in ["Time", "Segment", "Sub"]:
                    temp_dict[column_name.capitalize()] = i
                elif column_name in NV_CONSTANTS.COLUMN_UNITS:
                    temp_dict["parameter"] = column_name
                    temp_dict["unit"] = NV_CONSTANTS.COLUMN_UNITS[column_name][
                        unit_index
                    ]
                    temp_dict["df"] = NV_CONSTANTS.COLUMN_UNITS[column_name][df_index]
                    # Need to create a copy, otherwise it is just a reference to the temp_dict
                    self.parameters_dict[i] = temp_dict.copy()
            i += 1

    def lookup_parameters(self, d, output_meta_data):
        # Get the row for the specific run
        run_name = output_meta_data["file_path"].with_suffix("").name
        run_name = run_name.lower()
        row_number = self.file_name_2_rows.get(run_name, -1)
        parameter_value_list = []
        if row_number > -1:  # That means if found a run with the same name
            for parameter_column, lookup in self.parameters_dict.items():
                df_name = lookup["df"]
                if df_name in COMBINED_TIME:
                    # Get columns numbers where value for lookup data is located
                    time_column = lookup["Time"]
                    segment_column = lookup["Segment"]
                    parameter_name = lookup["parameter"]
                    # Get the values of looked up data
                    time_value = self.iteration_output.iloc[row_number, time_column]
                    segment_value = self.iteration_output.iloc[
                        row_number, segment_column
                    ]
                    # Get additioanl values for sub-segement, if needed
                    if df_name in TIME_SEGMENT:
                        parameter_value = d[df_name].loc[time_value, segment_value][
                            parameter_name
                        ]
                    elif df_name in TIME_SEGMENT_SUB:
                        sub_column = lookup["Sub"]
                        sub_value = self.iteration_output.iloc[row_number, sub_column]
                        parameter_value = d[df_name].loc[
                            time_value, segment_value, sub_value
                        ][parameter_name]
                    # Lookup value
                    parameter_value_list.append(
                        [row_number, parameter_column, parameter_value]
                    )
        return parameter_value_list

    def write_summary(self):
        # Specify openpyxl verion of the file
        self.next_in_openpyxl = next_in_instance.next_in_openpyxl

        # Specify the name of the sheet you want to modify
        # TODO update to use the input from the settings file
        sheet_name = "Iteration"

        # Access the specific sheet by name
        work_sheet = self.next_in_openpyxl[sheet_name]

        # Enter values into summary sheet
        row_offset = 6
        column_offset = 1
        for list in summary_list:
            row = list[0] + row_offset
            column = list[1] + column_offset
            value = list[2]
            cell = work_sheet.cell(row, column)
            cell.value = value
        cell = work_sheet.cell(7, 30)
        cell.value = 6969
        cell.data_type = "n"
        # TODO Use the output name
        self.next_in_openpyxl.save(
            Path(settings["ses_output_str"][0]).parent / "next-sim-020.xlsx"
        )


if __name__ == "__main__":
    summary_list = []
    next_in_name = "Next Iteration Sheet Rev13.xlsx"
    settings = {
        "ses_output_str": [
            "C:/Users/msn/OneDrive - Never Gray/Software Development/Next-Vis/_Tasks/Next-Sim Update/Output_Summary/siinfern_Fire_01-01_140m3s_E.OUT",
            "C:/Users/msn/OneDrive - Never Gray/Software Development/Next-Vis/_Tasks/Next-Sim Update/Output_Summary/siinfern_Fire_01-02_140m3s_E.OUT",
            "C:/Users/msn/OneDrive - Never Gray/Software Development/Next-Vis/_Tasks/Next-Sim Update/Output_Summary/siinfern_Fire_01-03_140m3s_E.OUT",
        ],
        "visio_template": "C:/Simulations/Demonstration/Next Vis Samples1p21.vsdx",
        "results_folder_str": "C:/Users/msn/OneDrive - Never Gray/Software Development/Next-Vis/_Tasks/Next-Sim Update/Output_Summary/",
        "simtime": -1,
        "conversion": "",
        "output": ["Excel", "", "", "", "", ""],
        "file_type": "next_in",  # If using input file, change 'file_type' value to 'input_file
        "path_exe": "C:/Simulations/_Exe/SESV6_32.exe",
        "next_in_ses_version": "SI",
        "next_in_single_file_name": "does not matter",
        "run_ses_next_in": "run_ses",
        "iteration_worksheets": "Iteration",
        "summary_output_name": "blank for now",
    }
    save_path = Path(settings["results_folder_str"])
    settings["next_in_path"] = Path(settings["ses_output_str"][0]).parent / next_in_name
    next_in_instance = next_in.Next_In(
        settings["next_in_path"], save_path, ses_version="SI"
    )
    next_in_instance.read_iteration("Iteration")
    next_in_output = Next_In_Output(next_in_instance)
    settings["next_in_output"] = next_in_output
    # TODO work on here and get summary list to work
    for output_str in settings["ses_output_str"]:
        output_file_path = Path(output_str)
        d, output_meta_data = NV_parser.parse_file(
            output_file_path, gui="", conversion_setting=""
        )
        parameter_value_list = next_in_output.lookup_parameters(d, output_meta_data)
        summary_list.extend(parameter_value_list)
    next_in_output.write_summary()
    print("Finished")
