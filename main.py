# Project Name: Next-Out
# Description: Perform SES simulations. Post-processes and analyze output data.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

import argparse
import ast
import multiprocessing #Needed for compiled (*.exe) version

import NO_GUI_main
import NO_GUI_command_line
import next_in

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run the simulation or open the GUI.')
    parser.add_argument('--settings', type=str, help='Settings as a Python dictionary string')

    # Parse the command-line arguments
    args = parser.parse_args()

    if args.settings:
        # Convert the settings string to a dictionary using ast.literal_eval
        settings = ast.literal_eval(args.settings)
        # Call the function with the parsed settings
        #TODO Test iteration. Worked with previous version, before conversions.
        file_type = settings.get("file_type")
        if file_type == "iteration" or file_type == "iteration_then_simulate":
            next_in.create_iterations_from_next_in(settings)
        elif file_type == "next_in":
            next_in_path = settings.get['next_in_path']
            input_file_path = settings.get['ses_output_str'][0]
            ses_version = settings.get['ses_version']
            next_in.create_input_files(next_in_path, input_file_path, ses_version)
            print("Created input file ", input_file_path)
        else:
            app = NO_GUI_command_line.command_line_screen(settings)
            app.mainloop()
    else:
        # Launch the GUI
        NO_GUI_main.launch_window()  # Assuming this is your GUI launch function

if __name__ == "__main__":
    multiprocessing.freeze_support() #May be needed for compiled (*.exe) version
    main()
    r'''
    Use the text below in a terminal to test the command line options.
    Create iteration input files only.
    python main.py --settings "{'file_type': 'iteration', 'next_in_path': 'c:/simulations/test/test.xlsm', 'iteration_path': 'c:/simulations/test', 'ses_version': 'SI'}"

    Create iteration input files, then confirm to simulate and post-process them.
    python main.py --settings "{'file_type': 'iteration_then_simulate', 'next_in_path': 'c:/simulations/test/test.xlsm', 'iteration_path': 'c:/simulations/test', 'ses_version': 'SI', 'output': ['Excel', 'H5_file'], 'path_exe': 'C:/Simulations/_Exe/SESV6_32.exe', 'simtime': -1, 'visio_template': '', 'output_conversion': ''}"

    Use the text below to run from the executable
    "C:\Simulations\_exe\Next-Out.exe" --settings "{'output_conversion': '', 'file_type': 'output_file', 'output': [' '], 'path_exe': '', 'results_folder_str': None, 'ses_output_str': ['C:/Simulations/Test/test2.inp'], 'simtime': -1, 'visio_template': ''}"
    
    Testing Conversions
    python main.py --settings "{'file_type': 'next_in', 'next_in_path': 'c:/simulations/test/test.xlsm', 'input_file_path': 'c:/simulations/test/test2si.inp', 'ses_version':'IP_TO_SI', 'ses_output_str': ['C:/Simulations/Test/test2.inp']}"
    "C:\Simulations\_exe\Next-Out 3A.exe --settings "{'file_type': 'next_in', 'next_in_path': 'c:/simulations/test/test.xlsm', 'input_file_path': 'c:/simulations/test/test2si.inp', 'ses_version':'IP_TO_SI', 'ses_output_str': ['C:/Simulations/Test/test2.inp']}"
    '''