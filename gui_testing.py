from tkinter import *
from tkinter import ttk
from tkinter import filedialog

class start_screen:
def start_screen(root):

        root.title("Next-Vis Beta 020")
        root.iconbitmap('icon4.ico')
        ss = ttk.Frame(root, padding="10") #start screen
        #Post Proccessing Frame (frm_pp) for check boxes
        frm_pp = ttk.LabelFrame(ss, borderwidth=5, text = 'Post Processing', padding="5")
        cbo_excel = StringVar()
        cbo_visio = StringVar()
        cbo_compare = StringVar()
        cb_excel = ttk.Checkbutton(frm_pp, text='Excel', variable = cbo_excel, onvalue = 'Excel', offvalue= '')
        cb_visio = ttk.Checkbutton(frm_pp, text='Visio', variable= cbo_visio, onvalue = 'Visio', offvalue= '')
        cb_compare= ttk.Checkbutton(frm_pp, text='Compare outputs', variable= cbo_compare, onvalue = 'Compare', offvalue= '')
        cb_excel.grid(column = 0, row = 0, sticky = W)
        cb_visio.grid(column = 0, row = 1, sticky = W)
        cb_compare.grid(column = 0, row = 2, sticky = W)
        #Output File Locations
        #TODO expand entry file name full length of window
        frm_ofl = ttk.LabelFrame(ss, borderwidth=5, text = 'Output File Location',padding="5")
        ofl = StringVar(value='ses')
        rb_ses   = ttk.Radiobutton(frm_ofl,text = 'Same as SES Output', variable = ofl, value='ses')
        rb_visio = ttk.Radiobutton(frm_ofl,text = 'Same as SES Visio Template', variable = ofl, value='visio')
        rb_selected =  ttk.Radiobutton(frm_ofl,text = 'Selected', variable = ofl, value='folder')
        rb_ses.grid(column = 1, row=0, sticky = W)
        rb_visio.grid(column = 2, row=0,sticky = W)
        rb_selected.grid(column = 0, row=0, sticky = W)
        btn_ofl = ttk.Button(frm_ofl, text='Select')
        btn_ofl.grid(column = 0, row=1, sticky = W)
        path_ofl = StringVar()
        ent_ofl = ttk.Entry(frm_ofl, textvariable = path_ofl)
        ent_ofl.grid(column = 1, row=1, sticky = [W,E], columnspan=2)
        #Visio Template
        #TODO expand entry file name full length of window
        frm_visio = ttk.LabelFrame(ss, borderwidth=5, text = 'Visio Template',padding="5")
        btn_visio = ttk.Button(frm_visio, text='Select', command=find_file)
        btn_visio.grid(column = 0, row = 0, sticky = W)
        path_visio = StringVar()
        ent_visio = ttk.Entry(frm_visio, textvariable = path_visio)
        ent_visio.grid(column = 1, row=0, sticky = [W,E])
        #SES Output Files to Process
        frm_ses = ttk.LabelFrame(ss, borderwidth=5, text = 'SES Output Files to Process',padding="5")
        btn_files = ttk.Button(frm_ses, text='File(s)')
        btn_folders = ttk.Button(frm_ses, text='Folder')
        btn_clear = ttk.Button(frm_ses, text='Clear')
        output_files = Text(frm_ses, width=75, height=10)
        btn_files.grid(column = 0, row = 0, sticky=[E,W])
        btn_folders.grid(column = 1, row = 0, sticky=[E,W])
        btn_clear.grid(column = 2, row = 0, sticky=[E,W])
        output_files.grid(column = 0,row = 1, columnspan = 3)
        #Runbutton
        #TODO expand run button entire length of window
        frm_run = ttk.Frame(ss, padding="5", borderwidth=5)
        btn_run = ttk.Button(frm_run, text='Run')
        btn_run.grid(column = 0, row =0)
        #Start Screen (SS) organization
        ss.grid(column = 0,row = 0)
        frm_pp.grid(column=0, row = 0, rowspan = 4, sticky=[N,S])
        frm_ofl.grid(column = 1, row = 0, sticky = [W,E])
        frm_visio.grid(column = 1, row = 1, sticky = [W,E])
        frm_ses.grid(column =1, row =2,sticky = [N,S,E,W])
        frm_run.grid(column = 1, row =3,sticky = [N,S,E,W])
        #TODO Adjust active adjustements. Entry boxes to right, SES text box vertically down
        root.mainloop()

def find_file(filetypes=[('Visio', '*.vsdx')], title='Select Visio Template'):
    #Allows signel file selection
    filename = filedialog.askopenfilename(
        title = title,
        filetypes = filetypes) 
    return filename

if __name__ == '__main__':
    root = Tk()
    #TODO Adjust Active adjustments
    #root.columnconfigure(1, weight=1)
    #root.rowconfigure(2, weight=1)
    start_screen(root)

