# Project Name: Next-Out
# Description: Perform SES simuilations. Post-processes and analyze output data.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

import multiprocessing 
import NO_gui

def main():
    NO_gui.launch_window()

if __name__ == "__main__":
    multiprocessing.freeze_support() #TODO Maybe necessary for TKinter, second window
    main()