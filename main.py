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
import NO_run

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
        NO_run.single_sim(settings)
    else:
        # Launch the GUI
        NO_gui.launch_window()  # Assuming this is your GUI launch function

if __name__ == "__main__":
    main()