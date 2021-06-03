
from uuid import getnode as get_mac
import requests
import json
import hashlib
import pyinputplus as pyip
import multiprocessing #When trying to make a multiprocessing
from pathlib import Path
import pandas as pd
import logging
#Import of scripts
import NV_parser as nvp
import NV_visio as nvv
import NV_file_manager as nfm
import NV_analyses as nva
from sys import exit as system_exit
from os import startfile

def single_sim(settings, multi_processor_name =''):
    if multi_processor_name != '':
        settings['simname'] = multi_processor_name
    data = nvp.parse_file(settings['simname'])
    base_name = settings['simname'][:-4]
    if len(data) == 0:
      return  
    if 'Excel' in settings['output']: #Create Excel File
        #TODO Add error checker if excel file is open
        #TODO Write to memor first, then to file to speed up process (especially for multiple simulations)
        try:
          with pd.ExcelWriter(base_name +".xlsx", engine = 'openpyxl') as writer:
              for item in data:
                  item.to_excel(writer, sheet_name = item.name, merge_cells=False)
                  #Add code to create filters
                  #https://stackoverflow.com/questions/51566349/openpyxl-how-to-add-filters-to-all-columns
                  worksheet = writer.sheets[item.name]
                  worksheet.auto_filter.ref = worksheet.dimensions
                  #Freeze cells from https://stackoverflow.com/questions/25588918/how-to-freeze-entire-header-row-in-openpyxl
                  testing = len(item.index.names)
                  freeze_column = len(item.index.names)
                  freeze_cell = worksheet.cell(row=2, column = freeze_column + 1)
                  worksheet.freeze_panes = freeze_cell
              #Add properties to Excel File.  Following https://stackoverflow.com/questions/52120125/how-to-edit-core-properties-of-xlsx-file-with-python
              writer.book.properties.creator = "Next Vis Beta"
              writer.book.properties.title = base_name
          print("Created Excel File " + base_name +".xlsx")
        except:
          print("ERROR creating Excel file " + base_name + ".xlsx.  Try closing this file in excel and process again")
    if 'Visio' in settings['output']:
        try:
            for item in data: 
                if item.name == 'PIT':
                    df_PIT = item #Pass dataframe 
                    break
            settings['simtime'] = nvv.valid_simtime(settings['simtime'], df_PIT)
            time_4_name = int(settings['simtime'])
            settings['new_visio']  = base_name +"-" + str(time_4_name)+ ".vsdx"
            nvv.update_visio(settings, df_PIT)
        except:
            print("ERROR creating Visio file in NV_run.")

if __name__ == '__main__':
    settings={
        'simname' : 'sinorm-detailed.out',
        'visname' : 'Sample012.vsdx',
        'simtime' : 9999.0,
        'version' : 'tbd',
        'control' : 'First',
        'output'  : ['Excel','Visio','Compare']
    }
    single_sim(settings)