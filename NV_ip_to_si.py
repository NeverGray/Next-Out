
from pathlib import Path

import pandas as pd

import NV_CONSTANTS
import NV_parser as nvp
import NV_run


def convert_ip_to_si(data, output_meta_data, gui=""):

    ST_temp_exception = ['Average_Positive_Dry_Bulb','Average_Negative_Dry_Bulb']
    if output_meta_data['ses_version'] == "IP":
        msg = f"Converting data from {output_meta_data['file_path'].name} to SI"
        NV_run.run_msg(gui, msg)
        #Iterate through all the dataframs in the data dictionary
        for dataframe in data.values():
            #Iterate through all columns (not indexes)
            for column in dataframe.columns:
                #Check if the column name is in column_units
                if column in NV_CONSTANTS.COLUMN_UNITS:
                    #Get the list of the units of the column for IP and SI
                    units = NV_CONSTANTS.COLUMN_UNITS[column]
                    #If the two units are different, we may need to convert
                    if units[0] != units[1]:
                        if units[1] == '°F':
                            dataframe[column] = (dataframe[column] - 32)/1.8 
                            if column in ST_temp_exception:
                                average_to_zero(data, dataframe, column)
                        elif units[1] in NV_CONSTANTS.IP_TO_SI:
                            conversion_factor = NV_CONSTANTS.IP_TO_SI[units[1]]
                            dataframe[column] = dataframe[column] * conversion_factor
        output_meta_data['ses_version'] = "SI from IP"
        return data, output_meta_data
    else:
        NV_run.run_msg(gui, "Cannot convert SI file "+ output_meta_data['file_path'].name +" to SI")
        output_meta_data['ses_version'] == "SI"
        return data, output_meta_data

def average_to_zero(data, dataframe, column):
    if column == 'Average_Positive_Dry_Bulb':
        airflow_name = 'Average_Positive_Airflow'
    else:
        airflow_name = 'Average_Negative_Airflow'
    #Copy the average postive or negative airflow
    df_SA_airflow  = data['SA'][airflow_name]
    #If airflow is zero, make the value False.
    df_one_or_zero = df_SA_airflow.map(lambda x: True if (x !=0) else False)
    dataframe[column] = dataframe[column] * df_one_or_zero

if __name__ == "__main__":
    file_path_string = "C:/Users/msn/OneDrive - Never Gray/Software Development/Next-Vis/Python2021/normal.prn"
    visio_template = "C:/Users/msn/OneDrive - Never Gray/Software Development/Next-Vis/Python2021/sample012.vsdx"
    results_folder_str = "C:/Users/msn/OneDrive - Never Gray/Software Development/Next-Vis/Python2021"
    settings = {
        "ses_output_str": [file_path_string],
        "visio_template": visio_template,
        "results_folder_str": results_folder_str,
        "simtime": 9999.0,
        "version": "IP_TO_SI",
        "control": "First",
        "output": ["Excel"],
    }
    file_path = Path(settings['ses_output_str'][0])
    data, output_meta_data = nvp.parse_file(file_path)
    #TODO Transfer new data created in function
    new_data, new_output_meta_data = convert_ip_to_si(data, output_meta_data, gui="")
    import NV_excel_R01 as NV_excel
    NV_excel.create_excel(settings, data, output_meta_data)
