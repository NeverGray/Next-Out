import base64
import datetime
import os
import pickle
import tkinter as tk
from multiprocessing import Queue
from pathlib import Path
from sys import exit as system_exit
from tkinter import filedialog, messagebox, ttk

import keygen
import NV_file_manager as nfm
import NV_run as nvr
from NV_CONSTANTS import VERSION_NUMBER
from NV_icon5 import Icon

# add requirement for program to be legit to run
class start_screen:
    def __init__(self, root, license_info):
        # Initialization and settings
        p = "5"  # padding
        py = "5"  # vertical padding
        px = "5"
        root.title("Next-Vis " + VERSION_NUMBER)
        # Call a function before closing the window.  See https://stackoverflow.com/questions/49220464/passing-arguments-in-tkinters-protocolwm-delete-window-function-on-python
        root.protocol("WM_DELETE_WINDOW", lambda arg=root: self.on_closing(arg))
        try:
            with open('tmp.ico','wb') as tmp:
                tmp.write(base64.b64decode(Icon().img))
            root.iconbitmap('tmp.ico')
            os.remove('tmp.ico')
        except:
            icon_value = False
        # root.iconbitmap('icon4.ico')
        # TODO Replace Icon in title bar with NV icon (icon4.ico)
        # root.attributes('-toolwindow', 'True')
        self.ss = ttk.Frame(root, padding=p)  # start screen
        self.license_info = license_info
        # POST PROCESSING and Analysis Frames
        frm_pp = ttk.LabelFrame(
            self.ss, borderwidth=5, text="Post Processing", padding=p
        )
        frm_analysis = ttk.LabelFrame(
            self.ss, borderwidth=5, text="Analysis", padding=p
        )
        #Initialize all setting variables. This process makes saving, than loading settings easier.
        self.load_settings()
        cb_excel = ttk.Checkbutton(
            frm_pp, text="Excel", variable=self.cbo_excel, onvalue="Excel", offvalue=""
        )
        cb_visio = ttk.Checkbutton(
            frm_pp, text="Visio", variable=self.cbo_visio, onvalue="Visio", offvalue="",
            command=self.update_post_processing_options
        )
        cb_ip_to_si = ttk.Checkbutton(
            frm_pp, text="Convert\nIP to SI", variable=self.cbo_ip_to_si, onvalue="IP_TO_SI", offvalue=""
        )
        cb_route = ttk.Checkbutton(
            frm_pp, text="Route Data", variable=self.cbo_route, onvalue="Route", offvalue=""
        )
        cb_average = ttk.Checkbutton(
            frm_analysis, text="Staggered\nheadways\nmean, max, min", variable=self.cbo_average, 
            onvalue="Average", offvalue="", command=self.update_post_processing_options
        )
        self.cb_compare = ttk.Checkbutton(
            frm_analysis,
            text="Compare two\noutputs",
            variable=self.cbo_compare,
            onvalue="Compare",
            offvalue="",
            command=self.update_post_processing_options
        )
        # POST PROCESSING grid
        cb_excel.grid(column=0, row=0, sticky='W', pady=py)
        cb_visio.grid(column=0, row=10, sticky='W', pady=py)
        cb_ip_to_si.grid(column=0, row=15, sticky='W', pady=py)
        cb_route.grid(column=0, row=17, sticky='W', pady=py)
        # Analysis grid
        self.cb_compare.grid(column=0, row=20, sticky='W', pady=py)
        cb_average.grid(column=0, row=30, sticky='W', pady=py)
        # SES Files to Process
        frm_ses = ttk.LabelFrame(
            self.ss, borderwidth=5, text="SES Files to Process", padding=p
        )
        file_type = ttk.Label(frm_ses, text="Type:")
        rb_input_files = ttk.Radiobutton(frm_ses, text="Input", variable=self.file_type, value="input_file", command=self.update_ses_exe)
        rb_output_files = ttk.Radiobutton(frm_ses, text="Output", variable=self.file_type, value="output_file", command=self.update_ses_exe)
        rb_file = ttk.Radiobutton(frm_ses, text="", variable=self.ses, value="File", command=self.update_output_options)
        rb_files = ttk.Radiobutton(frm_ses, text="", variable=self.ses, value="Files", command=self.update_output_options)
        rb_folder = ttk.Radiobutton(frm_ses, text="", variable=self.ses, value="Folder", command=self.update_output_options)
        self.btn_file = ttk.Button(frm_ses, text="One file", command=self.single_file)
        self.btn_files = ttk.Button(frm_ses, text="Many files", command=self.ses_files)
        self.btn_folder = ttk.Button(frm_ses, text="Folder", command=self.ses_folder)
        ent_file = ttk.Entry(frm_ses, textvariable=self.path_file)
        ent_files = ttk.Entry(frm_ses, textvariable=self.path_files)
        ent_folder = ttk.Entry(frm_ses, textvariable=self.path_folder)
        # SES Files Frame creation
        r = 0
        frm_ses.grid(column=0, row=r)
        file_type.grid(column=0,row=r)
        rb_input_files.grid(column=2, row=r, sticky=['W'], pady=py, padx="0")
        rb_output_files.grid(column=3, row=r, sticky=['W'], pady=py, padx="0")
        r = 9
        rb_file.grid(column=0, row=r, sticky=['W'], pady=py, padx="0")
        self.btn_file.grid(column=1, row=r, sticky=['W'], pady=py, padx=px)
        ent_file.grid(column=2, row=r, columnspan=2, sticky=['EW'], pady=py, padx=px)
        r = 10
        rb_files.grid(column=0, row=r, sticky=['W'], pady=py, padx="0")
        self.btn_files.grid(column=1, row=r, sticky=['W'], pady=py, padx=px)
        ent_files.grid(column=2, row=r, columnspan=2, sticky=['EW'], pady=py, padx=px)
        r = 20
        rb_folder.grid(column=0, row=r, sticky=['W'], pady=py, padx="0")
        self.btn_folder.grid(column=1, row=r, sticky=['W'], pady=py, padx=px)
        ent_folder.grid(column=2, row=r, columnspan=2, sticky=['EW'], pady=py, padx=px)
        frm_ses.columnconfigure(2, weight=1)
        # SES Executable for input files
        self.frm_ses_exe = ttk.LabelFrame(
            self.ss, borderwidth=5, text="SES Executable (for input files)", padding=p
        )
        self.btn_exe = ttk.Button(self.frm_ses_exe, text="SES EXE", command=lambda: self.single_file('EXE'))
        ent_file_exe = ttk.Entry(self.frm_ses_exe, textvariable=self.path_exe, )
        # SES Executable Frame Creation
        r = 0
        self.btn_exe.grid(column=0, row=r, sticky=['W'], pady=py, padx=px)
        ent_file_exe.grid(column=1, row=r, sticky=['WE'], columnspan=2)
        self.frm_ses_exe.columnconfigure(2,weight=1)
        # VISIO Template - Row 1
        self.frm_visio = ttk.LabelFrame(
            self.ss, borderwidth=5, text="Visio Template", padding=p
        )
        btn_visio = ttk.Button(self.frm_visio, text="Select", command=self.get_visio_file)
        ent_visio = ttk.Entry(self.frm_visio, textvariable=self.path_visio)
        # Visio Template - Row 2
        lbl_time = ttk.Label(self.frm_visio, text="Simulation Time: ")
        rb_end_time = ttk.Radiobutton(
            self.frm_visio, text="End", variable=self.rbo_time, value="end"
        )
        rb_user_time = ttk.Radiobutton(
            self.frm_visio, text="Specified", variable=self.rbo_time, value="user_time"
        )
        self.ent_user_time = ttk.Entry(self.frm_visio, textvariable=self.user_time)
        # Visio Template - Row 3
        self.cb_visio_open = ttk.Checkbutton(
            self.frm_visio, text="Open in Visio", variable=self.cbo_visio_open_option, onvalue="visio_open", offvalue=""
        )
        # Visio Template - Row 4
        lbl_image = ttk.Label(self.frm_visio, text="More Image Outputs: ")
        cb_pdf = ttk.Checkbutton(
            self.frm_visio, text="PDF", variable=self.cbo_pdf, onvalue="visio_2_pdf", offvalue=""
        )
        cb_png = ttk.Checkbutton(
            self.frm_visio, text="PNG", variable=self.cbo_png, onvalue="visio_2_png", offvalue=""
        )
        cb_svg = ttk.Checkbutton(
            self.frm_visio, text="SVG", variable=self.cbo_svg, onvalue="visio_2_svg", offvalue=""
        )
        # VISIO GRID
        r = 1  # Top Row
        btn_visio.grid(column=0, row=r, sticky='W', pady=py)
        ent_visio.grid(column=1, row=r, columnspan=3, sticky=['WE'], pady=py)
        r = 2
        lbl_time.grid(column=0, row=r, sticky='W', pady=py)
        rb_end_time.grid(column=1, row=r, sticky='W', pady=py)
        rb_user_time.grid(column=2, row=r, sticky='W', pady=py)
        self.ent_user_time.grid(column=3, row=r, sticky=['WE'], pady=py)
        self.frm_visio.columnconfigure(3, weight=1)
        r = 4
        lbl_image.grid(column=0, row=r, sticky='W', pady=py)
        cb_pdf.grid(column=1, row=r, sticky='W', pady=py)
        cb_png.grid(column=2, row=r, sticky='W', pady=py)
        cb_svg.grid(column=3, row=r, sticky='W', pady=py)
        r = 3
        self.cb_visio_open.grid(column=0, row=r, sticky='W', pady=py)
        # Results Folder widgets
        frm_results_folder = ttk.LabelFrame(self.ss, borderwidth=5, text="Folder to write results", padding=p)
        rb_ses = ttk.Radiobutton(frm_results_folder, text="Same as SES Output", variable=self.results_folder, value="ses output")
        rb_visio = ttk.Radiobutton(frm_results_folder,text="Same as Visio Template",variable=self.results_folder,value="visio template")
        rb_selected = ttk.Radiobutton(frm_results_folder,text="Selected",variable=self.results_folder, value="selected")
        btn_results_folder = ttk.Button(frm_results_folder, text="Select", command=self.get_results_folder)
        ent_results_folder = ttk.Entry(frm_results_folder, textvariable=self.path_results_folder)
        # OUTPUT FILE LOCATION grid
        rb_ses.grid(column=0, row=0, sticky='W')
        rb_visio.grid(column=1, row=0, sticky='W')
        rb_selected.grid(column=2, row=0, sticky='EW')
        btn_results_folder.grid(column=0, row=1, sticky='W')
        ent_results_folder.grid(column=1, row=1, sticky='WE', columnspan=2)
        frm_results_folder.columnconfigure(2, weight=1)
        # RUN button
        frm_run = ttk.Frame(self.ss, padding=p, borderwidth=5)
        self.btn_run = ttk.Button(frm_run, text="Run", command=self.run)
        self.btn_run.pack(expand=True, fill=tk.BOTH)
        # STATUS SCREEN
        frm_status = ttk.LabelFrame(self.ss, borderwidth=5, text="Status", padding=p)
        self.txt_status = tk.Text(
            frm_status, width=30, height=5, state=tk.DISABLED, wrap="none",
        )
        self.ys_status = ttk.Scrollbar(
            frm_status, orient="vertical", command=self.txt_status.yview
        )
        self.txt_status["yscrollcommand"] = self.ys_status.set
        self.txt_status.pack(side=tk.LEFT, expand=tk.TRUE, fill=tk.BOTH)
        self.ys_status.pack(side=tk.RIGHT, fill='y')
        # START SCREEN grid
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        # root.rowconfigure(0, weight=1)
        self.ss.grid(column=0, row=0, sticky="EWNS")
        self.ss.columnconfigure(1, weight=1)
        self.ss.rowconfigure(5, weight=1)
        frm_pp.grid(column=0, row=0, rowspan=2, sticky=['NSEW'], pady=py, padx=px)
        frm_analysis.grid(column=0, row=2, rowspan=2, sticky=['NSEW'], pady=py, padx=px)
        frm_ses.grid(column=1, row=0, sticky=['NSEW'], pady=py, padx=px)
        self.frm_ses_exe.grid(column=1,row=1, sticky=['NSEW'], pady=py, padx=px)
        self.frm_visio.grid(column=1, row=2, sticky=['WE'], pady=py, padx=px)
        frm_results_folder.grid(column=1, row=3, sticky=['WE'], pady=py, padx=px)
        frm_run.grid(column=0, columnspan=2, row=4, sticky=['WE'], pady=py, padx=px)
        frm_status.grid(
            column=0, row=5, columnspan=2, sticky=['WESN'], pady=py, padx=px
        )
        root.minsize(550, 385)  # Measured using paint.net
        self.update_post_processing_options()
        self.display_validation_info()
        self.ss.update()

    def load_settings(self, *args):
        # Define all variable and default vvalues for  GUI
        self.screen_settings = {
            'self.cbo_visio': 'tk.StringVar(value="")',
            'self.cbo_excel':  'tk.StringVar(value="Excel")',
            'self.cbo_ip_to_si':  'tk.StringVar(value="")',
            'self.cbo_compare':  'tk.StringVar(value="")',
            'self.cbo_average':  'tk.StringVar(value="")',
            'self.cbo_route':  'tk.StringVar(value="")',
            'self.file_type':  'tk.StringVar(value="output_file")',
            'self.ses':  'tk.StringVar(value="file")', #Radio button for file, files, or folders
            'self.path_file':  'tk.StringVar(value="")',
            'self.path_files':  'tk.StringVar(value="")',
            'self.path_folder':  'tk.StringVar(value="")',
            'self.path_exe':  'tk.StringVar(value="")', #Path for executable
            'self.path_visio':  'tk.StringVar(value="")',
            'self.rbo_time':  'tk.StringVar(value="end")',
            'self.user_time':  'tk.StringVar(value="")',
            'self.cbo_visio_open_option':  'tk.StringVar(value="")',
            'self.cbo_pdf': 'tk.StringVar(value="")',
            'self.cbo_png':  'tk.StringVar(value="")',
            'self.cbo_svg':  'tk.StringVar(value="")',
            'self.results_folder':  'tk.StringVar(value="ses output")',
            'self.path_results_folder':  'tk.StringVar(value="")'
        }
        for key, value in self.screen_settings.items():
            exec(f'{key} = {value}') 
        try:
            settings_file_name = "nv_settings.ini"
            path_of_file = Path(settings_file_name)
            if path_of_file.is_file():
                try:
                    with open("nv_settings.ini","rb") as f:
                        settings_2_load = pickle.load(f)
                    for key, value in settings_2_load.items():
                        if value != '':
                            exec(f'{key} = tk.StringVar(value="{value}")')
                except:
                    msg = f"Error loading {str(path_of_file)}."
        except:
            msg = "Error loading settings"
            messagebox.showinfo(message=msg)

    def display_validation_info(self, *args):
        msg_line=[]
        msg_line.append(f'Click OKAY to accept "Next-Vis License Agrement"')
        msg_line.append("Otherwise, click Cancel to exit")
        if self.license_info['type'] == 'Floating':
            validation_code, license_id, validation_info = keygen.validate_license_key_with_fingerprint(
                self.license_info["floating_key"], self.license_info['machine_fingerprint'])
            floats_available = validation_info['data']['attributes']['maxMachines']
            floats_in_use = validation_info['data']['relationships']['machines']['meta']['count']
            authorized_organization = self.license_info["Authorized_Organization"]
            expiry = validation_info['data']['attributes']['expiry'][:10]
            msg_line.append(f"\n{floats_in_use} of {floats_available} floating licenses in use for {authorized_organization}.")
            msg_line.append(f'License Expires on {expiry}.')
        else:
            expiry = str(self.license_info['expiry'])
            msg_line.append(f"\nOffline License Expires on {expiry}.")
        msg = "\n".join(msg_line)
        answer = messagebox.askokcancel(title='Use and accept license', message=msg, icon ='info')
        if not answer:
            system_exit("User did not accept license agreement")

    def check_floating_license(self, *args):
        active_license = keygen.ping_heartbeat_for_machine(
        self.license_info["machine_fingerprint"], self.license_info["floating_key"])
        if active_license:
            return True
        else:
            messagebox.showinfo(
                message='No licenses is available or there is no internet connection.\nProgram is going to shut down')
            system_exit("The license is no longer active")

    def get_visio_file(self, *args):
        try:
            filename = filedialog.askopenfilename(
                title="Select Visio template file", filetypes=[("Visio", "*.vsdx")]
            )
            self.path_visio.set(filename)
            self.cbo_visio.set("Visio")
        except ValueError:
            pass

    # Function to return a path of a single file: input, output, or executable
    def single_file(self, file_type='SES'):
        if file_type == 'EXE':
            filetypes_suffix = [("SES Executable", "*.EXE"),]
            title_text = "Select SES Executable to process input files"
        elif self.file_type.get() == 'input_file':
            filetypes_suffix = [("SES Input", ("*.INP", "*.SES")),]
            title_text = "Select one SES input File"
        else:
            filetypes_suffix = [("SES Output", ("*.PRN", "*.OUT")),]
            title_text ="Select one SES Output File"
        try:
            filename = filedialog.askopenfilename(
                title = title_text,
                filetypes=filetypes_suffix,
            )
            if file_type == 'EXE':
                self.path_exe.set(filename)
            else:
                self.path_file.set(filename)
                self.ses.set("File")
        except ValueError:
            pass

    def ses_files(self, *args): #Multiple files, not singular
        if self.file_type.get() == 'input_file':
            filetypes_suffix=[("SES Input", ("*.INP", "*.SES")),]
            title_text ="Select many SES input Files by holding Ctrl"
        else:
            filetypes_suffix=[("SES Output", ("*.PRN", "*.OUT")),]
            title_text ="Select many SES output Files by holding Ctrl"
        try:
            files = filedialog.askopenfilenames(
                title = title_text,
                filetypes = filetypes_suffix,
            )
            files_string = '; '.join(files,)
            self.path_files.set(files_string)
            self.ses.set("Files")
        except ValueError:
            pass

    def ses_folder(self, *args):
        try:
            filename = filedialog.askdirectory(
                title = "Select folder with SES output Files",
                mustexist = True
            )
            self.path_folder.set(filename)
            self.ses.set("Folder")
        except ValueError:
            pass

    def get_results_folder(self, *args):
        try:
            filename = filedialog.askdirectory(
                title = "Select folder to write post-processing results",
                mustexist = True
            )
            self.path_results_folder.set(filename)
            self.results_folder.set("selected")
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
        try:
            self.get_ses_file_str()
        except:
            error_msg = "ERROR finding iput or output file locations"
            self.gui_text(error_msg)
        try:
            self.get_results_folder_str()
        except:
            error_msg = "ERROR with selected result folder"
            self.gui_text(error_msg)
        self.settings = {
            "ses_output_str": self.ses_output_str,
            "visio_template": self.path_visio.get(),
            "results_folder_str": self.results_folder_str,
            "simtime": -1, #Updated in validation
            "version": self.cbo_ip_to_si.get(),
            "control": "First",
            "output": pp_list,
            "file_type": self.file_type.get(),
            "path_exe": self.path_exe.get()
        }
        if self.validation(self.settings):
            # Check validity of license
            if self.valid_license():
                try:
                    if (self.ses.get() == "File") or ("Average" in pp_list) or ("Compare" in pp_list):
                        nvr.single_sim(self.settings, gui=self)
                    else:
                        if 'visio_open' in self.settings['output']:
                            self.settings['output'].remove('visio_open')
                            self.cbo_visio_open_option.set("")
                        nvr.multiple_sim(self.settings, gui=self)
                    self.gui_text("Post processing completed.")
                except:
                    self.gui_text(
                        "Error after validation, before single_sim or multiple_sim"
                    )
            else:
                self.gui_text("Error Checking validity of license.")
        else:
            self.gui_text("Error with Validation of Settings")
        self.btn_run["state"] = tk.NORMAL
        self.btn_run["text"] = "Run"

    #Function to check that settings allows a successful simulation and post-processing
    def validation(self, settings):
        valid = True
        msg = ""
        # Check if settings are valid for Visio Files
        if "Visio" in settings["output"]:
            if settings["visio_template"] == "":
                msg = msg + "No Visio Template File is Specified. \n"
                valid = False
            if self.rbo_time.get() == "user_time":
                time = self.user_time.get()
                if time.isnumeric():
                    self.settings["simtime"] = time
                else:
                    msg = msg + "Specify a number for Visio's Simulation Time\n"
                    valid = False
        if settings["ses_output_str"] == "":
            msg = msg + "No SES output file or folders are specified.\n"
            valid = False
        if not self.settings["results_folder_str"] is None:
            results_folder_path = Path(self.settings["results_folder_str"])
            if not results_folder_path.is_dir():
                msg = msg + "Folder to write results does not exist.\n"
                valid = False
        # If using input file, check the executable exists
        if self.file_type.get()=="input_file":
            exe_path_string = self.path_exe.get()
            if exe_path_string == '':
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
            #Select all input files or output files
            if self.file_type.get() == "input_file":
                suffix=[".INP", ".SES"]
            else:
                suffix=[".OUT", ".PRN"]
            self.ses_output_str = nfm.find_all_files(extensions=suffix, pathway=folder_path, with_path=True)
        else:
            self.ses_output_str = []
            files_string = self.path_files.get() 
            self.ses_output_str = files_string.split('; ')   

    def get_results_folder_str(self, *args):
        option = self.results_folder.get()
        if option == "selected":
            self.results_folder_str = self.path_results_folder.get()
        elif option == "visio template":
            visio_str = self.path_visio.get()
            if visio_str !="":
                visio_path = Path(visio_str)
                self.results_folder_str = str(visio_path.parent)
            else:
                self.results_folder_str = None
        else: #Default is same as SES output. Use empty string
            self.results_folder_str = None

    def valid_license(self, *args):
        if self.license_info['type'] == 'Floating':
            ok = self.check_floating_license()
            return ok
        else:
            delta = datetime.timedelta(1)
            expiry = self.license_info['expiry']
            for file_path in self.settings["ses_output_str"]:
                file_time_seconds = os.path.getmtime(file_path)
                file_date= datetime.date.fromtimestamp(file_time_seconds)
                new_delta = expiry - file_date
                if new_delta < delta:
                    delta = new_delta
            if delta < datetime.timedelta(0):
                messagebox.showinfo(
                message='Offline License is being used past the expiry date')
                system_exit("License is expired")
            else:
                return True

    def update_output_options(self, *args):
        option = self.ses.get()
        if option == 'File':
            self.cb_visio_open["state"] = tk.NORMAL
        else:
            self.cb_visio_open["state"] = tk.DISABLED
            self.cbo_visio_open = tk.StringVar(value="")
            
    def update_post_processing_options(self, *args):
        if self.cbo_average.get() == '' and self.cbo_compare.get() == '' and self.cbo_visio.get() == "Visio":
            visio_state = 'enable'
        else:
            visio_state = 'disable'
        #Disable all items in a frame: https://www.tutorialspoint.com/how-to-gray-out-disable-a-tkinter-frame
        for child in self.frm_visio.winfo_children():
            child.configure(state=visio_state)

    def update_ses_exe(self, *args):
        if self.file_type.get() == "output_file":
            ses_exe_state = 'disable'
        else:
            ses_exe_state = 'enable'
        #Disable all items in a frame: https://www.tutorialspoint.com/how-to-gray-out-disable-a-tkinter-frame
        for child in self.frm_ses_exe.winfo_children():
            child.configure(state=ses_exe_state)
        #Set value of variable to be empty if you switch between Input and Output files. 
        #This prevents accidently running an output file as an input file or vice-versa
        self.path_file.set("")
        self.path_files.set("")

    def on_closing(self, root):
        title_on_closing = "Quite Next Vis?"
        msg_1 = "Click 'Yes' to quit and save the most recent settings.\n"
        msg_2 = "Click 'No' to exit without saving.\n"
        msg_3 = "Click 'Cancel' to return back to Next-Vis\n"
        msg_all = msg_1 + msg_2 + msg_3
        #answer = messagebox.askokcancel("Quit", "Do you want to quit Next-Vis?")
        answer = messagebox.askyesnocancel(title=title_on_closing, message = msg_all)
        if answer is None:
            return
        elif answer:
            try:
                settings_2_save = {}
                for key, value in self.screen_settings.items():
                    exec(f'settings_2_save["{key}"]= {key}.get()')
                with open("nv_settings.ini","wb") as f:
                    pickle.dump(settings_2_save, f)
                root.destroy()
            except:
                root.destroy()
        else:
            root.destroy()
       

    def text_update(self, text):
        self.gui_text(text)
        self.ss.update

def launch_window(license_info):
    root = tk.Tk()
    start_screen(root, license_info)
    root.mainloop()

if __name__ == "__main__":
    import main as main
    main.main(False)
