# Project Name: Next-Out
# Description: Performs multiple simulations and post-processing simutaneously. Display progress in a graphical user interface.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

import logging
import multiprocessing
import os
import subprocess
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

import NO_Excel_R01 as nve
import NO_parser
import NO_route
import NO_visio
import NO_file_tools
import NO_file_tools
import NO_average
import NO_summary
from NO_constants import VERSION_NUMBER
import NO_multifile_progress_bar as progress_tracker

# logging.disable(logging.CRITICAL)
logging.basicConfig(
    level=logging.DEBUG, format=" %(asctime)s -  %(levelname)s -  %(message)s"
)

UPDATE_FREQUENCY = 200  # vALUE IN MILLISECONDS
#COLUMN_HEADERS = ("PID", "File", "Simulation", "Read Output", "Visio", "Excel", "Route")
DEFAULT_WIDTH = 10
COLUMN_HEADERS_AND_WIDTH = {
    "PID": DEFAULT_WIDTH ,
    "File": 20,
    "Simulation": DEFAULT_WIDTH , 
    "Read Output": DEFAULT_WIDTH ,
    "Visio": DEFAULT_WIDTH ,
    "Excel": DEFAULT_WIDTH ,
    "Route": DEFAULT_WIDTH 
}
STATUS_FONT_COLOR = {
    "-": "black",
    "Queued": "blue",
    "Processing": "orange",
    "Done": "green",
    "Failed": "red",
}

def single_process(
    file_path,
    process_settings,
    settings,
    queued_list,
    processing_dictionary,
    done_list,
    pause_value,
    H5_file_paths,
    error_messages
):
    pause_check(pause_value)
    # Prepare to monitor process status
    name = file_path.stem
    queued_list.remove(name)
    pid = os.getpid()
    value_index = process_settings["process_status_value_index"]
    process_status = process_settings["process_status_start_values"]
    process_status[value_index["name"]] = name
    processing_dictionary[pid] = process_status
    # Start processing files
    # Perform simulation if necessary
    if process_settings["Simulation"]:
        pause_check(pause_value)
        process_status[value_index["Simulation"]] = "Processing"
        processing_dictionary[pid] = process_status
        logging.info(f"Staring SES simlaution of {name}")
        successful_simulation = run_SES(settings["path_exe"], file_path.__str__())
        if successful_simulation:
            # Change file path to work on the output file
            file_path = NO_file_tools.output_from_input(file_path, settings["path_exe"])
        else:
            logging.info(f"SES simulation failed for {name}")
            error_messages.append(f"{name}: SES simulation failed")
            process_status[value_index["Simulation"]] = "Failed"
            processing_dictionary[pid] = process_status
            return
        logging.info(f"Finished running SES Simualtion {name}")
        process_status[value_index["Simulation"]] = "Done"
        processing_dictionary[pid] = process_status
    # Parse output file or read data from NO File
    if process_settings["Read Output"]:
        pause_check(pause_value)
        try:
            pause_check(pause_value)
            logging.info(f"Parsing {name}")
            process_status[value_index["Read Output"]] = "Processing"
            processing_dictionary[pid] = process_status
            if settings["file_type"] == "H5_file":
                # Read data from NO file
                data, output_meta_data = NO_file_tools.read_h5_file(file_path)
                # Create a list of NO Files for averaging
                H5_file_paths.append(file_path) 
            else:
                #Parse the data from the output file
                data, output_meta_data = NO_parser.parse_file(
                    file_path, gui="", conversion_setting=settings["conversion"]
                )
                #Create NO File if it is an output
                if "H5_file" in settings["output"] or "Average" in settings["output"]:
                    try:
                        NO_file_tools.save_h5_file(data, output_meta_data, settings)
                        logging.info(f"Created H5 File for {name}")
                        # Create a list of H5 Files for averaging
                        H5_file_path = NO_file_tools.get_results_path2(output_meta_data, ".H5")
                        H5_file_paths.append(H5_file_path)
                        logging.info(f"Finished saving {H5_file_path}")
                    except Exception as e:
                        logging.error(f"Error creating H5 File for {name}: {str(e)}")
            process_status[value_index["Read Output"]] = "Done"
            processing_dictionary[pid] = process_status
            logging.info(f"Finished Parsing {name}")
        except Exception as e:
            process_status[value_index["Read Output"]] = "Failed"
            error_messages.append(f"{name}: Error parsing file - {str(e)}")
            logging.info(f"Error Parsing {name}: {str(e)}")
            return

    if process_settings["Visio"]:
        pause_check(pause_value)
        try:
            process_status[value_index["Visio"]] = "Processing"
            processing_dictionary[pid] = process_status
            logging.info(f"Staring to create Visio file for {name}")
            NO_visio.create_visio(settings, data, output_meta_data, gui="")
            logging.info(f"Finished writing Visio file for {name}")
            process_status[value_index["Visio"]] = "Done"
            processing_dictionary[pid] = process_status
        except Exception as e:
            process_status[value_index["Visio"]] = "Failed"
            error_messages.append(f"{name}: Error creating Visio - {str(e)}")
            logging.info(f"Error writing Visio file for {name}: {str(e)}")
    if process_settings["Excel"]:
        pause_check(pause_value)
        try:
            process_status[value_index["Excel"]] = "Processing"
            processing_dictionary[pid] = process_status
            logging.info(f"Staring to create Excel file for {name}")
            nve.create_excel(settings, data, output_meta_data, gui="")
            logging.info(f"Finished writing Excel file for {name}")
            process_status[value_index["Excel"]] = "Done"
            processing_dictionary[pid] = process_status
        except Exception as e:
            process_status[value_index["Excel"]] = "Failed"
            error_messages.append(f"{name}: Error creating Excel - {str(e)}")
            logging.info(f"Error writing Excel file for {name}: {str(e)}")
    if process_settings["Route"]:
        pause_check(pause_value)
        try:
            process_status[value_index["Route"]] = "Processing"
            processing_dictionary[pid] = process_status
            logging.info(f"Staring to create Route file for {name}")
            NO_route.create_route_excel(settings, data, output_meta_data, gui="")
            logging.info(f"Finished writing Route file for {name}")
            process_status[value_index["Route"]] = "Done"
            processing_dictionary[pid] = process_status
        except Exception as e:
            process_status[value_index["Route"]] = "Failed"
            error_messages.append(f"{name}: Error creating Route - {str(e)}")
            logging.info(f"Error creating Route Excel file for {name}: {str(e)}")
    done_list.append(name)
    logging.info(f"Finished processing {name}")


