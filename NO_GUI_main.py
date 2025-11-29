# Project Name: Next-Out
# Description: Launches Graphical User Interface to use Next-Out.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

import os
import tomllib
import tomli_w
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import NO_GUI_multifile_monitor
import NO_run
import NO_compare
import NO_summary
from NO_constants import VERSION_NUMBER

class Start_Screen(tk.Tk):
    def __init__(self):
        super().__init__()
        # Initialization and settings
        p = "3"  # padding
        py = "3"  # vertical padding
        px = "3"
        self.title("Next-Out " + VERSION_NUMBER)
        
        # Set window icon
        try:
            from pathlib import Path
            import sys
            # Get the directory where the script/executable is located
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                icon_path = Path(sys._MEIPASS) / 'NO_Icon.ico'
            else:
                # Running as script
                icon_path = Path(__file__).parent / 'NO_Icon.ico'
            
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception as e:
            # If icon can't be loaded, just continue with default
            pass
        
        style = ttk.Style()
        style.theme_use('winnative')

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
        self.frame_analysis = ttk.LabelFrame(
            self.left_column, borderwidth=5, text="Analysis", padding=p
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
            command=self.update_output_options,
        )
        # Summary checkbox
        cb_summary = ttk.Checkbutton(
            frame_post_processing, text="Summary*", variable=self.cbo_summary, onvalue="Summary", offvalue="",
            command=self.update_output_options
        )
        cb_route = ttk.Checkbutton(
            frame_post_processing,
            text="Route Data",
            variable=self.cbo_route,
            onvalue="Route",
            offvalue="",
        )
        self.cb_no_file = ttk.Checkbutton(
            frame_post_processing,
            text="H5 File",
            variable=self.cbo_no_file,
            onvalue="H5_file",
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
            self.frame_analysis,
            text="Staggered\nheadways\nmean, max, min*",
            variable=self.cbo_average,
            onvalue="Average",
            offvalue="",
            command=self.update_output_options
        )
        self.cb_compare = ttk.Checkbutton(
            self.frame_analysis,
            text="Compare two\noutputs",
            variable=self.cbo_compare,
            onvalue="Compare",
            offvalue="",
            command=self.average_off
        )
        # Label for H5 requirement (will be placed outside frame)
        h5_requirement_label = ttk.Label(
            self.left_column, text="* Requires H5 Files")
        # POST PROCESSING grid
        cb_excel.grid(column=0, row=0, sticky="W", pady=py)
        cb_visio.grid(column=0, row=10, sticky="W", pady=py)
        cb_route.grid(column=0, row=15, sticky="W", pady=py)
        self.cb_no_file.grid(column=0, row=20, sticky="W", pady=py)
        cb_summary.grid(column=0, row=25, sticky="W", pady=py)
        # Conversion grid
        rb_conversion_none.grid(column=0, row=10, sticky="W", pady=py)
        rb_IP_to_SI.grid(column=0, row=17, sticky="W", pady=py)
        rb_SI_to_IP.grid(column=0, row=18, sticky="W", pady=py)
        # Analysis grid
        self.cb_compare.grid(column=0, row=20, sticky="W", pady=py)
        cb_average.grid(column=0, row=30, sticky="W", pady=py)
        # SES Files to Process
        frame_ses_files = ttk.LabelFrame(
            self.ss, borderwidth=5, text="SES Files to Process", padding=p
        )
        frm_input_output = ttk.Frame(frame_ses_files)
        file_type = ttk.Label(frm_input_output, text="File Type to Process: ")
        rb_input_files = ttk.Radiobutton(
            frm_input_output,
            text="Input     ",
            variable=self.file_type,
            value="input_file",
            command=self.update_frame_ses_exe,
        )
        rb_output_files = ttk.Radiobutton(
            frm_input_output,
            text="Output     ",
            variable=self.file_type,
            value="output_file",
            command=self.update_frame_ses_exe,
        )
        rb_no_file_files = ttk.Radiobutton(
            frm_input_output,
            text="H5 File     ",
            variable=self.file_type,
            value="H5_file",
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
        self.btn_file = ttk.Button(frame_ses_files, text="One file", command=self.select_files)
        self.btn_files = ttk.Button(frame_ses_files, text="Many files", command=lambda: self.select_files(multiple=True))
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
        rb_no_file_files.pack(side="left")
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
            self.frame_ses_exe, text="SES EXE", command=lambda: self.select_files("EXE")
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
            self.frame_visio, text="Select", command=lambda: self.select_files("Visio")
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
        lbl_image = ttk.Label(self.frame_visio, text="Convert Visio to: ")
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
        # Visio Template - Row 5
        lbl_conversion_note = ttk.Label(
            self.frame_visio, 
            text="Note: Conversions are time-consuming"
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
        r = 5
        lbl_conversion_note.grid(column=0, row=r, columnspan=4, sticky="W", pady=py)
        
        # SUMMARY OPTIONS Frame
        self.frame_summary = ttk.LabelFrame(
            self.ss, borderwidth=5, text="Summary Options (Requires H5 File)", padding=p
        )
        self.cb_fire = ttk.Checkbutton(
            self.frame_summary, 
            text="Fire Segment", 
            variable=self.cbo_fire_segment, 
            onvalue=True, 
            offvalue=False
        )
        lbl_segments = ttk.Label(
            self.frame_summary, 
            text="Segment numbers (comma-separated):"
        )
        self.ent_segment_numbers = ttk.Entry(
            self.frame_summary, 
            textvariable=self.segment_numbers_str
        )
        
        # Summary Options Grid
        r = 0
        self.cb_fire.grid(column=0, row=r, sticky="W", pady=py, padx=px)
        r = 1
        lbl_segments.grid(column=0, row=r, sticky="W", pady=py, padx=px)
        r = 2
        self.ent_segment_numbers.grid(column=0, row=r, columnspan=4, sticky=["WE"], pady=py, padx=px)
        self.frame_summary.columnconfigure(0, weight=1)
        
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
        
        # START SCREEN grid
        self.columnconfigure(0, weight=1)  # Allow horizontal expansion
        self.rowconfigure(0, weight=1)    # Allow vertical expansion for the main frame
        self.ss.grid(column=0, row=0, sticky="EWNS")
        self.ss.columnconfigure(0, weight=1)

        # Ensure all rows except the Status row do not expand
        self.ss.rowconfigure(0, weight=0)  # Post Processing
        self.ss.rowconfigure(1, weight=0)  # SES Files
        self.ss.rowconfigure(2, weight=0)  # Visio Template
        self.ss.rowconfigure(3, weight=0)  # Summary Options
        self.ss.rowconfigure(4, weight=0)  # Run Button

        # Ensure the Status row expands
        self.ss.rowconfigure(5, weight=1)  # Status window row

        # Place the Status window at the bottom and allow it to expand
        frm_status.grid(column=0, row=5, columnspan=2, sticky="WENS", pady=py, padx=px)

        # Ensure the Run button row does not expand
        frm_run.grid(column=0, columnspan=2, row=4, sticky="WE", pady=py, padx=px)

        frame_output_conversion.pack(side="top", fill="x", pady=py, padx=px)
        self.frame_analysis.pack(side="top", fill="x", pady=py, padx=px)
        h5_requirement_label.pack(side="top", fill="x", pady=py, padx=px)

        # Switch left-hand and right-hand elements
        frame_post_processing.grid(column=1, row=0, sticky=["NSEW"], pady=py, padx=px)
        self.left_column.grid(row=1, column=1, rowspan=3, sticky=["NEW"])
        frame_ses_files.grid(column=0, row=0, sticky=["NSEW"], pady=py, padx=px)
        self.frame_ses_exe.grid(column=0, row=1, sticky=["NSEW"], pady=py, padx=px)
        self.frame_visio.grid(column=0, row=2, sticky=["WE"], pady=py, padx=px)
        self.frame_summary.grid(column=0, row=3, sticky=["WE"], pady=py, padx=px)

        # Set minimum window size
        self.minsize(550, 790)
        
        #Update the GUI to show the current settings
        self.update_output_options()
        self.update_frame_ses_exe()

    def load_settings(self, *args):
        # Define all variable and default values for  GUI
        self.screen_settings = {
            "self.cbo_visio": 'tk.StringVar(value="")',
            "self.cbo_excel": 'tk.StringVar(value="")',
            "self.cbo_route": 'tk.StringVar(value="")',
            "self.cbo_no_file": 'tk.StringVar(value="")',
            "self.cbo_summary": 'tk.StringVar(value="")',  # Add this line
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
            "self.cbo_fire_segment": 'tk.BooleanVar(value=False)',
            "self.segment_numbers_str": 'tk.StringVar(value="")'
        }
        self.directory_cache = {}
        self.summary_settings = {
            'lookup_fire_data':False,
            'segments_2_lookup':[]
        }
        for key, value in self.screen_settings.items():
            exec(f"{key} = {value}")
        try:
            settings_file_name = "NO_settings.toml"
            path_of_file = Path(settings_file_name)
            if path_of_file.is_file():
                try:
                    with open(settings_file_name, "rb") as f:
                        data_to_save = tomllib.load(f)
                    self.directory_cache = data_to_save.get("directory_cache", {})
                    self.summary_settings = data_to_save.get("summary_settings", self.summary_settings)
                    load_gui_settings = data_to_save.get("gui_settings", {})
                    for key, value in load_gui_settings.items():
                        if value != "":
                            # Handle boolean variables
                            if key == "self.cbo_fire_segment":
                                exec(f'{key} = tk.BooleanVar(value={value})')
                            else:
                                exec(f'{key} = tk.StringVar(value="{value}")')
                    
                    # Load summary settings into GUI fields
                    if self.summary_settings.get('lookup_fire_data', False):
                        self.cbo_fire_segment.set(True)
                    if 'segments_2_lookup' in self.summary_settings:
                        segment_numbers = self.summary_settings['segments_2_lookup']
                        numbers_str = ', '.join(map(str, segment_numbers))
                        self.segment_numbers_str.set(numbers_str)
                    
                    # Load and apply window geometry if it exists
                    window_geometry = data_to_save.get("window_geometry", None)
                    if window_geometry:
                        self.geometry(window_geometry)
                        
                except Exception as e:
                    msg = f"Error loading {str(path_of_file)}: {str(e)}"
        except Exception as e:
            msg = f"Error loading settings: {str(e)}"
            messagebox.showinfo(message=msg)

    # Function to return a paths of a single or multiple files
    def select_files(self, file_type="", multiple=False):
        file_type_config = {
            "input_file": {
                "filetypes_suffix": [("SES Input", ("*.INP", "*.SES"))],
                "title_text": "Select SES Input File(s)",
                "set_path": lambda filenames: self.path_file.set(filenames if not multiple else "; ".join(filenames)),
            },
            "output_file": {
                "filetypes_suffix": [("SES Output", ("*.PRN", "*.OUT"))],
                "title_text": "Select SES Output File(s)",
                "set_path": lambda filenames: self.path_file.set(filenames if not multiple else "; ".join(filenames)),
            },
            "H5_file": {
                "filetypes_suffix": [("H5 Files", "*.H5")],
                "title_text": "Select H5 File(s)",
                "set_path": lambda filenames: self.path_file.set(filenames if not multiple else "; ".join(filenames)),
            },
            "EXE": {
                "filetypes_suffix": [("SES Executable", "*.EXE")],
                "title_text": "Select SES Executable",
                "set_path": lambda filenames: self.path_exe.set(filenames),
            },
            "Visio": {
                "filetypes_suffix": [("Visio", "*.vsdx")],
                "title_text": "Select Visio Template File",
                "set_path": lambda filenames: self.path_visio.set(filenames),
            },
        }

        # Determine the file type configuration
        file_type_key = file_type if file_type else self.file_type.get()
        config = file_type_config.get(file_type_key, {})

        try:
            if multiple:
                filenames = filedialog.askopenfilenames(
                    title=config.get("title_text", "Select files"),
                    filetypes=config.get("filetypes_suffix", []),
                    initialdir=self.directory_cache.get(file_type_key, None),
                )
                if filenames:
                    # Save the directory selected for future selections
                    self.directory_cache[file_type_key] = os.path.dirname(filenames[0])
                    self.path_files.set("; ".join(filenames))
                    self.ses.set("Files")
            else:
                filename = filedialog.askopenfilename(
                    title=config.get("title_text", "Select a file"),
                    filetypes=config.get("filetypes_suffix", []),
                    initialdir=self.directory_cache.get(file_type_key, None),
                )
                if filename:
                    # Save the directory selected for future selections
                    self.directory_cache[file_type_key] = os.path.dirname(filename)
                    config["set_path"](filename)
                    # If selecting a single input, output, or no file, set the ses variable to "File"
                    if file_type_key in ["input_file", "output_file", "H5_file"]:
                        self.ses.set("File") #
        except ValueError:
            pass

    def ses_folder(self, *args):
        file_type = self.file_type.get()
        try:
            filename = filedialog.askdirectory(
                title="Select folder with files to process", mustexist=True,
                initialdir=self.directory_cache.get(file_type, None),
            )
            self.path_folder.set(filename)
            self.ses.set("Folder")
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
        #Update options using logic in GUI
        self.update_output_options
        self.btn_run["text"] = "In-progress"
        self.btn_run["state"] = tk.DISABLED
        self.ss.update()
        pp_list = []
        pp_list.append(self.cbo_excel.get())
        pp_list.append(self.cbo_visio.get())
        pp_list.append(self.cbo_summary.get())
        pp_list.append(self.cbo_route.get())
        pp_list.append(self.cbo_compare.get())
        pp_list.append(self.cbo_average.get())
        if self.file_type.get() != "H5_file":
            pp_list.append(self.cbo_no_file.get())
        pp_list.append(self.cbo_pdf.get())
        pp_list.append(self.cbo_png.get())
        pp_list.append(self.cbo_svg.get())
        pp_list = [item for item in pp_list if item]  # Remove empty strings
        # "Open Visio" should only be added if it is enabled by visio_open_off()
        if str(self.cb_visio_open.cget("state"))== "normal":
            pp_list.append(self.cbo_visio_open_option.get())
        try:
            self.get_files_2_process_in_str()
        except:
            error_msg = "ERROR finding input, output, or H5 Files"
            self.gui_text(error_msg)
        # Get summary settings from GUI
        lookup_fire_data = self.cbo_fire_segment.get()
        segments_2_lookup = []
        numbers_text = self.segment_numbers_str.get().strip()
        if numbers_text:
            try:
                segments_2_lookup = [int(num.strip()) for num in numbers_text.split(',')]
            except ValueError:
                self.gui_text("Warning: Invalid segment numbers format. Using empty list.\n")
        
        self.settings = {
            "ses_output_str": self.ses_output_str,
            "visio_template": self.path_visio.get(),
            "simtime": -1,
            "conversion": self.conversion.get(),
            "output": pp_list,
            "file_type": self.file_type.get(),
            "path_exe": self.path_exe.get(),
            "lookup_fire_data": lookup_fire_data,
            "segments_2_lookup": segments_2_lookup
        }
        if self.validation(self.settings):
            try:
                # If only performing one individual simulation
                if len(self.settings["ses_output_str"]) == 1 or "Compare" in self.settings["output"]:
                    if "Compare" in self.settings["output"] and len(self.settings["ses_output_str"]) != 2:
                        messagebox.showinfo(title="Error", message="Need exactly 2 files to compare outputs.")
                        self.gui_text("Error: Need exactly 2 files to compare outputs.\n")
                        self.btn_run["state"] = tk.NORMAL
                        self.btn_run["text"] = "Run"
                        return
                    else:
                        #TODO Check len(self.settings["ses_output_str"]) == 2 for Compare Case
                        NO_run.single_sim(self.settings, gui=self)
                        self.gui_text("Post processing completed.\n")
                elif "Compare" in self.settings["output"]:
                    NO_compare.compare_outputs(self.settings, gui=self)
                elif self.parallel_process_files:
                    # Launch process and monitor files when using multiple files
                    self.gui_text(
                        "Processing multiple files, openning monitor window."
                    )
                    self.open_monitor_gui()
                elif "Summary" in self.settings["output"]:
                    try:
                        NO_summary.create_excel_summary(self.settings, gui=self)
                    except Exception as e:
                        error_msg = f"Error with summary creation: {str(e)}\n"
                        self.gui_text(error_msg)
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
                msg + "No files to process. Check if input or output files are present.\n"
            )
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
        #Check if extensions for files to process are valid for settings
        valid_extensions = {
            "input_file": [".INP", ".SES"],
            "output_file": [".OUT", ".PRN"],
            "H5_file": [".H5"],
        }
        # Get the selected file type
        file_type = self.file_type.get()
        if file_type == "H5_file" and settings['output'] == ['Summary']:
            self.parallel_process_files = False
        else:
            self.parallel_process_files = True  # Changed from self.parallel_processing_needed
        # Get the valid extensions for the selected file type
        allowed_extensions = valid_extensions.get(file_type, [])

        # Check each file in ses_output_str
        invalid_files = []
        for file_path in self.settings["ses_output_str"]:
            # Check if the file has a valid extension
            if not any(file_path.upper().endswith(ext) for ext in allowed_extensions):
                invalid_files.append(file_path)
        # If there are invalid files, show an error message
        if invalid_files:
            msg_about_files = "The following files have invalid extensions for the selected file type:\n"
            msg_about_files += "\n".join(invalid_files)
            messagebox.showerror("Invalid File Types", msg_about_files)
            valid = False
            msg = msg + "Invalid file extensions to progress.\n"
        if "Average" in settings["output"]:
            if len(settings["ses_output_str"]) < 2:
                msg = msg + "Need at least 2 files to for average analysis.\n"
                valid = False
            if "H5_file" not in settings["output"]:
                settings["output"].append("H5_file")
        if "Compare" in settings["output"] and len(settings["ses_output_str"]) != 2:
            msg = msg + "Need excatly 2 files to compare files.\n"
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

    #Get the string to process files
    def get_files_2_process_in_str(self, *args):
        file_type_suffix = {
            "input_file": [".INP", ".SES"],
            "output_file": [".OUT", ".PRN"],
            "H5_file": [".H5"],
        }
        self.ses_output_str = []

        if self.ses.get() == "File":
            self.ses_output_str.append(self.path_file.get())
        elif self.ses.get() == "Folder":
            folder_path = self.path_folder.get()
            file_type = self.file_type.get()
            suffixes = file_type_suffix.get(file_type, [])
            all_files = []
            with os.scandir(folder_path) as it:
                for entry in it:  # For each item in the folder
                    if entry.is_file() and entry.name.upper().endswith(tuple(suffix.upper() for suffix in suffixes)):
                        all_files.append(entry.path)
            if all_files:
                self.ses_output_str = all_files
            else:
                self.ses_output_str = []
                msg = "No files found in folder to process.\n"
                self.gui_text(msg)
        else:  # If the option is "Files" (not "File" or "Folder")
            files_string = self.path_files.get()
            self.ses_output_str = files_string.split("; ")

    def update_output_options(self, *args):
        #TODO Update when "Open Visio can be selected or not"
        option = self.ses.get()
        if option == "File":
            self.cb_visio_open["state"] = tk.NORMAL
            self.cbo_average.set("")
            self.cbo_compare.set("")
            analysis_state = "disabled"
        else:
            self.cb_visio_open["state"] = tk.DISABLED
            self.cbo_visio_open = tk.StringVar(value="")
            analysis_state = "enabled"
        self.configure_widget_state(self.frame_analysis, analysis_state)
        if self.cbo_visio.get() == "Visio":
            visio_state = "enable"
        else:
            visio_state = "disable"
        # Disable all items in a frame: https://www.tutorialspoint.com/how-to-gray-out-disable-a-tkinter-frame
        self.configure_widget_state(self.frame_visio, visio_state)
        # Enable/disable summary frame
        if self.cbo_summary.get() == "Summary":
            summary_state = "enable"
            self.cbo_no_file.set("H5_file")  # Check "H5_file" when Summary is enabled
        else:
            summary_state = "disable"
        self.configure_widget_state(self.frame_summary, summary_state)
        if self.cbo_average.get() == "Average":
            self.cbo_compare.set("")  # Uncheck "Average"
            self.cbo_no_file.set("H5_file")  # Check "H5_file"
        self.visio_open_off()   
       
    def average_off(self, *args):
        if self.cbo_compare.get() == "Compare":
            self.cbo_average.set("")  # Uncheck "Average"
        self.visio_open_off()  

    #Adjust if Visio_Open is enabled or disabled based on the current settings
    def visio_open_off(self, *args):
        visio_frame_state = self.cb_visio_open.cget("state")
        if visio_frame_state == 'enable':
            if self.ses.get() == "File":
                self.cb_visio_open.configure(state=tk.NORMAL)
            else:
                self.cb_visio_open.configure(state=tk.DISABLED)

    #TODO Evaluate if this function is needed anymore or can be combined into with update_output_options
    def update_frame_ses_exe(self, *args):
        multiple_files_state = "enable"
        if self.file_type.get() == "input_file":
            ses_exe_state = "enable"
        else:
            ses_exe_state = "disable"
        if self.file_type.get() == "H5_file":
            self.cb_no_file.configure(state=tk.DISABLED)
            #Conversions are only performed on input or output files
            self.conversion.set("")
        else:
            self.cb_no_file.configure(state=tk.NORMAL)
        self.configure_widget_state(self.frame_ses_exe, ses_exe_state)
        # Update file buttons
        self.btn_files.configure(state=multiple_files_state)
        self.btn_folder.configure(state=multiple_files_state)
        self.ent_files.configure(state=multiple_files_state)
        self.ent_folder.configure(state=multiple_files_state)

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
    


    def on_closing(self):
        title_on_closing = "Quit Next Vis?"
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
                
                # Update summary_settings from GUI
                summary_settings = {
                    'lookup_fire_data': self.cbo_fire_segment.get(),
                    'segments_2_lookup': []
                }
                numbers_text = self.segment_numbers_str.get().strip()
                if numbers_text:
                    try:
                        summary_settings['segments_2_lookup'] = [int(num.strip()) for num in numbers_text.split(',')]
                    except ValueError:
                        pass  # Keep empty list if invalid
                
                # Save window geometry (size and position)
                window_geometry = self.geometry()
                
                data_to_save = {}
                data_to_save = {
                    "gui_settings":GUI_settings_2_save, 
                    "summary_settings":summary_settings,
                    "directory_cache":self.directory_cache,
                    "window_geometry":window_geometry}
                with open("NO_settings.toml", "wb") as f:
                    tomli_w.dump(data_to_save, f)
                self.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
                self.destroy()
        else:
            self.destroy()

    def open_monitor_gui(self):
        manager = NO_GUI_multifile_monitor.Manager_Class()
        window = NO_GUI_multifile_monitor.Monitor_GUI(self, manager, self.settings)
        window.focus_force()
        window.grab_set()

def launch_window():
    start_screen = Start_Screen()
    start_screen.mainloop()


if __name__ == "__main__":
    launch_window()
