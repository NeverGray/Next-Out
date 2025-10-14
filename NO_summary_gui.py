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

class Summary_Screen(tk.Toplevel):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.transient(parent)  # Make window transient
        self.grab_set()  # Make window modal
        
        # Store the original settings to preserve them
        self.settings = settings if settings else {}
        
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
        self.cbo_fire = tk.StringVar(value="")

        # Segment frame options
        cb_fire = ttk.Checkbutton(
            frame_segments, text="Fire Segment", variable=self.cbo_fire, 
            onvalue="Fire", offvalue=""
        )
        
        # Numbers entry field
        lbl_numbers = ttk.Label(frame_segments, text="Enter segment numbers separated by commas.\n Leave for fire segment only:")
        self.numbers_entry = ttk.Entry(frame_segments, width=40)

        # Load existing summary options if provided
        self.load_summary_options(settings)

        # Segments grid
        cb_fire.grid(column=0, row=0, sticky="W", pady=py)
        lbl_numbers.grid(column=0, row=1, sticky="W", pady=py)
        self.numbers_entry.grid(column=0, row=2, sticky="EW", pady=py, padx=px)
        
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

    def load_summary_options(self, settings):
        """
        Populate the GUI with existing summary options if provided.
        """
        # Check if settings exists and is not None
        if not settings:
            return
        
        # Set fire checkbox
        if settings.get('lookup_fire_data', False):
            self.cbo_fire.set("Fire")
        
        # Set segment numbers
        if 'segments_2_lookup' in settings:
            segment_numbers = settings['segments_2_lookup']
            # Convert list to comma-separated string
            numbers_str = ', '.join(map(str, segment_numbers))
            self.numbers_entry.delete(0, tk.END)
            self.numbers_entry.insert(0, numbers_str)

    def submit(self, *args):
        self.btn_submit["text"] = "Processing..."
        self.btn_submit["state"] = tk.DISABLED
        self.ss.update()
        
        # Get selected options
        segments_list = []
        if self.cbo_fire.get():
            segments_list.append("Fire")
        
        # Check if segment numbers are entered
        numbers_text = self.numbers_entry.get().strip()
        if numbers_text:
            segments_list.append("Segments")
        
        try:      
            # Update settings with fire data
            self.settings['lookup_fire_data'] = bool(self.cbo_fire.get())
            
            # Update settings with segment numbers
            if numbers_text:
                try:
                    # Split by comma and convert to integers
                    segment_numbers = [int(num.strip()) for num in numbers_text.split(',')]
                    self.settings['segments_2_lookup'] = segment_numbers
                except ValueError:
                    raise ValueError("Invalid segment numbers format. Please enter numbers separated by commas.\n")
            else:
                # Remove segments_2_lookup if no numbers entered
                self.settings.pop('segments_2_lookup', None)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error processing segments summary: {str(e)}")
            self.btn_submit["state"] = tk.NORMAL
            self.btn_submit["text"] = "Submit"
            return

        self.btn_submit["state"] = tk.NORMAL
        self.btn_submit["text"] = "Submit"
        self.destroy()
        return         

def launch_window(parent=None, settings=None):
    summary_screen = Summary_Screen(parent, settings)
    summary_screen.wait_window()
    # Return the updated settings
    return summary_screen.settings

if __name__ == "__main__":
    import NO_summary
    settings = {'conversion': '',
    'file_type': 'no_file',
    'output': ['', '', 'Summary', '', '', '', '', '', '', ''],
    'path_exe': '',
    'results_folder_str': None,
    'ses_output_str': ['C:/Simulations/Test\\PT09-S1GM-011-R01.no',
                        'C:/Simulations/Test\\PT09-S1GM-012-F-R01.no',
                        'C:/Simulations/Test\\PT09-S1GM-012-R01.no',
                        'C:/Simulations/Test\\PT09-S1GM-012-WG-F-R01.no',
                        'C:/Simulations/Test\\PT09-S1GM-012-WM-F-R01.no',
                        'C:/Simulations/Test\\PT09-S1GM-013-F-R01.no',
                        'C:/Simulations/Test\\PT09-S1GM-013-R01.no',
                        'C:/Simulations/Test\\PT09-S1GM-014-F-R01.no',
                        'C:/Simulations/Test\\PT09-S1GM-014-R01.no',
                        'C:/Simulations/Test\\PT09-S1GM-014-WG-F-R01.no',
                        'C:/Simulations/Test\\PT09-S1GM-014-WM-F-R01.no',
                        'C:/Simulations/Test\\PT09-S1MG-011-R01.no',
                        'C:/Simulations/Test\\PT09-S1MG-011-WG-R01.no',
                        'C:/Simulations/Test\\PT09-S1MG-012-F-R01.no',
                        'C:/Simulations/Test\\PT09-S1MG-012-R01.no',
                        'C:/Simulations/Test\\PT09-S1MG-012-WG-F-R01.no',
                        'C:/Simulations/Test\\PT09-S1MG-012-WG-R01.no',
                        'C:/Simulations/Test\\PT09-S1MG-012-WM-F-R01.no',
                        'C:/Simulations/Test\\PT09-S1MG-013-F-R01.no',
                        'C:/Simulations/Test\\PT09-S1MG-013-R01.no',
                        'C:/Simulations/Test\\PT09-S1MG-014-R01.no',
                        'C:/Simulations/Test\\PT09-S1MG-015-F-R01.no',
                        'C:/Simulations/Test\\PT09-S1MG-015-WG-F-R01.no',
                        'C:/Simulations/Test\\PT09-S1MG-015-WM-F-R01.no',
                        'C:/Simulations/Test\\PT09-S1MG-021-WG-R01.no',
                        'C:/Simulations/Test\\PT09-S1MG-022-WG-R01.no'],
    'simtime': -1,
    'lookup_fire_data': True,
    'segments_2_lookup': [2, 4, 6],
    'visio_template': 'C:/Users/6019997/OneDrive - Gruppo Ferrovie Dello '
                    'Stato/TVS-FLS Task/SES-PTUS/Calculations/SES-277 Stairway '
                    'Pressurization/SES-202 R3 Result Network for SES-277.vsdx'}
    
    # Pass settings correctly
    settings = launch_window(parent=None, settings=settings)
    
    output_file = NO_summary.create_excel_summary(settings)
    if output_file:
        print(f"\nSaved summary to: {output_file}")
        print(f"Full path: {output_file.absolute()}")
    else:
        print("No data to summarize")