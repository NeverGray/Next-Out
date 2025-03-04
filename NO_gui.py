# Project Name: Next-Out
# Description: Launches Graphical User Interface to use Next-Out.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

import os
import pickle
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import NO_file_manager
import NO_process_multiple_files
import NO_run
from NO_constants import VERSION_NUMBER

class Start_Screen(tk.Tk):
    def __init__(self):
        super().__init__()
        # Initialization and settings
        p = "3"  # padding
        py = "3"  # vertical padding
        px = "3"
        self.title("Next-Out " + VERSION_NUMBER)
        style = ttk.Style()
        style.theme_use('winnative') #TODO Look at other styles
        # Call a function before closing the window.  See https://stackoverflow.com/questions/49220464/passing-arguments-in-tkinters-protocolwm-delete-window-function-on-python
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.ss = ttk.Frame(padding=p)  # start screen
        self.left_column = ttk.Frame(self.ss)
        # POST PROCESSING and Analysis Frames
        frame_post_processing = ttk.LabelFrame(
            self.ss, borderwidth=5, text="Post Processing", padding=p
        )
        frame_output_conversion = ttk.LabelFrame(
            self.left_column, borderwidth=5, text="Output Conversion", padding=p
        )
        frame_analysis = ttk.LabelFrame(
            self.left_column, borderwidth=5, text="Analysis*", padding=p
        )
        # Initialize all setting variables. This process makes saving, than loading settings easier.
        self.load_settings()
        # Post Processing frame options
        cb_excel = ttk.Checkbutton(
            frame_post_processing, text="Excel", variable=self.cbo_excel, onvalue="Excel", offvalue=""
        )
        cb_visio = ttk.Checkbutton(
            frame_post_processing,
            text="Visio",
            variable=self.cbo_visio,
            onvalue="Visio",
            offvalue="",
            command=self.update_post_processing_options,
        )
        cb_route = ttk.Checkbutton(
            frame_post_processing,
            text="Route Data",
            variable=self.cbo_route,
            onvalue="Route",
            offvalue="",
        )
        # Conversion frame options (radio buttons)
        rb_conversion_none = ttk.Radiobutton(
            frame_output_conversion, text="None", variable=self.conversion, value=""
        )
        rb_IP_to_SI = ttk.Radiobutton(
            frame_output_conversion, text="IP to SI", variable=self.conversion, value="IP_TO_SI"
        )
        rb_SI_to_IP = ttk.Radiobutton(
            frame_output_conversion, text="SI to IP", variable=self.conversion, value="SI_TO_IP"
        )
        # Analysis frame options
        cb_average = ttk.Checkbutton(
            frame_analysis,
            text="Staggered\nheadways\nmean, max, min",
            variable=self.cbo_average,
            onvalue="Average",
            offvalue="",
            command=self.update_post_processing_options,
        )
        self.cb_compare = ttk.Checkbutton(
            frame_analysis,
            text="Compare two\noutputs",
            variable=self.cbo_compare,
            onvalue="Compare",
            offvalue="",
            command=self.update_post_processing_options,
        )
        analysis_label = ttk.Label(
            frame_analysis, text="* Visio Template\nis disabled with\nAnalysis"
        )
        # POST PROCESSING grid
        cb_excel.grid(column=0, row=0, sticky="W", pady=py)
        cb_visio.grid(column=0, row=10, sticky="W", pady=py)
        cb_route.grid(column=0, row=15, sticky="W", pady=py)
        # Conversion grid
        rb_conversion_none.grid(column=0, row=10, sticky="W", pady=py)
        rb_IP_to_SI.grid(column=0, row=17, sticky="W", pady=py)
        rb_SI_to_IP.grid(column=0, row=18, sticky="W", pady=py)
        # Analysis grid
        self.cb_compare.grid(column=0, row=20, sticky="W", pady=py)
        cb_average.grid(column=0, row=30, sticky="W", pady=py)
        analysis_label.grid(column=0, row=40, sticky="W", pady=py)
        # SES Files to Process
        frame_ses_files = ttk.LabelFrame(
            self.ss, borderwidth=5, text="SES Files to Process", padding=p
        )
        frm_input_output = ttk.Frame(frame_ses_files)
        file_type = ttk.Label(frm_input_output, text="File Type to Process: ")
        rb_input_files = ttk.Radiobutton(
            frm_input_output,
            text="Input         ",
            variable=self.file_type,
            value="input_file",
            command=self.update_frame_ses_exe,
        )
        rb_output_files = ttk.Radiobutton(
            frm_input_output,
            text="Output         ",
            variable=self.file_type,
            value="output_file",
            command=self.update_frame_ses_exe,
        )
        rb_file = ttk.Radiobutton(
            frame_ses_files,
            text="",
            variable=self.ses,
            value="File",
            command=self.update_output_options,
        )
        rb_files = ttk.Radiobutton(
            frame_ses_files,
            text="",
            variable=self.ses,
            value="Files",
            command=self.update_output_options,
        )
        rb_folder = ttk.Radiobutton(
            frame_ses_files,
            text="",
            variable=self.ses,
            value="Folder",
            command=self.update_output_options,
        )
        self.btn_file = ttk.Button(frame_ses_files, text="One file", command=self.single_file)
        self.btn_files = ttk.Button(frame_ses_files, text="Many files", command=self.many_files)
        self.btn_folder = ttk.Button(frame_ses_files, text="Folder", command=self.ses_folder)
        self.ent_file = ttk.Entry(frame_ses_files, textvariable=self.path_file)
        self.ent_files = ttk.Entry(frame_ses_files, textvariable=self.path_files)
        self.ent_folder = ttk.Entry(frame_ses_files, textvariable=self.path_folder)
        # SES Files Frame creation
        r = 0
        frame_ses_files.grid(column=0, row=r)
        frm_input_output.grid(
            column=0, row=r, columnspan=3, sticky=["W"], pady=py, padx="0"
        )
        file_type.pack(side="left")
        rb_input_files.pack(side="left")
        rb_output_files.pack(side="left")
        r = 9
        rb_file.grid(column=0, row=r, sticky=["W"], pady=py, padx="0")
        self.btn_file.grid(column=1, row=r, sticky=["W"], pady=py, padx=px)
        self.ent_file.grid(
            column=2, row=r, columnspan=2, sticky=["EW"], pady=py, padx=px
        )
        r = 10
        rb_files.grid(column=0, row=r, sticky=["W"], pady=py, padx="0")
        self.btn_files.grid(column=1, row=r, sticky=["W"], pady=py, padx=px)
        self.ent_files.grid(
            column=2, row=r, columnspan=2, sticky=["EW"], pady=py, padx=px
        )
        r = 20
        rb_folder.grid(column=0, row=r, sticky=["W"], pady=py, padx="0")
        self.btn_folder.grid(column=1, row=r, sticky=["W"], pady=py, padx=px)
        self.ent_folder.grid(
            column=2, row=r, columnspan=2, sticky=["EW"], pady=py, padx=px
        )
        frame_ses_files.columnconfigure(2, weight=1)
        # SES Executable for input files
        self.frame_ses_exe = ttk.LabelFrame(
            self.ss,
            borderwidth=5,
            text="SES Executable (for input files)",
            padding=p,
        )
        self.btn_exe = ttk.Button(
            self.frame_ses_exe, text="SES EXE", command=lambda: self.single_file("EXE")
        )
        self.ent_file_exe = ttk.Entry(
            self.frame_ses_exe,
            textvariable=self.path_exe,
        )
        # SES Executable Frame Creation
        r = 0
        self.btn_exe.grid(column=0, row=r, sticky=["W"], pady=py, padx=px)
        self.ent_file_exe.grid(column=1, row=r, sticky=["WE"], columnspan=2)
        self.frame_ses_exe.columnconfigure(2, weight=1)

        # VISIO Template - Row 1
        self.frame_visio = ttk.LabelFrame(
            self.ss, borderwidth=5, text="Visio Template", padding=p
        )
        btn_visio = ttk.Button(
            self.frame_visio, text="Select", command=self.get_visio_file
        )
        ent_visio = ttk.Entry(self.frame_visio, textvariable=self.path_visio)
        # Visio Template - Row 2
        lbl_time = ttk.Label(self.frame_visio, text="Simulation Time: ")
        rb_end_time = ttk.Radiobutton(
            self.frame_visio, text="End", variable=self.rbo_time, value="end"
        )
        rb_user_time = ttk.Radiobutton(
            self.frame_visio, text="Specified", variable=self.rbo_time, value="user_time"
        )
        self.ent_user_time = ttk.Entry(self.frame_visio, textvariable=self.user_time)
        # Visio Template - Row 3
        self.cb_visio_open = ttk.Checkbutton(
            self.frame_visio,
            text="Open in Visio",
            variable=self.cbo_visio_open_option,
            onvalue="visio_open",
            offvalue="",
        )
        # Visio Template - Row 4
        lbl_image = ttk.Label(self.frame_visio, text="More Image Outputs: ")
        cb_pdf = ttk.Checkbutton(
            self.frame_visio,
            text="PDF",
            variable=self.cbo_pdf,
            onvalue="visio_2_pdf",
            offvalue="",
        )
        cb_png = ttk.Checkbutton(
            self.frame_visio,
            text="PNG",
            variable=self.cbo_png,
            onvalue="visio_2_png",
            offvalue="",
        )
        cb_svg = ttk.Checkbutton(
            self.frame_visio,
            text="SVG",
            variable=self.cbo_svg,
            onvalue="visio_2_svg",
            offvalue="",
        )
        # VISIO GRID
        r = 1  # Top Row
        btn_visio.grid(column=0, row=r, sticky="W", pady=py)
        ent_visio.grid(column=1, row=r, columnspan=3, sticky=["WE"], pady=py)
        r = 2
        lbl_time.grid(column=0, row=r, sticky="W", pady=py)
        rb_end_time.grid(column=1, row=r, sticky="W", pady=py)
        rb_user_time.grid(column=2, row=r, sticky="W", pady=py)
        self.ent_user_time.grid(column=3, row=r, sticky=["WE"], pady=py)
        self.frame_visio.columnconfigure(3, weight=1)
        r = 3
        self.cb_visio_open.grid(column=0, row=r, sticky="W", pady=py)
        r = 4
        lbl_image.grid(column=0, row=r, sticky="W", pady=py)
        cb_pdf.grid(column=1, row=r, sticky="W", pady=py)
        cb_png.grid(column=2, row=r, sticky="W", pady=py)
        cb_svg.grid(column=3, row=r, sticky="W", pady=py)
        # Results Folder widgets
        frame_results_folder = ttk.LabelFrame(
            self.ss, borderwidth=5, text="Folder to write results", padding=p
        )
        rb_ses = ttk.Radiobutton(
            frame_results_folder,
            text="Same as SES Input",
            variable=self.results_folder,
            value="ses output",
        )
        rb_selected = ttk.Radiobutton(
            frame_results_folder,
            text="Selected",
            variable=self.results_folder,
            value="selected",
        )
        btn_results_folder = ttk.Button(
            frame_results_folder, text="Select", command=self.get_results_folder
        )
        ent_results_folder = ttk.Entry(
            frame_results_folder, textvariable=self.path_results_folder
        )
        # OUTPUT FILE LOCATION grid
        rb_ses.grid(column=0, row=0, sticky="W")
        rb_selected.grid(column=2, row=0, sticky="EW")
        btn_results_folder.grid(column=0, row=1, sticky="W")
        ent_results_folder.grid(column=1, row=1, sticky="WE", columnspan=2)
        frame_results_folder.columnconfigure(2, weight=1)
        # RUN button
        frm_run = ttk.Frame(self.ss, padding=p, borderwidth=5)
        #self.btn_run = ttk.Button(frm_run, text="Run", command=self.run)
        self.btn_run = tk.Button(
            frm_run,
            text="Run",
            command=self.run,
            bg="#444444",  # Darker background color
            fg="white",    # White text
            activebackground="#222222",  # Darker shade when hovered
            activeforeground="white"     # Text color when hovered
        )
        self.btn_run.pack(expand=True, fill=tk.BOTH)
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
        '''# START SCREEN grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.ss.grid(column=0, row=0, sticky="EWNS")
        self.ss.columnconfigure(1, weight=1)
        self.ss.rowconfigure(5, weight=1)
        frame_output_conversion.pack(side="top", fill="x", pady=py, padx=px)
        frame_analysis.pack(side="top", fill="x", pady=py, padx=px)
        frame_post_processing.grid(column=0, row=0, sticky=["NSEW"], pady=py, padx=px)
        self.left_column.grid(row=1, column=0, rowspan=3, sticky=["NEW"])
        frame_ses_files.grid(column=1, row=0, sticky=["NSEW"], pady=py, padx=px)
        self.frame_ses_exe.grid(column=1, row=1, sticky=["NSEW"], pady=py, padx=px)
        self.frame_visio.grid(column=1, row=2, sticky=["WE"], pady=py, padx=px)
        self.frame_visio.grid(column=1, row=2, sticky=["WE"], pady=py, padx=px)
        frame_results_folder.grid(column=1, row=3, sticky=["WE"], pady=py, padx=px)
        frm_run.grid(column=0, columnspan=2, row=4, sticky=["WE"], pady=py, padx=px)
        frm_status.grid(
            column=0, row=6, columnspan=2, sticky=["WESN"], pady=py, padx=px
        )'''
        # START SCREEN grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.ss.grid(column=0, row=0, sticky="EWNS")
        self.ss.columnconfigure(0, weight=1)
        self.ss.rowconfigure(5, weight=1)

        frame_output_conversion.pack(side="top", fill="x", pady=py, padx=px)
        frame_analysis.pack(side="top", fill="x", pady=py, padx=px)

        # Switch left-hand and right-hand elements
        frame_post_processing.grid(column=1, row=0, sticky=["NSEW"], pady=py, padx=px)
        self.left_column.grid(row=1, column=1, rowspan=3, sticky=["NEW"])
        frame_ses_files.grid(column=0, row=0, sticky=["NSEW"], pady=py, padx=px)
        self.frame_ses_exe.grid(column=0, row=1, sticky=["NSEW"], pady=py, padx=px)
        self.frame_visio.grid(column=0, row=2, sticky=["WE"], pady=py, padx=px)
        frame_results_folder.grid(column=0, row=3, sticky=["WE"], pady=py, padx=px)

        frm_run.grid(column=0, columnspan=2, row=4, sticky=["WE"], pady=py, padx=px)
        frm_status.grid(column=0, row=6, columnspan=2, sticky=["WESN"], pady=py, padx=px)


    def load_settings(self, *args):
        # Define all variable and default values for  GUI
        self.screen_settings = {
            "self.cbo_visio": 'tk.StringVar(value="")',
            "self.cbo_excel": 'tk.StringVar(value="Excel")',
            "self.cbo_route": 'tk.StringVar(value="")',
            "self.conversion": 'tk.StringVar(value="")',
            "self.cbo_compare": 'tk.StringVar(value="")',
            "self.cbo_average": 'tk.StringVar(value="")',
            "self.file_type": 'tk.StringVar(value="output_file")',
            "self.ses": 'tk.StringVar(value="file")',  # Radio button for file, files, or folders
            "self.path_file": 'tk.StringVar(value="")',
            "self.path_files": 'tk.StringVar(value="")',
            "self.path_folder": 'tk.StringVar(value="")',
            "self.path_exe": 'tk.StringVar(value="")',  # Path for executable
            "self.path_visio": 'tk.StringVar(value="")',
            "self.rbo_time": 'tk.StringVar(value="end")',
            "self.user_time": 'tk.StringVar(value="")',
            "self.cbo_visio_open_option": 'tk.StringVar(value="")',
            "self.cbo_pdf": 'tk.StringVar(value="")',
            "self.cbo_png": 'tk.StringVar(value="")',
            "self.cbo_svg": 'tk.StringVar(value="")',
            "self.results_folder": 'tk.StringVar(value="ses output")',
            "self.path_results_folder": 'tk.StringVar(value="")',
            "self.iteration_worksheet_1": 'tk.StringVar(value="")',
            "self.iteration_worksheet_2": 'tk.StringVar(value="")',
        }
        self.directory_cache = {}
        for key, value in self.screen_settings.items():
            exec(f"{key} = {value}")
        try:
            settings_file_name = "NO_settings.ini"
            path_of_file = Path(settings_file_name)
            if path_of_file.is_file():
                try:
                    with open("NO_settings.ini", "rb") as f:
                        data_to_save = pickle.load(f)
                    self.directory_cache = data_to_save["directory_cache"]
                    load_gui_settings = data_to_save["gui_settings"]
                    for key, value in load_gui_settings.items():
                        if value != "":
                            exec(f'{key} = tk.StringVar(value="{value}")')
                except:
                    msg = f"Error loading {str(path_of_file)}."
        except:
            msg = "Error loading settings"
            messagebox.showinfo(message=msg)

    def get_visio_file(self, *args):
        try:
            file_type = "Visio"
            filename = filedialog.askopenfilename(
                title="Select Visio template file", filetypes=[("Visio", "*.vsdx")],
                initialdir=self.directory_cache.get(file_type, None),
            )
            self.path_visio.set(filename)
            self.cbo_visio.set("Visio")
            self.directory_cache[file_type] = os.path.dirname(filename)
        except ValueError:
            pass

    # Function to return a path of a single file: input, output, or executable
    def single_file(self, file_type=""):
        if file_type == "EXE":
            filetypes_suffix = [
                ("SES Executable", "*.EXE"),
            ]
            title_text = "Select SES Executable to process input files"
        elif self.file_type.get() == "input_file":
            file_type = self.file_type.get() 
            filetypes_suffix = [
                ("SES Input", ("*.INP", "*.SES")),
            ]
            title_text = "Select one SES input File"
        else:
            file_type = self.file_type.get() 
            filetypes_suffix = [
                ("SES Output", ("*.PRN", "*.OUT")),
            ]
            title_text = "Select one SES Output File"
        try:
            filename = filedialog.askopenfilename(
                title=title_text,
                filetypes=filetypes_suffix,
                #Use the previous directory for the specific file type
                initialdir=self.directory_cache.get(file_type, None),
            )
            #Save the directory selected for future selections
            self.directory_cache[file_type] = os.path.dirname(filename)
            if file_type == "EXE":
                self.path_exe.set(filename)
            else:
                self.path_file.set(filename)
                self.ses.set("File")
        except ValueError:
            pass

    def many_files(self, *args):  # Multiple files, not singular
        file_type = self.file_type.get()
        if file_type == "input_file":
            filetypes_suffix = [
                ("SES Input", ("*.INP", "*.SES")),
            ]
            title_text = "Select many SES input Files by holding Ctrl"
        else:
            filetypes_suffix = [
                ("SES Output", ("*.PRN", "*.OUT")),
            ]
            title_text = "Select many SES output Files by holding Ctrl"
        try:
            files = filedialog.askopenfilenames(
                title=title_text,
                filetypes=filetypes_suffix,
                #Use the previous directory for many files
                initialdir=self.directory_cache.get(file_type, None),
            )
            files_string = "; ".join(
                files,
            )
            self.path_files.set(files_string)
            self.ses.set("Files")
            #save the directory selected for many files for future selections
            self.directory_cache[file_type] = os.path.dirname(files[0])
        except ValueError:
            pass

    def ses_folder(self, *args):
        file_type = self.file_type.get()
        try:
            filename = filedialog.askdirectory(
                title="Select folder with SES output Files", mustexist=True,
                initialdir=self.directory_cache.get(file_type, None),
            )
            self.path_folder.set(filename)
            self.ses.set("Folder")
            self.directory_cache[file_type] = filename
        except ValueError:
            pass

    def get_results_folder(self, *args):
        file_type = "results"
        try:
            filename = filedialog.askdirectory(
                title="Select folder to write post-processing results", mustexist=True,
                initialdir=self.directory_cache.get(file_type, None),
            )
            self.path_results_folder.set(filename)
            self.results_folder.set("selected")
            self.directory_cache[file_type] = filename
        except ValueError:
            pass

    def ses_clear(self, *args):  # For clearing text boxses (not needed right now)
        try:
            self.output_files["state"] = "normal"
            self.output_files.delete("1.0", "end")
            self.output_files["state"] = "disabled"
        except ValueError:
            pass

    def run(self, *args):
        self.btn_run["text"] = "In-progress"
        self.btn_run["state"] = tk.DISABLED
        self.ss.update()
        pp_list = []
        pp_list.append(self.cbo_excel.get())
        pp_list.append(self.cbo_visio.get())
        pp_list.append(self.cbo_compare.get())
        pp_list.append(self.cbo_average.get())
        pp_list.append(self.cbo_route.get())
        pp_list.append(self.cbo_pdf.get())
        pp_list.append(self.cbo_png.get())
        pp_list.append(self.cbo_svg.get())
        pp_list.append(self.cbo_visio_open_option.get())
        # interation_worksheets = []
        # interation_worksheets.append(self.iteration_worksheet_1.get())
        # interation_worksheets.append(self.iteration_worksheet_2)
        try:
            self.get_ses_file_str()
        except:
            error_msg = "ERROR finding input or output file locations"
            self.gui_text(error_msg)
        try:
            self.get_results_folder_str()
        except:
            error_msg = "ERROR with selected result folder"
            self.gui_text(error_msg)
            self.results_folder_str = (
                None  # Default to putting results in the same folder as the SES output
            )
        self.settings = {
            "ses_output_str": self.ses_output_str,
            "visio_template": self.path_visio.get(),
            "results_folder_str": self.results_folder_str,
            "simtime": -1,  # Updated in validation
            "conversion": self.conversion.get(),  # Determine what type of conversion is needed
            "output": pp_list,
            "file_type": self.file_type.get(),
            "path_exe": self.path_exe.get(),
        }

        if self.validation(self.settings):
            try:
                # If only performing one individual simulation
                if (
                    len(self.settings["ses_output_str"]) == 1
                    or ("Average" in pp_list)
                    or ("Compare" in pp_list)
                    ):
                    NO_run.single_sim(self.settings, gui=self)
                    self.gui_text("Post processing completed.\n")
                else:
                    # Launch process and monitor files when using multiple files
                    self.gui_text(
                        "Processing multiple files, openning monitor window."
                    )
                    # Turn off opening visio for multiple files
                    if "visio_open" in self.settings["output"]:
                        self.settings["output"].remove("visio_open")
                        self.cbo_visio_open_option.set("")
                    self.open_monitor_gui()
            except:
                self.gui_text(
                    "Error after validation, before single_sim or multiple_sim. \n"
                )
        else:
            self.gui_text("Error with Validation of Settings")
        self.btn_run["state"] = tk.NORMAL
        self.btn_run["text"] = "Run"

    # Function to check that settings allows a successful simulation and post-processing
    def validation(self, settings):
        valid = True
        msg = ""
        # Check if settings are valid for Visio Files
        if "Visio" in settings["output"]:
            if settings["visio_template"] == "":
                msg = msg + "No Visio Template File is Specified. \n"
                valid = False
            #Check the time input is a number
            if self.rbo_time.get() == "user_time":
                time = self.user_time.get()
                if time.isnumeric():
                    self.settings["simtime"] = time
                else:
                    msg = msg + "Specify a number for Visio's Simulation Time\n"
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
        if self.file_type.get() == "input_file":
            exe_path_string = self.path_exe.get()
            if exe_path_string == "":
                msg = msg + "Select an SES executable to perform simulations.\n"
                valid = False
            elif not os.path.exists(self.path_exe.get()):
                msg = msg + "Select an SES executable to perform simulations.\n"
                valid = False
        if not valid:
            messagebox.showinfo(title="Error with settings", message=msg)
        return valid

    def gui_text(self, status):
        self.txt_status["state"] = tk.NORMAL
        self.txt_status.insert("end", status + "\n")
        self.txt_status.see(tk.END)
        self.txt_status["state"] = tk.DISABLED
        self.ss.update()

    def get_ses_file_str(self, *args):
        if self.ses.get() == "File":
            self.ses_output_str = []
            self.ses_output_str.append(self.path_file.get())
        elif self.ses.get() == "Folder":
            self.ses_output_str = []
            folder_path = self.path_folder.get()
            # Select all input files or output files
            if self.file_type.get() == "input_file":
                suffix = [".INP", ".SES"]
            else:
                suffix = [".OUT", ".PRN"]
            self.ses_output_str = NO_file_manager.find_all_files(
                extensions=suffix, pathway=folder_path, with_path=True
            )
        else:
            self.ses_output_str = []
            files_string = self.path_files.get()
            self.ses_output_str = files_string.split("; ")

    def get_results_folder_str(self, *args):
        option = self.results_folder.get()
        if option == "selected":
            self.results_folder_str = self.path_results_folder.get()
        else:  # Default is same as SES output. Use empty string
            self.results_folder_str = None

    def update_output_options(self, *args):
        option = self.ses.get()
        if option == "File":
            self.cb_visio_open["state"] = tk.NORMAL
        else:
            self.cb_visio_open["state"] = tk.DISABLED
            self.cbo_visio_open = tk.StringVar(value="")

    def update_post_processing_options(self, *args):
        if (
            self.cbo_average.get() == ""
            and self.cbo_compare.get() == ""
            and self.cbo_visio.get() == "Visio"
        ):
            visio_state = "enable"
        else:
            visio_state = "disable"
        # Disable all items in a frame: https://www.tutorialspoint.com/how-to-gray-out-disable-a-tkinter-frame
        self.configure_widget_state(self.frame_visio, visio_state)

    def update_frame_ses_exe(self, *args):
        multiple_files_state = "enable"
        if self.file_type.get() == "input_file":
            ses_exe_state = "enable"
        else:
            ses_exe_state = "disable"
        self.configure_widget_state(self.frame_ses_exe, ses_exe_state)
        # Update file buttons
        self.btn_files.configure(state=multiple_files_state)
        self.btn_folder.configure(state=multiple_files_state)
        self.ent_files.configure(state=multiple_files_state)
        self.ent_folder.configure(state=multiple_files_state)
        # Old cold to erase entries
        # self.path_file.set("")
        # self.path_files.set("")

    # Change the state of the elements in a frame
    def configure_widget_state(self, widget, state):
        widget_class = widget.winfo_class()
        if widget_class in (
            "TRadiobutton",
            "TEntry",
            "TCheckbutton",
            "TButton",
            "TLabel",
        ):
            widget.configure(state=state)
        elif "frame" in widget_class.lower():
            for child in widget.winfo_children():
                self.configure_widget_state(child, state)

    #Offer to save the current settings before exiting the program
    def on_closing(self):
        title_on_closing = "Quite Next Vis?"
        msg_1 = "Click 'Yes' to quit and save the most recent settings.\n"
        msg_2 = "Click 'No' to exit without saving.\n"
        msg_3 = "Click 'Cancel' to return back to Next-Out\n"
        msg_all = msg_1 + msg_2 + msg_3
        answer = messagebox.askyesnocancel(title=title_on_closing, message=msg_all)
        if answer is None:
            return
        elif answer:
            try:
                GUI_settings_2_save = {}
                for key, value in self.screen_settings.items():
                    exec(f'GUI_settings_2_save["{key}"]= {key}.get()')
                data_to_save = {}
                data_to_save = {"gui_settings":GUI_settings_2_save, "directory_cache":self.directory_cache}
                with open("NO_settings.ini", "wb") as f:
                    pickle.dump(data_to_save, f)
                self.destroy()
            except:
                self.destroy()
        else:
            self.destroy()

    #TODO Check if this can be deleted.
    def text_update(self, text):
        self.gui_text(text)
        self.ss.update

    def open_monitor_gui(self):
        manager = NO_process_multiple_files.Manager_Class()
        window = NO_process_multiple_files.Monitor_GUI(self, manager, self.settings)
        window.focus_force()
        window.grab_set()

def launch_window():
    start_screen = Start_Screen()
    start_screen.mainloop()


if __name__ == "__main__":
    launch_window()
