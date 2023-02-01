# Test Code for Tkinter with threads
import tkinter as Tk
import multiprocessing
import time

class GuiApp(object):
   def __init__(self,status):
        self.root = Tk.Tk()
        self.label = Tk.Label(self.root, text=status.value)
        self.label.pack()
        self.root.after(1000, self.CheckQueuePoll, status)

   def CheckQueuePoll(self,status):
      try:
         get_value = status.value 
         self.label.config(text=get_value)
      except:
         pass
      finally:
         self.root.after(1000, self.CheckQueuePoll, status)

# Data Generator which will generate Data
def GenerateData(status):
        while status.value != -1:
            with status.get_lock():
                status.value +=1
            print(f'Generate Data: {status.value}')
            time.sleep(2)

if __name__ == '__main__':
# Queue which will be used for storing Data

   #q = multiprocessing.Queue()
   #q.cancel_join_thread() # or else thread that puts data will not term
    status = multiprocessing.Value('i',0)
    gui = GuiApp(status)
    t1 = multiprocessing.Process(target=GenerateData,args=(status,))
    t1.start()
    gui.root.mainloop()
    status.value = -1
    t1.join()

