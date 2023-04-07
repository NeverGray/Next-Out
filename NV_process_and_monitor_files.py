'''This code processes and monitor multiple files'''
import logging
import multiprocessing
import os
import threading
import time
import tkinter as tk
import subprocess
from pathlib import Path
from tkinter import messagebox, ttk

import NV_parser
import NV_excel_R01 as nve
import NV_route
import NV_visio


#logging.disable(logging.CRITICAL)
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s -  %(levelname)s -  %(message)s')

VERSION_NUMBER = "1"
UPDATE_FREQUENCY = 1000 #vALUE IN MILLISECONDS
COLUMN_HEADERS = ("PID", "File", "Simulation", "Read Output", "Visio", "Excel", "Route")
STATUS_FONT_COLOR = {
    '-': 'black',
    'Queued': 'blue',
    'Processing':'orange',
    'Done':'green',
    'Failed':'red'
}


def single_process(file_path, process_settings, settings, queued_list, processing_dictionary, done_list, pause_value,):
    pause_check(pause_value)
    # Prepare to monitor process status
    name = file_path.stem
    queued_list.remove(name)
    pid = os.getpid()
    value_index = process_settings['process_status_value_index']
    process_status = process_settings['process_status_start_values']
    process_status[value_index['name']] = name
    processing_dictionary[pid] = process_status

    # Start processing files
    # Perform simulation if necessary
    if process_settings['Simulation']:
        pause_check(pause_value)
        process_status[value_index['Simulation']] = "Processing"
        processing_dictionary[pid] = process_status
        logging.info(f"Staring SES simlaution of {name}")
        successful_simulation = run_SES(settings["path_exe"], file_path.__str__())
        if successful_simulation:
            # Change file path to work on the output file
            file_path = output_from_input(file_path, settings["path_exe"])
        else:
            logging.info(f"SES simulation failed for {name}")
            process_status[value_index['Simulation']] = "Failed"
            processing_dictionary[pid] = process_status
            return
        logging.info(f"Finished writing Visio file for {name}")
        process_status[value_index['Simulation']] = "Done"
        processing_dictionary[pid] = process_status
    # Parse output file
    logging.info(f"Parsing {name}")
    process_status[value_index['Read Output']] = "Processing"
    processing_dictionary[pid] = process_status
    data, output_meta_data = NV_parser.parse_file(file_path, gui="",convert_df=settings['version'])
    process_status[value_index['Read Output']] = "Done"
    processing_dictionary[pid] = process_status
    logging.info(f"Finished Parsing {name}")
    if process_settings['Visio']:
        pause_check(pause_value)
        process_status[value_index['Visio']] = "Processing"
        processing_dictionary[pid] = process_status
        logging.info(f"Staring to create Visio file for {name}")
        NV_visio.create_visio(settings, data, output_meta_data, gui="")
        logging.info(f"Finished writing Visio file for {name}")
        process_status[value_index['Visio']] = "Done"
        processing_dictionary[pid] = process_status
    if process_settings['Excel']:
        pause_check(pause_value)
        process_status[value_index['Excel']] = "Processing"
        processing_dictionary[pid] = process_status
        logging.info(f"Staring to create Excel file for {name}")
        nve.create_excel(settings, data, output_meta_data, gui="")
        logging.info(f"Finished writing Excel file for {name}")
        process_status[value_index['Excel']] = "Done"
        processing_dictionary[pid] = process_status
    if process_settings['Route']:
        pause_check(pause_value)
        process_status[value_index['Route']] = "Processing"
        processing_dictionary[pid] = process_status
        logging.info(f"Staring to create Route file for {name}")
        NV_route.create_route_excel(settings, data, output_meta_data, gui="")
        logging.info(f"Finished writing Excel file for {name}")
        process_status[value_index['Route']] = "Done"
        processing_dictionary[pid] = process_status
    done_list.append(name)
    logging.info(f"Finished processing {name}")

def run_SES(ses_exe_path, ses_input_file_path, gui =""):
    try: 
        # Check the proces is successful, see https://realpython.com/python-subprocess/ 
        subprocess.run([ses_exe_path, ses_input_file_path], check=True) 
        return True
    except FileNotFoundError as exc: 
        logging.info(f"Process failed because the executable could not be found.\n{exc}")
        return False
    except subprocess.CalledProcessError as exc: 
        if exc.returncode == 100:
            return True
        else:
            msg = ( 
                    f"SES Simulation failed." 
                    f"Returned {exc.returncode}\n{exc}" 
                )
            logging.info(msg)
            return False
    except:
        return False

