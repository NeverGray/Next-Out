from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import NV_run as nvr

#add requirement for program to be legit to run
class start_screen:
    
    def __init__(self, root):

        root.title("Next-Vis Beta 020")
        root.iconbitmap('icon4.ico')
        ss = ttk.Frame(root, padding="10") #start screen
        #Post Proccessing Frame (frm_pp) for check boxes
        frm_pp = ttk.LabelFrame(ss, borderwidth=5, text = 'Post Processing', padding="5")
        #TODO Use a list compiler?
        self.cbo_excel = StringVar(value='Excel')
        self.cbo_visio = StringVar(value='')
        self.cbo_compare = StringVar(value='')
        cb_excel = ttk.Checkbutton(frm_pp, text='Excel', variable = self.cbo_excel, onvalue = 'Excel', offvalue= '')
        cb_visio = ttk.Checkbutton(frm_pp, text='Visio', variable= self.cbo_visio, onvalue = 'Visio', offvalue= '')
        cb_compare= ttk.Checkbutton(frm_pp, text='Compare outputs', variable= self.cbo_compare, onvalue = 'Compare', offvalue= '',state=DISABLED)
        cb_excel.grid(column = 0, row = 0, sticky = W)
        cb_visio.grid(column = 0, row = 1, sticky = W)
        cb_compare.grid(column = 0, row = 2, sticky = W)
        #Output File Locations
        #TODO expand entry file name full length of window
        frm_ofl = ttk.LabelFrame(ss, borderwidth=5, text = 'Output File Location',padding="5")
        self.ofl = StringVar(value='ses')
        rb_ses   = ttk.Radiobutton(frm_ofl,text = 'Same as SES Output', variable = self.ofl, value='ses')
        rb_visio = ttk.Radiobutton(frm_ofl,text = 'Same as SES Visio Template', variable = self.ofl, value='visio')
        rb_selected =  ttk.Radiobutton(frm_ofl,text = 'Selected', variable = self.ofl, value='Selected')
        rb_ses.grid(column = 1, row=0, sticky = W)
        rb_visio.grid(column = 2, row=0,sticky = W)
        rb_selected.grid(column = 0, row=0, sticky = W)
        btn_ofl = ttk.Button(frm_ofl, text='Select', command = self.output_folder)
        btn_ofl.grid(column = 0, row=1, sticky = W)
        self.path_ofl = StringVar()
        ent_ofl = ttk.Entry(frm_ofl, textvariable = self.path_ofl)
        ent_ofl.grid(column = 1, row=1, sticky = [W,E], columnspan=2)
        #Visio Template
        #TODO expand entry file name full length of window
        frm_visio = ttk.LabelFrame(ss, borderwidth=5, text = 'Visio Template',padding="5")
        btn_visio = ttk.Button(frm_visio, text='Select', command=self.visio_file)
        btn_visio.grid(column = 0, row = 0, sticky = W)
        self.path_visio = StringVar()
        ent_visio = ttk.Entry(frm_visio, textvariable = self.path_visio)
        ent_visio.grid(column = 1, row=0, sticky = [W,E])
        #SES Output Files to Process
        #TODO right align the text in the box
        frm_ses = ttk.LabelFrame(ss, borderwidth=5, text = 'SES Output Files to Process',padding="5")
        self.btn_files = ttk.Button(frm_ses, text='File', command = self.ses_files)
        self.btn_folders = ttk.Button(frm_ses, text='Folder', command = self.ses_folder)
        self.btn_clear = ttk.Button(frm_ses, text='Clear', command = self.ses_clear)
        self.output_files = Text(frm_ses, width=75, height=10)
        self.output_files['state'] = 'disabled'
        #TODO Remove line wrap from output file
        self.btn_files.grid(column = 0, row = 0, sticky=[E,W])
        self.btn_folders.grid(column = 1, row = 0, sticky=[E,W])
        self.btn_clear.grid(column = 2, row = 0, sticky=[E,W])
        self.output_files.grid(column = 0,row = 1, columnspan = 3)
        #Runbutton
        #TODO expand run button entire length of window
        frm_run = ttk.Frame(ss, padding="5", borderwidth=5)
        self.btn_run = ttk.Button(frm_run, text='Run', command = self.run)
        self.btn_run.grid(column = 0, row =0)
        #Start Screen (SS) organization
        #TODO Add input for simulation time for output
        ss.grid(column = 0,row = 0)
        frm_pp.grid(column=0, row = 0, rowspan = 4, sticky=[N,S])
        frm_ofl.grid(column = 1, row = 0, sticky = [W,E])
        frm_visio.grid(column = 1, row = 1, sticky = [W,E])
        frm_ses.grid(column =1, row =2,sticky = [N,S,E,W])
        frm_run.grid(column = 1, row =3,sticky = [N,S,E,W])
        #TODO Adjust active adjustements. Entry boxes to right, SES text box vertically down

    def visio_file(self,*args):
        try:
                filename = filedialog.askopenfilename(
                    title = "Select Visio template file",
                    filetypes = [('Visio', '*.vsdx')])
                self.path_visio.set(filename)
                self.cbo_visio.set('Visio')
        except ValueError:
            pass

    def output_folder(self,*args):
        try:
            folder = filedialog.askdirectory(
                title = "Select one or more SES output Files")
            self.path_ofl.set(folder)
            self.ofl.set('Selected')
        except ValueError:
            pass
    
    def ses_files(self,*args):
        try:
            filename = filedialog.askopenfilename(
                title = "Select one or more SES output Files",
                filetypes = [('SES Output', ('*.PRN', '*.OUT')),])
            self.ses_clear()
            self.output_files['state'] = 'normal'
            self.output_files.insert('end', filename)
            self.output_files['state'] = 'disabled'
        except ValueError:
            pass
    
    def ses_clear(self,*args):
        try:
            self.output_files['state'] = 'normal'
            self.output_files.delete('1.0','end')
            self.output_files['state'] = 'disabled'
        except ValueError:
            pass

    def ses_folder(self,*args):
        try:
            filename = filedialog.askdirectory(
                title = "Select file with SES output Files",)
            self.ses_clear()
            self.output_files['state'] = 'normal'
            self.output_files.insert('end', filename)
            self.output_files['state'] = 'disabled'
        except ValueError:
            pass
    
    def run(self,*args):
            #TODO Create status window
            #TODO Process multiple files
            pp_list = []
            pp_list.append(self.cbo_excel.get())
            pp_list.append(self.cbo_visio.get())
            pp_list.append(self.cbo_compare.get())
            print('This is a test, this is only a test. Any questions')
            print(pp_list)
            settings={
                'simname' : self.output_files.get("1.0",'end-1c'),
                'visname' : self.path_visio.get(),
                'simtime' : 9999.0,
                'version' : 'tbd',
                'control' : 'First',
                'output'  : pp_list
            }
            print(settings['output'])
            nvr.single_sim(settings)

    #TODO Pass file or file names to display window

if __name__ == '__main__':
    root = Tk()
    start_screen(root)
    root.mainloop()
