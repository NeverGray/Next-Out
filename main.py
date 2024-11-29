#TODO Insert Beginning Notes

import multiprocessing
import NO_gui

def main(testing=False):
    NO_gui.launch_window()

if __name__ == "__main__":
    multiprocessing.freeze_support() #TODO Experiement if this command is necessary
    main(testing=False)
 