def output_from_input(file_path, path_exe):
    #TODO Select suffix based on SES type
    try:
        if "SES41.exe".lower() in path_exe.lower():
            extension = ".PRN"
        else:
            extension = ".OUT"
        new_file_path = file_path.with_suffix(extension)
        return new_file_path
    except:
        logging.debug("Error in 'output_from_input' when converting file strings")
        return file_path

def pause_check(pause_value):
    while pause_value.get() == 1:
        time.sleep(1.0)
    return

class Manager_Class:
    def __init__(self):
        logging.debug('Start of manager class')
        self.manager = multiprocessing.Manager()
        self.shared_dict = self.manager.dict()
        self.processing_dictionary = self.manager.dict()
        self.queued_files = self.manager.list()
        self.done_files = self.manager.list()
        self.pause_value = self.manager.Value("i",0)
        self.finished = self.manager.Value("i",0)
        self.file_names = self.manager.list()

class Monitor_GUI(tk.Toplevel):
    def __init__(self, parent, manager, start_screen_settings):
        super().__init__(parent)
        self.manager = manager
        self.settings = start_screen_settings
        self.create_process_settings() #Create settings for processing
        self.in_progress = True
        p = "5"  # padding
        self.title("Next-Vis " + VERSION_NUMBER + " Monitor")
        self.c_width = 15
        self.font_size = 14
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Establish base frame to draw monitor
        self.monitor_window = ttk.Frame(self, padding=p, borderwidth=5)
        # Queued List
        self.queue_frame = ttk.LabelFrame(
            self.monitor_window, borderwidth=5, text="Queued Files", padding=p
        )
        self.queued_scrollbar = ttk.Scrollbar(self.queue_frame)
        self.queued_scrollbar.pack(side='right', fill='y')
        self.queued_list_var = tk.Variable(value=[]) #Start with blank value
        #Trying to start queue with a list of files. 
        #self.queued_list_var.set(['hello world'])
        self.queued_list_var.set(list(self.manager.queued_files))
        self.queued_list = tk.Listbox(self.queue_frame, yscrollcommand=self.queued_scrollbar.set, listvariable=self.queued_list_var)
        self.queued_scrollbar.config(command = self.queued_list.yview)
        self.queued_list.pack(side='left', fill='both')
        # Create processing table
        self.processing_frame = ttk.LabelFrame(
            self.monitor_window, borderwidth=5, text="Processing", padding=p
        )
        headers = COLUMN_HEADERS
        column_number = 10
        for header in headers:
            self.entry = tk.Entry(
                self.processing_frame,
                width=self.c_width,
                bg="DarkOrange1",
                fg="Black",
                font=("Arial", self.font_size, "bold"),
            )
            self.entry.grid(row=10, column=column_number)
            self.entry.insert(tk.END, header)
            column_number += 10
        # Done List
        self.done_frame = ttk.LabelFrame(
            self.monitor_window, borderwidth=5, text="Done Files", padding=p
        )
        self.done_scrollbar = ttk.Scrollbar(self.done_frame)
        self.done_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.done_list_var = tk.Variable(value=[]) #Start with blank value
        self.done_list = tk.Listbox(self.done_frame, yscrollcommand=self.done_scrollbar.set, listvariable=self.done_list_var)
        self.done_scrollbar.config(command = self.done_list.yview)
        self.done_list.pack(side=tk.LEFT, fill=tk.BOTH)

        # Pause and stop buttons
        button_frame = ttk.LabelFrame(
            self.monitor_window, borderwidth=5, text="Control", padding=p
        )
        self.pause_text = tk.StringVar()
        self.pause_text.set("Pause")
        self.btn_pause = ttk.Button(
            button_frame, textvariable=self.pause_text, command=self.pause_press, width=20
        )
        ''' Previous code for a start button
        self.start_text = tk.StringVar()
        self.start_text.set("Start")
        self.btn_start = ttk.Button(
            button_frame, textvariable=self.start_text, command=self.seperate_thread, width=20
        )
        self.btn_start.grid(column=3, row=1)'''
        #Draw Item
        self.btn_pause.grid(column=2, row=1)
        # Draw grid
        self.monitor_window.grid(column=1, row=1, sticky="EWNS")
        self.queue_frame.grid(column=5,row=10, sticky='NS')
        self.processing_frame.grid(column=10, row=10, sticky='N')
        self.done_frame.grid(column=15,row=10, sticky='NS')
        button_frame.grid(column=10, row=100)
        self.seperate_thread()
        self.after(UPDATE_FREQUENCY, self.update_monitor_window)

    def update_monitor_table(self):
        #Update the queued and done list in the tkinter application, manager
        self.queued_list_var.set(list(self.manager.queued_files))
        self.done_list_var.set(list(self.manager.done_files))
        row_number = 20
        for key, values in self.manager.processing_dictionary.items():
            column_number = 10
            self.entry = tk.Entry(
                self.processing_frame, width=self.c_width, fg="blue", font=("Arial", self.font_size, "")
            )
            self.entry.grid(row=row_number, column=column_number)
            #First entry is the PID for the process
            self.entry.insert(tk.END, key)
            column_number += 10
            #Update the status of the process for the PID
            for value in values:
                font_color_text = STATUS_FONT_COLOR.get(value, "black")
                self.entry = tk.Entry(
                    self.processing_frame, width=self.c_width, fg=font_color_text, font=("Arial", self.font_size, "")
                )
                self.entry.grid(row=row_number, column=column_number)
                self.entry.insert(tk.END, value)
                column_number += 10
            row_number += 10

    def update_monitor_window(self):
        if self.in_progress:
            #Update the processing dictionary
            self.update_monitor_table()
            self.update()
            self.after(UPDATE_FREQUENCY, self.update_monitor_window)
        else:
            return

    def pause_press(self):
        print('Clicked Pause')
        if self.pause_text.get() == "Pause":
            self.manager.pause_value.value = 1
            self.pause_text.set("Continue")
        else:
            self.manager.pause_value.value = 0
            self.pause_text.set("Pause")
    
    def seperate_thread(self):
        print('Starting a single thread to control the processing pool')
        self.t1=threading.Thread(target=self.processing_pool, daemon=True)
        self.t1.start()

    def processing_pool(self):
        logging.info('Getting ready to start the pool')
        num_files = len(self.settings["ses_output_str"])
        # Use all processors except 1
        num_of_processes = max(multiprocessing.cpu_count() - 1, 1)  
        num_of_processes = min(num_of_processes, num_files)
        logging.info('Stating loop for multiprocesing')
        with multiprocessing.Pool(num_of_processes) as self.pool:
            self.results = []
            for file_path in self.file_paths:
                result = self.pool.apply_async(single_process, args=(file_path, self.process_settings, self.settings, self.manager.queued_files, self.manager.processing_dictionary, self.manager.done_files, self.manager.pause_value,))
                self.results.append(result)
            self.pool.close()
            self.pool.join()
        logging.info('Processing Pool finished')
        self.in_progress = False #This stops the self-updating process.
        #Message that this finished.
        self.update_monitor_table()
        self.update()
        title_msg = "Post-processing complete."
        msg_1 = "Click 'Okay' to return to main screen."
        msg_all = msg_1
        #Make message box appear above the status window using code from https://stackoverflow.com/questions/52345195/getting-tkinter-messagebox-at-top-of-the-screen-in-python
        self.wm_attributes("-topmost",-1)
        messagebox.showinfo(title=title_msg, message = msg_all, parent=self)
        self.destroy()

    def create_process_settings(self):
        settings = self.settings
        self.process_settings = {}
        #Determine if an SES Simulation needs to be performed
        self.process_settings['Simulation'] = settings['file_type']=='input_file'
        #All processes require the read_output to be performed
        self.process_settings['Read Output'] = True
        #Determine what processes are needed after parsing the file
        post_read_processes = ['Visio','Excel','Route']
        for process_name in post_read_processes:
            setting_selected = process_name in settings['output']
            self.process_settings[process_name] = setting_selected
        #Determine staring values for process_dictionary. A list and index is used because this assumed to be faster than a dictionary
        process_status_start_values = []
        process_status_value_index = {}
        process_status_start_values.append('name') #holding spot for name
        i = 0 #starting value for index
        process_status_value_index['name'] = i
        for key, value in self. process_settings.items():
            i +=1
            if value:
                status = "Queued"
            else:
                status = "-"
            process_status_start_values.append(status)
            process_status_value_index[key] = i

        self.process_settings['process_status_start_values'] = process_status_start_values
        self.process_settings['process_status_value_index'] = process_status_value_index
        # Create list of file paths and start queue with names
        self.file_paths = []
        for value in self.settings['ses_output_str']:
            path = Path(value)
            self.file_paths.append(path)
            self.manager.queued_files.append(path.stem)

    def on_closing(self):
        # Try to pause ongoing processes
        self.update_monitor_table()
        self.update()
        self.manager.pause_value.value = 1
        self.pause_text.set("Continue")
        # Create window
        title_on_closing = "Stop processing immediately?"
        msg_1 = "Click 'Yes' to quit immediately.\n"
        msg_2 = "Click 'No' to continue.\n"
        #msg_3 = "Click 'Cancel' to continue processing.\n"
        msg_all = msg_1 + msg_2 #+ msg_3
        answer = messagebox.askyesno(title=title_on_closing, message = msg_all)
        #TODO Exit if pool is already.
        if answer: #Yes
            #Check if any results are still pending
            try:
                if any(not result.ready() for result in self.results):
                    self.pool.terminate()
                    self.pool.join()
                self.destroy()
            except:
                self.destroy()
        else:
            self.manager.pause_value.value = 0
            self.pause_text.set("Pause")
            return

