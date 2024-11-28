import concurrent.futures
import logging
import subprocess
import os
import time
from pathlib import Path
from tkinter import Tk, Frame, Label, Button, messagebox

class App(Tk):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.title("Process and Monitor Files")
        self.geometry("500x300")
        self.setup_ui()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.tasks = []
        self.monitor_thread = None
        self.running = False

    def setup_ui(self):
        frame = Frame(self)
        frame.pack(pady=20)

        self.status_label = Label(frame, text="Status: Waiting")
        self.status_label.pack(pady=10)

        start_button = Button(frame, text="Start", command=self.start_processing)
        start_button.pack(side="left", padx=5)

        stop_button = Button(frame, text="Stop", command=self.stop_processing)
        stop_button.pack(side="right", padx=5)

    def start_processing(self):
        if not self.running:
            self.running = True
            self.status_label.config(text="Status: Running")
            self.monitor_thread = self.executor.submit(self.monitor_tasks)
            self.tasks = [
                self.executor.submit(self.process_file, file_path)
                for file_path in self.settings["ses_output_str"]
            ]

    def stop_processing(self):
        if self.running:
            self.running = False
            self.status_label.config(text="Status: Stopping")
            for task in self.tasks:
                task.cancel()
            if self.monitor_thread:
                self.monitor_thread.cancel()

    def monitor_tasks(self):
        while self.running:
            done, not_done = concurrent.futures.wait(self.tasks, timeout=1)
            if not_done:
                self.status_label.config(text=f"Status: Running ({len(not_done)} tasks remaining)")
            else:
                self.running = False
                self.status_label.config(text="Status: Completed")

    def process_file(self, file_path):
        try:
            logging.info(f"Processing file: {file_path}")
            self.run_SES(self.settings["path_exe"], file_path)
            logging.info(f"Finished processing: {file_path}")
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}")
            messagebox.showerror("Error", f"Error processing file {file_path}: {e}")

    def run_SES(self, ses_exe_path, ses_input_file_path):
        try:
            subprocess.run(
                [ses_exe_path, ses_input_file_path],
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except FileNotFoundError as exc:
            logging.info(
                f"Process failed because the executable could not be found.\n{exc}"
            )
        except subprocess.CalledProcessError as exc:
            if exc.returncode != 100:
                msg = f"SES Simulation failed. Returned {exc.returncode}\n{exc}"
                logging.info(msg)
        except Exception as e:
            logging.error(f"Unexpected error running SES: {e}")

    def on_closing(self):
        self.stop_processing()
        self.executor.shutdown(wait=False)
        self.destroy()

def output_from_input(file_path, path_exe):
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
    while pause_value():
        time.sleep(0.1)

if __name__ == "__main__":
    settings = {
        "ses_output_str": ["example1.ses", "example2.ses"],  # Example SES files
        "path_exe": "path_to_ses_executable",
        "results_folder_str": None,
        "next_in_ses_version": "SI",
    }
    app = App(settings)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
