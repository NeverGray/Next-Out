# Project Name: Next-Out
# Description: Create file with output data from SES simulations
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

import gzip
import logging
import pickle
import pandas as pd
from pathlib import Path

#Get variable from parsed file. Save information as zipped (compressed) pickle file
def create_no_file(data, output_meta_data):
    # TODO Consider how to implement the result folder. 
    # Define the output file path with the pickle that is zipped suffix
    no_file_path = output_meta_data['file_path'].with_suffix('.no')
    
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