class App(tk.Tk):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.geometry('300x200')
        self.title('Main Window')
        # place a button on the root window
        ttk.Button(self,
                text='Open a window',
                command=self.open_window).pack(expand=True)

    def open_window(self):
        manager = Manager_Class()
        window = Monitor_GUI(self, manager, self.settings)
        window.focus_force()
        window.grab_set()

if __name__ == "__main__":
    one_output_file = ['C:/Simulations/Demonstration/SI Samples/siinfern-detailed.out']
    two_output_files = ['C:/Simulations/Demonstration/SI Samples/siinfern-detailed.out', 'C:/Simulations/Demonstration/SI Samples/sinorm-detailed.out']
    many_output_files = ['C:/Simulations/Demonstration/SI Samples\\coolpipe.out', 'C:/Simulations/Demonstration/SI Samples\\siinfern-detailed.out', 'C:/Simulations/Demonstration/SI Samples\\siinfern.out', 'C:/Simulations/Demonstration/SI Samples\\sinorm-detailed.out', 'C:/Simulations/Demonstration/SI Samples\\sinorm.out', 'C:/Simulations/Demonstration/SI Samples\\Test02R01.out', 'C:/Simulations/Demonstration/SI Samples\\Test06.out']
    many_output_files.remove('C:/Simulations/Demonstration/SI Samples\\Test02R01.out') #Takes too long to compute
    #If using input file, change 'file_type' value to 'input_file
    one_input_file = ['C:/Simulations/Demonstration/SI Samples/siinfern-detailed.inp']
    two_input_files = ['C:/Simulations/Demonstration/SI Samples/siinfern-detailed.inp', 'C:/Simulations/Demonstration/SI Samples/sinorm-detailed.inp']
    many_input_files = ['C:/Simulations/Demonstration/SI Samples\\coolpipe.inp', 'C:/Simulations/Demonstration/SI Samples\\siinfern-detailed.inp', 'C:/Simulations/Demonstration/SI Samples\\siinfern.inp', 'C:/Simulations/Demonstration/SI Samples\\sinorm-detailed.inp', 'C:/Simulations/Demonstration/SI Samples\\sinorm.inp', 'C:/Simulations/Demonstration/SI Samples\\Test02R01.inp', 'C:/Simulations/Demonstration/SI Samples\\Test06.inp']
    many_input_files.remove('C:/Simulations/Demonstration/SI Samples\\Test02R01.inp') #Takes too long to compute
    settings = {
        'ses_output_str': one_input_file, 
        'visio_template': 'C:/Simulations/Demonstration/Next Vis Samples1p21.vsdx', 
        'results_folder_str': 'C:/Simulations/1p30 Testing', 
        'simtime': -1, 
        'version': '', 
        'control': 'First', 
        'output': ['Excel', 'Visio', '', '', 'Route', '', '', '', ''], 
        'file_type': 'input_file', 
        'path_exe': 'C:/Simulations/_Exe/SESV6_32.exe'}

    app = App(settings)
    app.mainloop()
    print('app.mainloop finished')