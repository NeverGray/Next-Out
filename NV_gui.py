from pathlib import Path
from sys import exit as system_exit
from tkinter import *
from tkinter import filedialog, messagebox, ttk

import keygen
import main as main
import NV_file_manager as nfm
import NV_run as nvr
from NV_parser import percentage_parser


# add requirement for program to be legit to run
class start_screen:
    def __init__(self, root, license_info):
        # Initialization and settings
        p = "5"  # padding
        py = "5"  # vertical padding
        px = "5"
        root.title("Next-Vis")
        # root.iconbitmap('icon4.ico')
        # Eliminate icon
        # TODO Replace Icon in title bar with NV icon (icon4.ico)
        # root.attributes('-toolwindow', 'True')
        self.ss = ttk.Frame(root, padding=p)  # start screen
        self.license_info = license_info
        # POST PROCESSING widgets
        frm_pp = ttk.LabelFrame(
            self.ss, borderwidth=5, text="Post Processing", padding=p
        )
        self.cbo_excel = StringVar(value="Excel")
        self.cbo_visio = StringVar(value="")
        self.cbo_compare = StringVar(value="")
        self.cbo_average = StringVar(value="")
        cb_excel = ttk.Checkbutton(
            frm_pp, text="Excel", variable=self.cbo_excel, onvalue="Excel", offvalue=""
        )
        cb_visio = ttk.Checkbutton(
            frm_pp, text="Visio", variable=self.cbo_visio, onvalue="Visio", offvalue=""
        )
        cb_average = ttk.Checkbutton(
            frm_pp, text="Staggered\nheadeways\nmean, max, min", variable=self.cbo_average, onvalue="Average", offvalue=""
        )
        cb_compare = ttk.Checkbutton(
            frm_pp,
            text="Compare two\noutputs",
            variable=self.cbo_compare,
            onvalue="Compare",
            offvalue="",
        )
        # POST PROCESSING grid
        cb_excel.grid(column=0, row=0, sticky=W, pady=py)
        cb_visio.grid(column=0, row=1, sticky=W, pady=py)
        cb_compare.grid(column=0, row=2, sticky=W, pady=py)
        cb_average.grid(column=0, row=3, sticky=W, pady=py)
        # SES OUTPUT Files to Process
        frm_ses = ttk.LabelFrame(
            self.ss, borderwidth=5, text="SES Output to Process", padding=p
        )
        self.ses = StringVar(value="file")
        rb_file = ttk.Radiobutton(frm_ses, text="", variable=self.ses, value="File")
        rb_files = ttk.Radiobutton(frm_ses, text="", variable=self.ses, value="Files")
        rb_folder = ttk.Radiobutton(frm_ses, text="", variable=self.ses, value="Folder")
        self.btn_file = ttk.Button(frm_ses, text="One file", command=self.ses_file)
        self.btn_files = ttk.Button(frm_ses, text="Many files", command=self.ses_files)
        self.btn_folder = ttk.Button(frm_ses, text="Folder", command=self.ses_folder)
        self.path_file = StringVar()
        self.path_files = StringVar()
        self.path_folder = StringVar()
        ent_file = ttk.Entry(frm_ses, textvariable=self.path_file)
        ent_files = ttk.Entry(frm_ses, textvariable=self.path_files)
        ent_folder = ttk.Entry(frm_ses, textvariable=self.path_folder)
        # SES Output Frame creation
        r = 0
        frm_ses.grid(column=0, row=r)
        rb_file.grid(column=0, row=r, sticky=[E], pady=py, padx="0")
        self.btn_file.grid(column=1, row=r, sticky=[E], pady=py, padx=px)
        ent_file.grid(column=2, row=r, sticky=[E, W], pady=py, padx=px)
        r = 10
        frm_ses.grid(column=0, row=r)
        rb_files.grid(column=0, row=r, sticky=[E], pady=py, padx="0")
        self.btn_files.grid(column=1, row=r, sticky=[E], pady=py, padx=px)
        ent_files.grid(column=2, row=r, sticky=[E, W], pady=py, padx=px)
        r = 20
        rb_folder.grid(column=0, row=r, sticky=[E], pady=py, padx="0")
        self.btn_folder.grid(column=1, row=r, sticky=[E], pady=py, padx=px)
        ent_folder.grid(column=2, row=r, sticky=[E, W], pady=py, padx=px)
        frm_ses.columnconfigure(2, weight=1)
        # VISIO Template
        frm_visio = ttk.LabelFrame(
            self.ss, borderwidth=5, text="Visio Template", padding=p
        )
        btn_visio = ttk.Button(frm_visio, text="Select", command=self.get_visio_file)
        self.path_visio = StringVar()
        ent_visio = ttk.Entry(frm_visio, textvariable=self.path_visio)
        lbl_time = ttk.Label(frm_visio, text="Simulation Time: ")
        self.rbo_time = StringVar(value="end")
        rb_end_time = ttk.Radiobutton(
            frm_visio, text="End", variable=self.rbo_time, value="end"
        )
        rb_user_time = ttk.Radiobutton(
            frm_visio, text="Specified", variable=self.rbo_time, value="user_time"
        )
        self.user_time = StringVar()
        self.ent_user_time = ttk.Entry(frm_visio, textvariable=self.user_time)
        # VISIO GRID
        r = 0  # Top Row
        btn_visio.grid(column=0, row=r, sticky=W, pady=py)
        ent_visio.grid(column=1, row=r, columnspan=3, sticky=[W, E], pady=py)
        r = 1
        lbl_time.grid(column=0, row=r, sticky=W, pady=py)
        rb_end_time.grid(column=1, row=r, sticky=W, pady=py)
        rb_user_time.grid(column=2, row=r, sticky=W, pady=py)
        self.ent_user_time.grid(column=3, row=r, sticky=[W, E], pady=py)
        frm_visio.columnconfigure(3, weight=1)
        # Results Folder widgets
        frm_results_folder = ttk.LabelFrame(self.ss, borderwidth=5, text="Folder to write results", padding=p)
        self.results_folder = StringVar(value="ses output")
        rb_ses = ttk.Radiobutton(frm_results_folder, text="Same as SES Output", variable=self.results_folder, value="ses output")
        rb_visio = ttk.Radiobutton(frm_results_folder,text="Same as Visio Template",variable=self.results_folder,value="visio template")
        rb_selected = ttk.Radiobutton(frm_results_folder,text="Selected",variable=self.results_folder, value="selected")
        btn_results_folder = ttk.Button(frm_results_folder, text="Select", command=self.get_results_folder)
        self.path_results_folder = StringVar()
        ent_results_folder = ttk.Entry(frm_results_folder, textvariable=self.path_results_folder)
        # OUTPUT FILE LOCATION grid
        rb_ses.grid(column=0, row=0, sticky=W)
        rb_visio.grid(column=1, row=0, sticky=W)
        rb_selected.grid(column=2, row=0, sticky=(E, W))
        btn_results_folder.grid(column=0, row=1, sticky=W)
        ent_results_folder.grid(column=1, row=1, sticky=[W, E], columnspan=2)
        frm_results_folder.columnconfigure(2, weight=1)
        # RUN button
        frm_run = ttk.Frame(self.ss, padding=p, borderwidth=5)
        self.btn_run = ttk.Button(frm_run, text="Run", command=self.run)
        self.btn_run.pack(expand=True, fill=BOTH)
        # STATUS SCREEN
        frm_status = ttk.LabelFrame(self.ss, borderwidth=5, text="Status", padding=p)
        self.txt_status = Text(
            frm_status, width=30, height=5, state=DISABLED, wrap="none",
        )
        self.ys_status = ttk.Scrollbar(
            frm_status, orient="vertical", command=self.txt_status.yview
        )
        self.txt_status["yscrollcommand"] = self.ys_status.set
        self.txt_status.pack(side=LEFT, expand=TRUE, fill=BOTH)
        self.ys_status.pack(side=RIGHT, fill=Y)
        # START SCREEN grid
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        # root.rowconfigure(0, weight=1)
        self.ss.grid(column=0, row=0, sticky=(E, W, N, S))
        self.ss.columnconfigure(1, weight=1)
        self.ss.rowconfigure(4, weight=1)
        frm_pp.grid(column=0, row=0, rowspan=4, sticky=[N, S], pady=py, padx=px)
        frm_results_folder.grid(column=1, row=2, sticky=[W, E], pady=py, padx=px)
        frm_visio.grid(column=1, row=1, sticky=[W, E], pady=py, padx=px)
        frm_ses.grid(column=1, row=0, sticky=[N, S, E, W], pady=py, padx=px)
        frm_run.grid(column=1, row=3, sticky=[W, E], pady=py, padx=px)
        frm_status.grid(
            column=0, row=4, columnspan=2, sticky=[W, E, S, N], pady=py, padx=px
        )
        root.minsize(550, 385)  # Measured using paint.net
        self.display_validation_info()
        # root.maxsize(1080,385) worried about scaling on other monitors

    def display_validation_info(self, *args):
        validation_code, license_id, validation_info = keygen.validate_license_key_with_fingerprint(
            self.license_info["floating_key"], self.license_info['machine_fingerprint'])
        floats_available = validation_info['data']['attributes']['maxMachines']
        floats_in_use = validation_info['data']['relationships']['machines']['meta']['count']
        authorized_company = self.license_info["Authorized_Company"]
        expiry = validation_info['data']['attributes']['expiry'][:10]
        msg_line=[]
        msg_line.append(f'Click OKAY to accept "Next-Vis License Agrement"')
        msg_line.append("Otherwise, click Cancel to exit")
        msg_line.append(f"\n{floats_in_use} of {floats_available} floating licenses in use for {authorized_company}.")
        msg_line.append(f'License Expires on {expiry}.')
        msg = "\n".join(msg_line)
        answer = messagebox.askokcancel(title='Use and accept license', message=msg, icon ='info')
        if not answer:
            system_exit("User did not accept license agreement")

    def check_floating_license(self, *args):
        active_license = keygen.ping_heartbeat_for_machine(
        self.license_info["machine_fingerprint"], self.license_info["floating_token"])
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

    def ses_file(self, *args):
        try:
            filename = filedialog.askopenfilename(
                title="Select one SES output Files",
                filetypes=[("SES Output", ("*.PRN", "*.OUT")),],
            )
            self.path_file.set(filename)
            self.ses.set("File")
        except ValueError:
            pass

    def ses_files(self, *args):
        try:
            files = filedialog.askopenfilenames(
                title="Select many SES output Files by holding Ctrl",
                filetypes=[("SES Output", ("*.PRN", "*.OUT")),],
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
        self.btn_run["state"] = DISABLED
        self.ss.update()
        if not self.check_floating_license():
            system_exit("Floating License is not Active")
        pp_list = []
        pp_list.append(self.cbo_excel.get())
        pp_list.append(self.cbo_visio.get())
        pp_list.append(self.cbo_compare.get())
        pp_list.append(self.cbo_average.get())
        try:
            self.get_ses_output_str()
        except:
            error_msg = "ERROR finding output file locations"
            self.gui_text(error_msg)
        try:
            self.get_results_folder_str()
        except:
            error_msg = "EEROR with getting result folder"
            self.gui_text(error_msg)
        self.settings = {
            "ses_output_str": self.ses_output_str,
            "visio_template": self.path_visio.get(),
            "results_folder_str": self.results_folder_str,
            "simtime": -1, #Updated in validation
            "version": "tbd",
            "control": "First",
            "output": pp_list,
        }
        if self.validation(self.settings):
            try:
                if (self.ses.get() == "File") or ("Average" in pp_list) or ("Compare" in pp_list):
                    nvr.single_sim(self.settings, gui=self)
                else:
                    nvr.multiple_sim(self.settings, gui=self)
            except:
                self.gui_text(
                    "Error after validation, before single_sim or multiple_sim"
                )
        self.btn_run["state"] = NORMAL
        self.btn_run["text"] = "Run"
        self.gui_text("Post processing completed.")

    def validation(self, settings):
        valid = True
        msg = ""
        if "Visio" in settings["output"]:
            if settings["visio_template"] == "":
                msg = msg + "No Visio Template File is Specified. \n"
                valid = False
            if self.rbo_time.get() == "user_time":
                time = self.user_time.get()
                if time.isnumeric():
                    self.settings["simtime"] = time
                else:
                    msg = msg + "Specify a number for Visio's Simulation Time"
                    valid = False
        if settings["ses_output_str"] == "":
            msg = msg + "No SES output file or folders are specified."
            valid = False
        if not valid:
            messagebox.showinfo(message=msg)
        return valid

    def gui_text(self, status):
        self.txt_status["state"] = NORMAL
        self.txt_status.insert("end", status + "\n")
        self.txt_status.see(END)
        self.txt_status["state"] = DISABLED
        self.ss.update()

    def get_ses_output_str(self, *args):
        if self.ses.get() == "File":
            self.ses_output_str = self.path_file.get()
        elif self.ses.get() == "Folder":
            self.ses_output_str = []
            folder_path = self.path_folder.get()
            self.ses_output_str = nfm.find_all_files(pathway=folder_path, with_path=True)
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

if __name__ == "__main__":
    main.main(False)
