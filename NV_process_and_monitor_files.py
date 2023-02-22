'''This code processes and monitor multiple files'''

import tkinter as tk
from tkinter import ttk, messagebox
import multiprocessing
import time
import os
import threading
import random
import copy

VERSION_NUMBER = "1"
UPDATE_FREQUENCY = 1000 #vALUE IN MILLISECONDS
DELAY = 2 #Seconds for delay

def fake_processing_9(queued_list, processing_dictionary, done_list, pause_value, name):
    pid = os.getpid()
    queued_list.remove(name)
    processing_dictionary[pid] = (name, "Processing", "Processing", "Processing", "Processing")
    pause_check(pause_value)
    delay = DELAY * random.random()
    time.sleep(delay)
    processing_dictionary[pid] = (name, "Done", "Done", "Done", "Done")
    done_list.append(name)
    print(f"Finished {name}")

def pause_check(pause_value):
    while pause_value.get() == 1:
        time.sleep(1.0)
    return

class Manager_Class:
    def __init__(self):
        self.manager = multiprocessing.Manager()
        self.shared_dict = self.manager.dict()
        self.processing_dictionary = self.manager.dict()
        self.queued_files = self.manager.list()
        self.done_files = self.manager.list()
        self.pause_value = self.manager.Value("i",0)
        self.finished = self.manager.Value("i",0)
        self.file_names = self.manager.list()
        #Initially create file names
        for i in range(1, 100):
            self.file_names.append("file_"+str(i))
            self.queued_files.append("file_"+str(i))
        print('finished initalizing variables')

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        #self.manager = Manager_Class()
        self.geometry('300x200')
        self.title('Main Window')
        # place a button on the root window
        ttk.Button(self,
                text='Open a window',
                command=self.open_window).pack(expand=True)

    def open_window(self):
        manager = Manager_Class()
        window = Monitor_GUI(self, manager)
        window.focus_force()
        window.grab_set()

class Monitor_GUI(tk.Toplevel):
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager
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
        self.queued_list = tk.Listbox(self.queue_frame, yscrollcommand=self.queued_scrollbar.set, listvariable=self.queued_list_var)
        self.queued_scrollbar.config(command = self.queued_list.yview)
        self.queued_list.pack(side='left', fill='both')
        # Create processing table
        self.processing_frame = ttk.LabelFrame(
            self.monitor_window, borderwidth=5, text="Processing", padding=p
        )
        headers = ("PID", "File", "Simulation", "Read Output", "Excel", "Visio")
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
        self.start_text = tk.StringVar()
        self.start_text.set("Start")
        self.btn_start = ttk.Button(
            button_frame, textvariable=self.start_text, command=self.seperate_thread, width=20
        )
        #Draw Item
        self.btn_pause.grid(column=2, row=1)
        self.btn_start.grid(column=3, row=1)
        # Draw grid
        self.monitor_window.grid(column=1, row=1, sticky="EWNS")
        self.queue_frame.grid(column=5,row=10, sticky='NS')
        self.processing_frame.grid(column=10, row=10, sticky='N')
        self.done_frame.grid(column=15,row=10, sticky='NS')
        button_frame.grid(column=10, row=100)
        self.after(UPDATE_FREQUENCY, self.update_monitor_window)

    def update_processing(self):
        row_number = 20
        for key, values in self.manager.processing_dictionary.items():
            column_number = 10
            self.entry = tk.Entry(
                self.processing_frame, width=self.c_width, fg="blue", font=("Arial", self.font_size, "")
            )
            self.entry.grid(row=row_number, column=column_number)
            self.entry.insert(tk.END, key)
            column_number += 10
            #TODO Update color and fonts based on status
            for value in values:
                self.entry = tk.Entry(
                    self.processing_frame, width=self.c_width, fg="blue", font=("Arial", self.font_size, "")
                )
                self.entry.grid(row=row_number, column=column_number)
                self.entry.insert(tk.END, value)
                column_number += 10
            row_number += 10

    def update_monitor_window(self):
        #Update the queued and done list in the tkinter application
        self.queued_list_var.set(list(self.manager.queued_files))
        self.done_list_var.set(list(self.manager.done_files))
        #Update the processing dictionary
        self.update_processing()
        #app.update()
        self.update()
        self.after(UPDATE_FREQUENCY, self.update_monitor_window)

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
        self.t1=threading.Thread(target=self.processing_pool_3, daemon=True)
        self.t1.start()

    def processing_pool_3(self):
        #TODO Need to adjust. It runs after other processes are finished :(
        print('Getting ready to start the pool')
        local_file_names = copy.copy(list(self.manager.file_names))
        num_of_processes = max(multiprocessing.cpu_count() - 1, 1)
        num_of_processes = min(num_of_processes, len(local_file_names))
        num_of_processes = 2 #TEMP override during code creation
        self.pool = multiprocessing.Pool(num_of_processes)
        print('about to do the loop')
        with multiprocessing.Pool(num_of_processes) as pool:
            for name in local_file_names:
                self.pool.apply_async(fake_processing_9, args=(self.manager.queued_files, self.manager.processing_dictionary, self.manager.done_files, self.manager.pause_value, name, ))
            self.pool.close()
            self.pool.join()
        print('Processing pool finished')

    def on_closing(self):
        # Try to pause ongoing processes
        self.manager.pause_value.value = 1
        self.pause_text.set("Continue")
        # Create window
        title_on_closing = "Stop processing immediately?"
        msg_1 = "Click 'Yes' to quit immediately (could).\n"
        msg_2 = "Click 'No' to continue.\n"
        #msg_3 = "Click 'Cancel' to continue processing.\n"
        msg_all = msg_1 + msg_2 #+ msg_3
        #answer = messagebox.askokcancel("Quit", "Do you want to quit Next-Vis?")
        answer = messagebox.askyesno(title=title_on_closing, message = msg_all)
        if answer: #Yes
            self.pool.terminate()
            self.pool.join()
            self.destroy()
        else:
            self.manager.pause_value.value = 0
            self.pause_text.set("Pause")
            return

if __name__ == "__main__":
    app = App()
    app.mainloop()
    print('app.mainloop finished')