
from pathlib import Path

import pandas as pd

import NV_CONSTANTS
import NO_parser as nvp
import NO_run


def convert_output_units(conversion_setting, data, output_meta_data, gui=""):
    if conversion_is_possible(conversion_setting, output_meta_data):
        ST_temp_exception = ['Average_Positive_Dry_Bulb','Average_Negative_Dry_Bulb']
        if conversion_setting=="IP_TO_SI":
            unit_msg = "SI"
        else:
            unit_msg = "IP"
        msg = f"Converting data from {output_meta_data['file_path'].name} to {unit_msg}"
        NO_run.run_msg(gui, msg)
        #Iterate through all the dataframs in the data dictionary
        for dataframe in data.values():
            #Iterate through all columns (not indexes)
            for column in dataframe.columns:
                #Check if the column name is in column_units
                if column in NV_CONSTANTS.COLUMN_UNITS:
                    #Get the list of the units of the column for IP and SI
                    units = NV_CONSTANTS.COLUMN_UNITS[column]
                    si_unit = units[0]
                    ip_unit = units[1]
                    #A conversion is needed if the two units for the column are different, 
                    if si_unit != ip_unit:
                        if conversion_setting=="IP_TO_SI":
                            #Temperature requires a special formula
                            if ip_unit == NV_CONSTANTS.DEGREE_SYMBOL + 'F':
                                dataframe[column] = (dataframe[column] - 32)/1.8 
                                #For average temps columns (ST_temp_exception), some zero values should not be converted.
                                if column in ST_temp_exception:
                                    average_to_zero(data, dataframe, column)
                            #all other units can use a simple conversion factor
                            elif ip_unit in NV_CONSTANTS.IP_TO_SI:
                                conversion_factor = NV_CONSTANTS.IP_TO_SI[ip_unit]
                                dataframe[column] = dataframe[column] * conversion_factor
                        elif conversion_setting=="SI_TO_IP":
                            #Temperature requires a special formula
                            if si_unit == NV_CONSTANTS.DEGREE_SYMBOL + 'C':
                                dataframe[column] = (dataframe[column]*1.8) + 32
                                #For average temps columns (ST_temp_exception), some zero values should not be converted.
                                if column in ST_temp_exception:
                                    average_to_zero(data, dataframe, column)
                            #all other units can use a simple conversion factor
                            elif ip_unit in NV_CONSTANTS.IP_TO_SI:
                                conversion_factor = NV_CONSTANTS.IP_TO_SI[ip_unit]
                                dataframe[column] = dataframe[column] / conversion_factor    
        #Change output_meta_data to show the file has been converted.
        if conversion_setting=="IP_TO_SI":
            output_meta_data['ses_version'] = "SI from IP"
        elif conversion_setting=="SI_TO_IP":
            output_meta_data['ses_version'] = "IP from SI"
    else:
        NO_run.run_msg(gui, "Cannot convert file "+ output_meta_data['file_path'].name +" because it is already in that unit.")
    return data, output_meta_data

def conversion_is_possible(conversion_setting, output_meta_data):
    if conversion_setting=="IP_TO_SI" and output_meta_data['ses_version']=="IP":
        is_possible = True
    elif conversion_setting=="SI_TO_IP" and output_meta_data['ses_version']=="SI":
        is_possible = True
    else:
        is_possible = False
    return is_possible

def average_to_zero(data, dataframe, column):
    #Change an invalid average value back to zero
    if column == 'Average_Positive_Dry_Bulb':
        airflow_name = 'Average_Positive_Airflow'
    else: #column is 'Average_Negative_Dry_bulb'
        airflow_name = 'Average_Negative_Airflow'
    #Copy the average postive or negative airflow to a temporary data frame
    df_SA_airflow  = data['SA'][airflow_name]
    #If average airflow is zero, make the value False.
    df_one_or_zero = df_SA_airflow != 0
    #Multiply by truth table. If average airflow is false, average temperature becomes zero
    dataframe[column] = dataframe[column] * df_one_or_zero

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
    file_path = Path(settings['ses_output_str'][0])
    data, output_meta_data = nvp.parse_file(file_path)
    #TODO Transfer new data created in function
    conversion_setting = settings["conversion"]
    new_data, new_output_meta_data = convert_output_units(conversion_setting, data, output_meta_data, gui="")
    import NO_Excel_R01 as NV_excel
    NV_excel.create_excel(settings, data, output_meta_data)