def run_SES(ses_exe_path, ses_input_file_path, gui=""):
    try:
        # Check the proces is successful, see https://realpython.com/python-subprocess/
        subprocess.run(
            [ses_exe_path, ses_input_file_path],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return True
    except FileNotFoundError as exc:
        logging.info(
            f"Process failed because the executable could not be found.\n{exc}"
        )
        return False
    except subprocess.CalledProcessError as exc:
        if exc.returncode == 100:
            return True
        else:
            msg = f"SES Simulation failed." f"Returned {exc.returncode}\n{exc}"
            logging.info(msg)
            return False
    except:
        return False


def pause_check(pause_value):
    while pause_value.get() == 1:
        time.sleep(1.0)
    return


class Manager_Class:
    def __init__(self):
        logging.debug("Start of manager class")
        self.manager = multiprocessing.Manager()
        self.shared_dict = self.manager.dict()
        self.processing_dictionary = self.manager.dict()
        self.queued_files = self.manager.list()
        self.done_files = self.manager.list()
        self.error_messages = self.manager.list()  # Track errors
        self.pause_value = self.manager.Value("i", 0)
        self.finished = self.manager.Value("i", 0)
        self.file_names = self.manager.list()
        self.no_file_paths = self.manager.list() #List of NO files created for averaging

class Monitor_GUI(tk.Toplevel):
    def __init__(self, parent, manager, start_screen_settings):
        super().__init__(parent)
        self.manager = manager
        self.settings = start_screen_settings
        self.create_process_settings()  # Create settings for processing
        self.in_progress = True
        p = "5"  # padding
        self.title("Next-Out " + VERSION_NUMBER + " Monitor")
        
        # Set window icon
        try:
            from pathlib import Path
            import sys
            if getattr(sys, 'frozen', False):
                icon_path = Path(sys._MEIPASS) / 'NO_Icon.ico'
            else:
                icon_path = Path(__file__).parent / 'NO_Icon.ico'
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except:
            pass
        self.c_width = 15
        self.font_size = 12
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Establish base frame to draw monitor
        self.monitor_window = ttk.Frame(self, padding=p, borderwidth=5)
        # Queued List
        self.queue_frame = ttk.LabelFrame(
            self.monitor_window, borderwidth=5, text="Queued (0)", padding=p
        )
        self.queued_scrollbar = ttk.Scrollbar(self.queue_frame)
        self.queued_scrollbar.pack(side="right", fill="y")
        self.queued_list_var = tk.Variable(value=[])  # Start with blank value
        self.queued_list_var.set(list(self.manager.queued_files))
        self.queued_list = tk.Listbox(
            self.queue_frame,
            yscrollcommand=self.queued_scrollbar.set,
            listvariable=self.queued_list_var,
        )
        self.queued_scrollbar.config(command=self.queued_list.yview)
        self.queued_list.pack(side="left", fill="both")
        # Create processing table
        self.processing_frame = ttk.LabelFrame(
            self.monitor_window, borderwidth=5, text="Processing (0)", padding=p
        )
        headers = list(COLUMN_HEADERS_AND_WIDTH.keys())
        column_number = 10
        self.column_width = {}
        for header in headers:
            self.entry = tk.Entry(
                self.processing_frame,
                width=COLUMN_HEADERS_AND_WIDTH[header],
                bg="DarkOrange1",
                fg="Black",
                font=("Arial", self.font_size),
            )
            self.entry.grid(row=10, column=column_number)
            self.entry.insert(tk.END, header)
            self.column_width[column_number] = COLUMN_HEADERS_AND_WIDTH[header]
            column_number += 10
        # Done List
        self.done_frame = ttk.LabelFrame(
            self.monitor_window, borderwidth=5, text="Done (0)", padding=p
        )
        self.done_scrollbar = ttk.Scrollbar(self.done_frame)
        self.done_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.done_list_var = tk.Variable(value=[])  # Start with blank value
        self.done_list = tk.Listbox(
            self.done_frame,
            yscrollcommand=self.done_scrollbar.set,
            listvariable=self.done_list_var,
        )
        self.done_scrollbar.config(command=self.done_list.yview)
        self.done_list.pack(side=tk.LEFT, fill=tk.BOTH)

        # Error Log Frame
        self.error_frame = ttk.LabelFrame(
            self.monitor_window, borderwidth=5, text="Errors", padding=p
        )
        self.error_scrollbar = ttk.Scrollbar(self.error_frame)
        self.error_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.error_text = tk.Text(
            self.error_frame,
            width=60,
            height=6,
            state=tk.DISABLED,
            wrap="word",
            yscrollcommand=self.error_scrollbar.set,
            fg="red",
            font=("Arial", 9)
        )
        self.error_scrollbar.config(command=self.error_text.yview)
        self.error_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Progress Bar Frame
        progress_frame = ttk.LabelFrame(
            self.monitor_window, borderwidth=5, text="Overall Progress", padding=p
        )
        self.progress_label = ttk.Label(
            progress_frame, 
            text="0/0 tasks (0%)",
            font=("Arial", 10)
        )
        self.progress_label.pack(pady=5)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            length=400,
            mode="determinate",
            maximum=100
        )
        self.progress_bar.pack(pady=5, fill="x", expand=True)

        # Pause and stop buttons
        button_frame = ttk.LabelFrame(
            self.monitor_window, borderwidth=5, text="Control", padding=p
        )
        self.pause_text = tk.StringVar()
        self.pause_text.set("Pause")
        self.btn_pause = ttk.Button(
            button_frame,
            textvariable=self.pause_text,
            command=self.pause_press,
            width=20,
        )
        """ Previous code for a start button
        self.start_text = tk.StringVar()
        self.start_text.set("Start")
        self.btn_start = ttk.Button(
            button_frame, textvariable=self.start_text, command=self.seperate_thread, width=20
        )
        self.btn_start.grid(column=3, row=1)"""
        # Draw Item
        self.btn_pause.grid(column=2, row=1)
        # Draw grid
        self.monitor_window.grid(column=1, row=1, sticky="EWNS")
        self.queue_frame.grid(column=5, row=10, sticky="NS")
        self.processing_frame.grid(column=10, row=10, sticky="N")
        self.done_frame.grid(column=15, row=10, sticky="NS")
        progress_frame.grid(column=5, row=40, columnspan=11, sticky="EW", pady=5)
        self.error_frame.grid(column=5, row=50, columnspan=11, sticky="EW", pady=10)
        button_frame.grid(column=10, row=100)
        
        # Initialize progress tracker
        num_files = len(self.settings["ses_output_str"])
        self.progress_tracker = progress_tracker.ProgressTracker(
            num_files, 
            self.process_settings
        )
        
        self.seperate_thread()
        self.after(UPDATE_FREQUENCY, self.update_monitor_window)

    def update_monitor_table(self):
        # Update the queued and done list in the tkinter application, manager
        queued_files = list(self.manager.queued_files)
        done_files = list(self.manager.done_files)
        
        # Count dictionary items that contain "Processing" or "Queued"
        processing_count = 0
        for pid, status_list in self.manager.processing_dictionary.items():
            if "Processing" in status_list or "Queued" in status_list:
                processing_count += 1
        
        self.queued_list_var.set(queued_files)
        self.done_list_var.set(done_files)
        
        # Update frame labels with counts
        self.queue_frame.config(text=f"Queued ({len(queued_files)})")
        self.processing_frame.config(text=f"Processing ({processing_count})")
        self.done_frame.config(text=f"Done ({len(done_files)})")
        
        # Update error log
        self.update_error_log()
        # Update progress bar
        self.update_progress_bar()
        row_number = 20
        for key, values in self.manager.processing_dictionary.items():
            column_number = 10
            self.entry = tk.Entry(
                self.processing_frame,
                width=self.column_width[column_number],
                fg="blue",
                font=("Arial", self.font_size, ""),
            )
            self.entry.grid(row=row_number, column=column_number)
            # First entry is the PID for the process
            self.entry.insert(tk.END, key)
            column_number += 10
            # Update the status of the process for the PID
            for value in values:
                font_color_text = STATUS_FONT_COLOR.get(value, "black")
                self.entry = tk.Entry(
                    self.processing_frame,
                    width=self.column_width[column_number],
                    fg=font_color_text,
                    font=("Arial", self.font_size, ""),
                )
                self.entry.grid(row=row_number, column=column_number)
                self.entry.insert(tk.END, value)
                column_number += 10
            row_number += 10

    def update_error_log(self):
        """Update the error text widget with new errors"""
        current_errors = list(self.manager.error_messages)
        if current_errors:
            self.error_text["state"] = tk.NORMAL
            self.error_text.delete("1.0", tk.END)
            for error in current_errors:
                self.error_text.insert(tk.END, f"• {error}\n")
            self.error_text["state"] = tk.DISABLED
    
    def update_progress_bar(self):
        """Update progress bar based on current processing status"""
        # Calculate completed work from processing dictionary
        completed = progress_tracker.calculate_progress_from_status(
            self.manager.processing_dictionary,
            self.process_settings["process_status_value_index"]
        )
        
        # Update the progress tracker
        self.progress_tracker.completed_work_units = completed
        
        # Update progress bar value
        percentage = self.progress_tracker.get_progress_percentage()
        self.progress_bar["value"] = percentage
        
        # Update progress label text
        progress_text = self.progress_tracker.get_progress_text()
        self.progress_label.config(text=progress_text)

    def update_monitor_window(self):
        if self.in_progress:
            # Update the processing dictionary
            self.update_monitor_table()
            self.update()
            self.after(UPDATE_FREQUENCY, self.update_monitor_window)
        else:
            return

    def pause_press(self):
        print("Clicked Pause")
        if self.pause_text.get() == "Pause":
            self.manager.pause_value.value = 1
            self.pause_text.set("Continue")
        else:
            self.manager.pause_value.value = 0
            self.pause_text.set("Pause")

    def seperate_thread(self):
        print("Starting a single thread to control the processing pool")
        self.t1 = threading.Thread(target=self.processing_pool, daemon=True)
        self.t1.start()

    def processing_pool(self):
        logging.info("Getting ready to start the pool")
        num_files = len(self.settings["ses_output_str"])
        # Use all processors except 1
        num_of_processes = max(multiprocessing.cpu_count() - 1, 1)
        num_of_processes = min(num_of_processes, num_files)
        logging.info("Starting loop for multiprocesing")
        with multiprocessing.Pool(num_of_processes) as self.pool:
            self.results = []
            for file_path in self.file_paths:
                result = self.pool.apply_async(
                    single_process,
                    args=(
                        file_path,
                        self.process_settings,
                        self.settings,
                        self.manager.queued_files,
                        self.manager.processing_dictionary,
                        self.manager.done_files,
                        self.manager.pause_value,
                        self.manager.no_file_paths,
                        self.manager.error_messages
                    ),
                )
                self.results.append(result)
            self.pool.close()
            self.pool.join()
        logging.info("Processing Pool finished")
        # Message that this finished.
        # This stops the self-updating process.
        self.update_monitor_window()
        self.update()
        self.in_progress = False
        # Average results from NO Files
        if "Average" in self.settings["output"]: 
            # Update progress label to show post-processing
            self.progress_label.config(text="Post-processing: Creating average output...")
            self.update()
            try:
                unsorted_no_file_paths = list(self.manager.no_file_paths)
                no_file_paths = sorted(unsorted_no_file_paths)
                logging.info(f"NO File Paths: {list(self.manager.no_file_paths)}")
                self.settings["ses_output_str"] = no_file_paths
                NO_average.average_outputs(self.settings, gui="")
            except Exception as e:
                error_msg = f"CRITICAL: Error with averaging - {str(e)}"
                self.manager.error_messages.append(error_msg)
                self.update_error_log()
                self.wm_attributes("-topmost", -1)
                messagebox.showerror(
                    title="Averaging Error",
                    message=f"Failed to create average output:\n\n{str(e)}",
                    parent=self
                )
        if "Summary" in self.settings["output"]:
            # Update progress label to show post-processing
            self.progress_label.config(text="Post-processing: Creating summary output...")
            self.update()
            try:
                NO_summary.create_excel_summary(self.settings, gui="")
            except Exception as e:
                error_msg = f"CRITICAL: Error creating summary - {str(e)}"
                self.manager.error_messages.append(error_msg)
                self.update_error_log()
                self.wm_attributes("-topmost", -1)
                messagebox.showerror(
                    title="Summary Error",
                    message=f"Failed to create summary output:\n\n{str(e)}",
                    parent=self
                )
        
        # Set progress to 100% when completely done
        self.progress_bar["value"] = 100
        self.progress_tracker.completed_work_units = self.progress_tracker.total_work_units
        self.progress_label.config(text=f"Complete! {self.progress_tracker.get_progress_text()}")
        # Determine completion message based on errors
        error_count = len(list(self.manager.error_messages))
        if error_count > 0:
            title_msg = f"Post-processing complete with {error_count} error(s)"
            msg_1 = f"Processing finished with {error_count} error(s).\n"
            msg_2 = "Check the 'Errors' section above for details.\n\n"
            msg_3 = "Click 'Okay' to return to main screen."
            msg_all = msg_1 + msg_2 + msg_3
            msg_type = messagebox.showwarning
        else:
            title_msg = "Post-processing complete."
            msg_1 = "All files processed successfully!\n\n"
            msg_2 = "Click 'Okay' to return to main screen."
            msg_all = msg_1 + msg_2
            msg_type = messagebox.showinfo
        
        # Make message box appear above the status window using code from https://stackoverflow.com/questions/52345195/getting-tkinter-messagebox-at-top-of-the-screen-in-python
        self.wm_attributes("-topmost", -1)
        msg_type(title=title_msg, message=msg_all, parent=self)
        self.destroy()

    def create_process_settings(self):
        settings = self.settings
        self.process_settings = {}
        # Determine if an SES Simulation needs to be performed
        if settings["file_type"] in ["input_file"]:
            self.process_settings["Simulation"] = True
        else:
            self.process_settings["Simulation"] = False
        # Requirement for read_output to be performed
        if settings["file_type"] == "output_file":
            self.process_settings["Read Output"] = True
        elif "H5_file" in settings["output"]:
            self.process_settings["Read Output"] = True
        else:
            self.process_settings["Read Output"] = False
        # Determine what processes are needed after parsing the file
        post_read_processes = ["Visio", "Excel", "Route"]
        for process_name in post_read_processes:
            setting_selected = process_name in settings["output"]
            self.process_settings[process_name] = setting_selected
            # Turn on Read Output if any post-processing is required
            if setting_selected and not self.process_settings["Read Output"]:
                self.process_settings["Read Output"] = True
        # Determine staring values for process_dictionary. A list and index is used because this assumed to be faster than a dictionary
        process_status_start_values = []
        process_status_value_index = {}
        process_status_start_values.append("name")  # holding spot for name
        i = 0  # starting value for index
        process_status_value_index["name"] = i
        for key, value in self.process_settings.items():
            i += 1
            if value:
                status = "Queued"
            else:
                status = "-"
            process_status_start_values.append(status)
            process_status_value_index[key] = i
        self.process_settings[
            "process_status_start_values"
        ] = process_status_start_values
        self.process_settings["process_status_value_index"] = process_status_value_index
        # Create list of file paths and start queue with names
        self.file_paths = []
        for value in self.settings["ses_output_str"]:
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
        # msg_3 = "Click 'Cancel' to continue processing.\n"
        msg_all = msg_1 + msg_2  # + msg_3
        answer = messagebox.askyesno(title=title_on_closing, message=msg_all)
        # TODO Exit if pool is already.
        if answer:  # Yes
            self.in_progress = False
            # Check if any results are still pending
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
        self.geometry("300x200")
        self.title("Main Window")
        
        # Set window icon
        try:
            from pathlib import Path
            import sys
            if getattr(sys, 'frozen', False):
                icon_path = Path(sys._MEIPASS) / 'NO_Icon.ico'
            else:
                icon_path = Path(__file__).parent / 'NO_Icon.ico'
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except:
            pass
        
        # place a button on the root window
        ttk.Button(
            self, text="Start processes and monitor", command=self.open_window
        ).pack(expand=True)

    def open_window(self):
        manager = Manager_Class()
        window = Monitor_GUI(self, manager, self.settings)
        window.focus_force()
        window.grab_set()

if __name__ == "__main__":
    # Main code copied from NV_GUi
    settings={
        'ses_output_str': ['C:\\Simulations\\2023-12-28\\Next-In 3p1 lite.xlsm'],
        'visio_template': 'C:/Simulations/1p31 Testing/Next Vis Samples1p21.vsdx',
        'simtime': -1,
        'conversion': '',
        'output': ['', '', '', '', '', '', '', '', ''], 
        'file_type': 'next_in',
        'path_exe': 'C:/Simulations/_Exe/SESV6_32.exe', 
        'next_in_ses_version': 'SI', 
        'next_in_option': 'Iterations', 
        'next_in_single_file_name': 'test001',
        'run_ses_next_in': 'run_ses', 
        'iteration_worksheets': ['Iteration'],
        'summary_name': 'summary',
    }
    app = App(settings)
    app.mainloop()
    print("app.mainloop finished")
