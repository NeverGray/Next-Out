# Project Name: Next-Out
# Description: Tools for working with files in Next Out.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

import gzip
import logging
import pickle
import pandas as pd
from pathlib import Path

def output_from_input(file_path_string, path_exe):
    file_path = Path(file_path_string)
    # TODO Select suffix based on SES type
    try:
        if "SES41.exe".lower() in path_exe.lower():
            extension = ".PRN"
        else:
            extension = ".OUT"
        new_file_path = file_path.with_suffix(extension)
        return new_file_path
    except:
        logging.debug("Error in 'output_from_input' when converting file strings")
        return file_path

def get_results_path2(settings, output_meta_data, suffix):
    output_file_path = Path(output_meta_data['file_path'])
    output_stem = output_file_path.stem
    if output_meta_data['ses_version'] == "SI from IP":
        results_name_str = output_stem + '_SI' + suffix
    elif output_meta_data['ses_version'] == "IP from SI":
        results_name_str = output_stem + '_IP' + suffix
    else:
        results_name_str = output_stem + suffix
    results_folder_str = settings.get("results_folder_str")
    if results_folder_str is None:
        results_parent = output_file_path.parent
    else:
        results_parent = Path(results_folder_str)
    results_path = results_parent/Path(results_name_str)
    return results_path

#Get variable from parsed file. Save information as zipped (compressed) pickle file
def create_no_file(data, output_meta_data, settings=None):
    # TODO Consider how to implement the result folder. 
    # Define the output file path with the pickle that is zipped suffix
    if settings is None:
        no_file_path = output_meta_data['file_path'].with_suffix('.no')
    else:
        no_file_path = get_results_path2(settings, output_meta_data, '.no')
    
    # Save the data and output_meta_data to the file with compression
    with gzip.open(no_file_path, 'wb') as file:
        no_file = {'data': data, 'output_meta_data': output_meta_data}
        pickle.dump(no_file, file)
    
    logging.info(f"{no_file_path} created.")

# Read the data and output_meta_data from the no file, a zipped pickle file
def read_no_file(no_file_path):
    with gzip.open(no_file_path, 'rb') as file:
        no_file = pickle.load(file)
    data = no_file['data']
    output_meta_data = no_file['output_meta_data']
    #Add names to the Dataframes. Names do not appear when reading in a file.
    for key, df in data.items():
        if isinstance(df, pd.DataFrame):  # Ensure the value is a DataFrame
            df.name = key  # Set the name attribute of the DataFrame
    return data, output_meta_data

if __name__ == "__main__":
    import NO_parser
    directory_str = "C:\\simulations\\test\\"
    output_file_name = "test.out"
    file_path = Path(directory_str + output_file_name)
    data, output_meta_data = NO_parser.parse_file(file_path)
    create_no_file(data, output_meta_data)