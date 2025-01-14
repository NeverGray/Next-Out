# Project Name: Next-Out
# Description: Perform SES simuilations. Post-processes and analyze output data.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

#import multiprocessing #TODO Testing if necessary
import argparse
import ast
import ctypes
import sys

import NO_gui
import NO_command_line

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
        app = NO_command_line.command_line_screen(settings)
        app.mainloop()
    else:
        # Launch the GUI
        NO_gui.launch_window()  # Assuming this is your GUI launch function

if __name__ == "__main__":
    main()
    '''
    Use the text below in a terminal to test the command line options.
    python main.py --settings "{'conversion': '', 'file_type': 'input_file', 'output': ['Excel', 'Visio', '', '', '', '', '', '', ''], 'path_exe': 'C:/Simulations/_Exe/SESV6_32.exe', 'results_folder_str': None, 'ses_output_str': ['C:/simulations/test/test.inp'], 'simtime': -1, 'visio_template': 'C:/Simulations/Test/Test Template.vsdx'}"
    '''