from tkinter import *
from tkinter import filedialog, messagebox, ttk

import main as main
import NV_run as nvr
from NV_parser import percentage_parser


# add requirement for program to be legit to run
class start_screen:
    def __init__(self, root):
        # Initialization and settings
        p = "5"  # padding
        py = "5"  # vertical padding
        px = "5"
        root.title("Next-Vis Beta 021")
        # root.iconbitmap('icon4.ico')
        # Eliminate icon
        # TODO Replace Icon in title bar with NV icon (icon4.ico)
        # root.attributes('-toolwindow', 'True')
        self.ss = ttk.Frame(root, padding=p)  # start screen
        # POST PROCESSING widgets
        frm_pp = ttk.LabelFrame(
            self.ss, borderwidth=5, text="Post Processing", padding=p
        )
        self.cbo_excel = StringVar(value="Excel")
        self.cbo_visio = StringVar(value="")
        self.cbo_compare = StringVar(value="")
        cb_excel = ttk.Checkbutton(
            frm_pp, text="Excel", variable=self.cbo_excel, onvalue="Excel", offvalue=""
        )
        cb_visio = ttk.Checkbutton(
            frm_pp, text="Visio", variable=self.cbo_visio, onvalue="Visio", offvalue=""
        )
        cb_compare = ttk.Checkbutton(
            frm_pp,
            text="Compare outputs",
            variable=self.cbo_compare,
            onvalue="Compare",
            offvalue="",
            state=DISABLED,
        )
        # POST PROCESSING grid
        cb_excel.grid(column=0, row=0, sticky=W, pady=py)
        cb_visio.grid(column=0, row=1, sticky=W, pady=py)
        cb_compare.grid(column=0, row=2, sticky=W, pady=py)
        # SES OUTPUT Files to Process
        frm_ses = ttk.LabelFrame(
            self.ss, borderwidth=5, text="SES Output to Process", padding=p
        )
        self.ses = StringVar(value="file")
        rb_file = ttk.Radiobutton(frm_ses, text="", variable=self.ses, value="file")
        rb_folder = ttk.Radiobutton(frm_ses, text="", variable=self.ses, value="folder")
        self.btn_file = ttk.Button(frm_ses, text="File", command=self.ses_files)
        self.btn_folder = ttk.Button(frm_ses, text="Folder", command=self.ses_folder)
        self.path_file = StringVar()
        self.path_folder = StringVar()
        ent_file = ttk.Entry(frm_ses, textvariable=self.path_file)
        ent_folder = ttk.Entry(frm_ses, textvariable=self.path_folder)
        # SES Output Frame creation Remove line wrap from output file
        r = 0
        frm_ses.grid(column=0, row=r)
        rb_file.grid(column=0, row=r, sticky=[E], pady=py, padx="0")
        self.btn_file.grid(column=1, row=r, sticky=[E], pady=py, padx=px)
        ent_file.grid(column=2, row=r, sticky=[E, W], pady=py, padx=px)
        r = 1
        rb_folder.grid(column=0, row=r, sticky=[E], pady=py, padx="0")
        self.btn_folder.grid(column=1, row=r, sticky=[E], pady=py, padx=px)
        ent_folder.grid(column=2, row=r, sticky=[E, W], pady=py, padx=px)
        frm_ses.columnconfigure(2, weight=1)
        # VISIO Template
        frm_visio = ttk.LabelFrame(
            self.ss, borderwidth=5, text="Visio Template", padding=p
        )
        btn_visio = ttk.Button(frm_visio, text="Select", command=self.visio_file)
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
        # OUTPUT FILE LOCATION widgets
        frm_ofl = ttk.LabelFrame(
            self.ss, borderwidth=5, text="Output File Location", padding=p
        )
        self.ofl = StringVar(value="ses")
        rb_ses = ttk.Radiobutton(
            frm_ofl, text="Same as SES Output", variable=self.ofl, value="ses"
        )
        rb_visio = ttk.Radiobutton(
            frm_ofl,
            text="Same as SES Visio Template",
            variable=self.ofl,
            value="visio",
            state=DISABLED,
        )
        rb_selected = ttk.Radiobutton(
            frm_ofl,
            text="Selected",
            variable=self.ofl,
            value="Selected",
            state=DISABLED,
        )
        btn_ofl = ttk.Button(
            frm_ofl, text="Select", command=self.output_folder, state=DISABLED
        )
        self.path_ofl = StringVar()
        ent_ofl = ttk.Entry(frm_ofl, textvariable=self.path_ofl, state=DISABLED)
        ##OUTPUT FILE LOCATION grid
        rb_ses.grid(column=0, row=0, sticky=W)
        rb_visio.grid(column=1, row=0, sticky=W)
        rb_selected.grid(column=2, row=0, sticky=(E, W))
        btn_ofl.grid(column=0, row=1, sticky=W)
        ent_ofl.grid(column=1, row=1, sticky=[W, E], columnspan=2)
        frm_ofl.columnconfigure(2, weight=1)
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
        frm_ofl.grid(column=1, row=2, sticky=[W, E], pady=py, padx=px)
        frm_visio.grid(column=1, row=1, sticky=[W, E], pady=py, padx=px)
        frm_ses.grid(column=1, row=0, sticky=[N, S, E, W], pady=py, padx=px)
        frm_run.grid(column=1, row=3, sticky=[W, E], pady=py, padx=px)
        frm_status.grid(
            column=0, row=4, columnspan=2, sticky=[W, E, S, N], pady=py, padx=px
        )
        root.minsize(550, 385)  # Measured using paint.net
        # root.maxsize(1080,385) worried about scaling on other monitors

    def visio_file(self, *args):
        try:
            filename = filedialog.askopenfilename(
                title="Select Visio template file", filetypes=[("Visio", "*.vsdx")]
            )
            self.path_visio.set(filename)
            self.cbo_visio.set("Visio")
        except ValueError:
            pass

    def output_folder(self, *args):
        try:
            folder = filedialog.askdirectory(
                title="Select one or more SES output Files"
            )
            self.path_ofl.set(folder)
            self.ofl.set("Selected")
        except ValueError:
            pass

    def ses_files(self, *args):
        try:
            filename = filedialog.askopenfilename(
                title="Select one or more SES output Files",
                filetypes=[("SES Output", ("*.PRN", "*.OUT")),],
            )
            self.path_file.set(filename)
            self.ses.set("file")
        except ValueError:
            pass

    def ses_clear(self, *args):  # For clearing text boxses (not needed right now)
        try:
            self.output_files["state"] = "normal"
            self.output_files.delete("1.0", "end")
            self.output_files["state"] = "disabled"
        except ValueError:
            pass

    def ses_folder(self, *args):
        try:
            filename = filedialog.askdirectory(
                title="Select file with SES output Files",
            )
            self.path_folder.set(filename)
            self.ses.set("folder")
        except ValueError:
            pass

    def run(self, *args):
        # TODO Create status window
        self.btn_run["text"] = "In-progress"
        self.btn_run["state"] = DISABLED
        self.ss.update()
        pp_list = []
        pp_list.append(self.cbo_excel.get())
        pp_list.append(self.cbo_visio.get())
        pp_list.append(self.cbo_compare.get())
        simtime = -1
        # Previous code to get file name from text file: 'simname' : self.output_files.get("1.0",'end-1c'),
        if self.ses.get() == "folder":
            simname = self.path_folder.get()
        else:
            simname = self.path_file.get()
        self.settings = {
            "simname": simname,
            "visname": self.path_visio.get(),
            "simtime": simtime,
            "version": "tbd",
            "control": "First",
            "output": pp_list,
        }
        if self.validation(self.settings):
            try:
                if self.ses.get() == "file":
                    nvr.single_sim(self.settings, gui=self)
                elif self.ses.get() == "folder":
                    self.gui_text(
                        "Error after validation, before single_sim or multiple_sim"
                    )
                    nvr.multiple_sim(self.settings, gui=self)
            except:
                self.gui_text(
                    "Error after validation, before single_sim or multiple_sim"
                )
        self.btn_run["state"] = NORMAL
        self.btn_run["text"] = "Run"
        self.gui_text("Post processing completed")

    def validation(self, settings):
        valid = True
        msg = ""
        if "Visio" in settings["output"]:
            if settings["visname"] == "":
                msg = msg + "No Visio Template File is Specified. \n"
                valid = False
            if self.rbo_time.get() == "user_time":
                time = self.user_time.get()
                if time.isnumeric():
                    self.settings["simtime"] = time
                else:
                    msg = msg + "Specify a number for Visio's Simulation Time"
                    valid = False
        if settings["simname"] == "":
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


if __name__ == "__main__":
    main.main(False)
