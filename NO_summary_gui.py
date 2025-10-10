# Project Name: Next-Out
# Description: GUI for selecting summary options
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

import os
import pickle
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from NO_constants import VERSION_NUMBER
import NO_summary

class Summary_Screen(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.transient(parent)  # Make window transient
        self.grab_set()  # Make window modal
        # Initialization and settings
        p = "3"  # padding
        py = "3"  # vertical padding
        px = "3"
        self.title("Next-Out Summary " + VERSION_NUMBER)
        style = ttk.Style()
        style.theme_use('winnative')
        
        # Set window position relative to parent
        if parent:
            x = parent.winfo_x() + 50
            y = parent.winfo_y() + 50
            self.geometry(f"+{x}+{y}")
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        # Create the main frame
        self.ss = ttk.Frame(self, padding=p)  # start screen
        self.ss.grid(row=0, column=0, sticky="nsew")
        
        # Configure window grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Main Frame
        frame_segments = ttk.LabelFrame(
            self.ss, borderwidth=5, text="Segments to Process", padding=p
        )
        frame_segments.columnconfigure(0, weight=1)  # Make the column expandable
        
        # Initialize settings variables
        self.load_settings()
        
        # Segment frame options
        cb_fire = ttk.Checkbutton(
            frame_segments, text="Fire Segment", variable=self.cbo_fire, 
            onvalue="Fire", offvalue=""
        )
        cb_segments = ttk.Checkbutton(
            frame_segments, text="Segments", variable=self.cbo_segments,
            onvalue="Segments", offvalue="", command=self.toggle_numbers_entry
        )
        
        # Numbers entry field
        lbl_numbers = ttk.Label(frame_segments, text="Enter segement numbers separated by commas:")
        self.numbers_entry = ttk.Entry(frame_segments, width=40)

        # Segments grid
        cb_fire.grid(column=0, row=0, sticky="W", pady=py)
        cb_segments.grid(column=0, row=1, sticky="W", pady=py)
        lbl_numbers.grid(column=0, row=2, sticky="W", pady=py)
        self.numbers_entry.grid(column=0, row=3, sticky="EW", pady=py, padx=px)
        
        # Submit button
        frm_run = ttk.Frame(self.ss, padding=p, borderwidth=5)
        self.btn_submit = tk.Button(
            frm_run,
            text="Submit",
            command=self.submit,
            bg="#0C0A0A",
            fg="white",
            activebackground="#222222",
            activeforeground="white"
        )
        self.btn_submit.pack(expand=True, fill=tk.BOTH)
        

        
        # START SCREEN grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.ss.grid(column=0, row=0, sticky="EWNS")
        self.ss.columnconfigure(0, weight=1)

        # Grid layout
        self.ss.rowconfigure(0, weight=1)  # Segments frame
        self.ss.rowconfigure(1, weight=0)  # Submit button

        # Place frames
        frame_segments.grid(column=0, row=0, sticky=["NSEW"], pady=py, padx=px)
        frm_run.grid(column=0, row=1, sticky="WE", pady=py, padx=px)
        
        # Initialize numbers entry state
        self.toggle_numbers_entry()

    def toggle_numbers_entry(self):
        """Enable or disable the numbers entry field based on Segments checkbox state"""
        if self.cbo_segments.get() == "Segments":
            self.numbers_entry.configure(state="normal")
        else:
            self.numbers_entry.configure(state="disabled")

    def load_settings(self):
        # Define all variables and default values for GUI
        self.screen_settings = {
            "self.cbo_fire": 'tk.StringVar(value="")',
            "self.cbo_segments": 'tk.StringVar(value="")',
            "self.numbers_entry_value": 'tk.StringVar(value="")',
        }
        
        for key, value in self.screen_settings.items():
            exec(f"{key} = {value}")
            
        try:
            settings_file_name = "NO_summary_settings.ini"
            path_of_file = Path(settings_file_name)
            if path_of_file.is_file():
                with open(settings_file_name, "rb") as f:
                    load_gui_settings = pickle.load(f)
                for key, value in load_gui_settings.items():
                    if value != "":
                        exec(f'{key} = tk.StringVar(value="{value}")')
        except:
            msg = "Error loading settings"
            messagebox.showinfo(message=msg)

    def submit(self, *args):
        self.btn_submit["text"] = "Processing..."
        self.btn_submit["state"] = tk.DISABLED
        self.ss.update()
        
        # Get selected options
        segments_list = []
        if self.cbo_fire.get():
            segments_list.append("Fire")
        if self.cbo_segments.get():
            segments_list.append("Segments")
            
        if not segments_list:
            messagebox.showinfo(message="Please select at least one segment type")
            self.btn_submit["state"] = tk.NORMAL
            self.btn_submit["text"] = "Submit"
            return
            
        try:
            # Create summary options dictionary
            summary_options = {}
            
            # Handle fire data
            if self.cbo_fire.get():
                summary_options['lookup_fire_data'] = True
            else:
                summary_options['lookup_fire_data'] = False
                
            # Handle segment numbers
            if self.cbo_segments.get():
                # Get numbers from entry field
                numbers_text = self.numbers_entry.get().strip()
                if numbers_text:
                    try:
                        # Split by comma and convert to integers
                        segment_numbers = [int(num.strip()) for num in numbers_text.split(',')]
                        summary_options['segment_numbers_2_lookup'] = segment_numbers
                    except ValueError:
                        raise ValueError("Invalid segment numbers format. Please enter numbers separated by commas.")
                else:
                    raise ValueError("Please enter segment numbers when Segments is selected.")
            
            # Store the options and close the window
            self.summary_options = summary_options
            self.destroy()
            return
          
        # Store the options and close the window
            self.summary_options = summary_options
            self.destroy()
            return
          
        except Exception as e:
            messagebox.showerror("Error", f"Error processing segments: {str(e)}")
            
        self.btn_submit["state"] = tk.NORMAL
        self.btn_submit["text"] = "Submit"

def launch_window(parent=None):
    summary_screen = Summary_Screen(parent)
    summary_screen.wait_window()
    return getattr(summary_screen, 'summary_options', {})

if __name__ == "__main__":
    settings = {
        'ses_output_str': [
            'C:/Simulations/Test/PT09-S1GM-011-R01.no',
            'C:/Simulations/Test/PT09-S1GM-012-F-R01.no',
            'C:/Simulations/Test/PT09-S1GM-012-R01.no'
        ],
        'segment_numbers_2_lookup': [2, 4],
        'segment_data_2_lookup': ["SSA"],
        'fire_data_2_lookup': True,
        'sim_time': -1,
        'results_folder_str': 'C:/Simulations/Test',
        'output_filename': 'summary_results.xlsx'
    }
    launch_window()