# Project Name: Next-Out
# Description: Return a list of all files in a folder with specific extensions
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

import logging
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