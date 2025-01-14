# Project Name: Next-Out
# Description: Launches status window when program starts from the command line with argurements
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

import os
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

import NO_process_multiple_files
import NO_run
from NO_constants import VERSION_NUMBER

class command_line_screen(tk.Tk):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        # Initialization and settings
        p = "3"  # padding
        py = "3"  # vertical padding
        px = "3"
        self.title("Next-Out " + VERSION_NUMBER +" Command Line Monitor ")
        style = ttk.Style()
        style.theme_use('winnative') #TODO Look at other styles
        self.ss = ttk.Frame(padding=p)  # start screen
        self.left_column = ttk.Frame(self.ss)
        # STATUS SCREEN
        frm_status = ttk.LabelFrame(self.ss, borderwidth=5, text="Status", padding=p)
        self.txt_status = tk.Text(
            frm_status,
            width=30,
            height=5,
            state=tk.DISABLED,
            wrap="none",
        )
        self.ys_status = ttk.Scrollbar(
            frm_status, orient="vertical", command=self.txt_status.yview
        )
        self.txt_status["yscrollcommand"] = self.ys_status.set
        self.txt_status.pack(side=tk.LEFT, expand=tk.TRUE, fill=tk.BOTH)
        self.ys_status.pack(side=tk.RIGHT, fill="y")

        # START SCREEN grid configuration
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Configure ss grid to expand
        self.ss.grid(column=0, row=0, sticky="nsew")
        self.ss.columnconfigure(0, weight=1)  # Ensure the first column expands
        self.ss.rowconfigure(6, weight=1)  # Ensure the row containing frm_status expands

        frm_status.grid(
            column=0, row=6, columnspan=2, sticky="nsew", pady=py, padx=px
        )
        self.minsize(550, 385) 
        self.ss.update()
        self.run()
        self.ss.update()

    def run(self, *args):
        if self.validation(self.settings):
            pp_list = self.settings["output"]
            try:
                # If only performing one individual simulation
                if (
                    len(self.settings["ses_output_str"]) == 1
                    or ("Average" in pp_list)
                    or ("Compare" in pp_list)
                    ):
                    NO_run.single_sim(self.settings, gui=self)
                    self.gui_text("Post processing completed. You can close this window.\n")
                else:
                    # Launch process and monitor files when using multiple files
                    self.gui_text(
                        "Processing multiple files, openning monitor window."
                    )
                    # Turn off opening visio for multiple files
                    if "visio_open" in self.settings["output"]:
                        self.settings["output"].remove("visio_open")
                        self.cbo_visio_open_option.set("")
                    #TODO Need to test if multiple files work from command line.
                    self.open_monitor_gui()
                    self.gui_text("Post processing completed.\n")
            except:
                self.gui_text(
                    "Error after validation, before single_sim or multiple_sim. \n"
                )
        else:
            self.gui_text("Error with Validation of Settings")

    # Function to check that settings allows a successful simulation and post-processing
    #TODO Change Validation in NO_Gui to a standalone function that can be called here. 
    def validation(self, settings):
        try:
            valid = True
            msg = ""
            # Check if settings are valid for Visio Files
            if "Visio" in settings["output"]:
                if settings["visio_template"] == "":
                    msg = msg + "No Visio Template File is Specified. \n"
                    valid = False
            if not isinstance(settings["simtime"], (int, float)):
                msg = msg + "Simulation Time is not a number. \n"
                valid = False
            if len(settings["ses_output_str"]) == 0:
                msg = (
                    msg + "Files to process. Check if input or output files are present.\n"
                )
                valid = False
            # Check if the folder for post-processing output exists
            if not self.settings["results_folder_str"] is None:
                results_folder_path = Path(self.settings["results_folder_str"])
                if not results_folder_path.is_dir():
                    msg = msg + "Folder to write results does not exist.\n"
                    valid = False
            # If using input file, check the executable exists
            if self.settings["file_type"] == "input_file":
                exe_path_string = settings["path_exe"]
                if exe_path_string == "":
                    msg = msg + "Select an SES executable to perform simulations.\n"
                    valid = False
                elif not os.path.exists(exe_path_string):
                    msg = msg + "Select an SES executable to perform simulations.\n"
                    valid = False
            if not valid:
                messagebox.showinfo(title="Error with settings", message=msg)
            return valid
        except:
            msg = "Error with Validation"
            messagebox.showinfo(message=msg)
    


    def gui_text(self, status):
        self.txt_status["state"] = tk.NORMAL
        self.txt_status.insert("end", status + "\n")
        self.txt_status.see(tk.END)
        self.txt_status["state"] = tk.DISABLED
        self.ss.update()

    def open_monitor_gui(self):
        manager = NO_process_multiple_files.Manager_Class()
        window = NO_process_multiple_files.Monitor_GUI(self, manager, self.settings)
        window.focus_force()
        window.grab_set()

if __name__ == "__main__":
    directory_str = "C:\\simulations\\test\\"
    input_file_name = "test.inp"
    settings = {
        'conversion': '',
        'file_type': 'input_file',
        'output': ['Excel', 'Visio', '', '', '', '', '', '', ''],
        'path_exe': 'C:/Simulations/_Exe/SESV6_32.exe',
        'results_folder_str': None,
        'ses_output_str': [directory_str + input_file_name],
        'simtime': -1,
        'visio_template': 'C:/Simulations/Test/Test Template.vsdx'}
    app = command_line_screen(settings)
    app.mainloop()
    print("app.mainloop finished")

