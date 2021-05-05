#Import of standard modules
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

def read_lic():
  #TODO Error checking if file doesn't exist
  license_files = nfm.find_all_files(extensions = [".LIC"])
  if len(license_files) > 1:
    print("License ERROR! Too many license files (*.lic) in the directory. Only include one valid license and try again.")
    system_exit("License ERROR! Too many license files (*.lic) in the directory. Only include one valid license and try again.")
  elif len(license_files) == 0:
    print("License Error! Cannot find license file (*.lic). Add valid license in directory or request license from Justin@NeverGray.biz and try again.")
    system_exit("License Error! Cannot find license file (*.lic). Add valid license in directory or request license form Justin@NeverGray.biz and try again.")
  else:
    filepath = license_files[0]
  with open(filepath, 'r') as file_object:
    lines = file_object.readlines()
  for line in lines:
    if line.startswith('license_key ='):
      license_key = line[14:].strip()
    elif line.startswith('keygen_account_id ='):
      keygen_account_id = line[19:].strip()
    elif line.startswith('keygen_activation_token'):
      keygen_activation_token = line[25:].strip()
  return license_key, keygen_account_id, keygen_activation_token

def activate_license(license_key, keygen_account_id, kegen_activation_token):
  logging.getLogger("urllib3").setLevel(logging.WARNING) #Remove debugging screen from request, see https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
  machine_fingerprint = hashlib.sha256(str(get_mac()).encode('utf-8')).hexdigest()
  validation = requests.post(
    "https://api.keygen.sh/v1/accounts/{}/licenses/actions/validate-key".format(keygen_account_id),
    headers={
      "Content-Type": "application/vnd.api+json",
      "Accept": "application/vnd.api+json"
    },
    data=json.dumps({
      "meta": {
        "scope": { "fingerprint": machine_fingerprint },
        "key": license_key
      }
    })
  ).json()

  if "errors" in validation:
    errs = validation["errors"]

    return False, "license validation failed: {}".format(
      map(lambda e: "{} - {}".format(e["title"], e["detail"]).lower(), errs)
    )

  # If the license is valid for the current machine, that means it has
  # already been activated. We can return early.
  if validation["meta"]["valid"]:
    return True, "license has already been activated on this machine"

  # Otherwise, we need to determine why the current license is not valid,
  # because in our case it may be invalid because another machine has
  # already been activated, or it may be invalid because it doesn't
  # have any activated machines associated with it yet and in that case
  # we'll need to activate one.
  #
  # NOTE: the "NO_MACHINE" status is unique to *node-locked* licenses. If
  #       you need to implement a floating license, you may also need to
  #       check for the "NO_MACHINES" status (note: plural) and also the
  #       "FINGERPRINT_SCOPE_MISMATCH" status.
  if validation["meta"]["constant"] != "NO_MACHINE":
    return False, "license {}".format(validation["meta"]["detail"])

  # If we've gotten this far, then our license has not been activated yet,
  # so we should go ahead and activate the current machine.
  activation = requests.post(
    "https://api.keygen.sh/v1/accounts/{}/machines".format(keygen_account_id),
    headers={
      "Authorization": "Bearer {}".format(kegen_activation_token),
      "Content-Type": "application/vnd.api+json",
      "Accept": "application/vnd.api+json"
    },
    data=json.dumps({
      "data": {
        "type": "machines",
        "attributes": {
          "fingerprint": machine_fingerprint
        },
        "relationships": {
          "license": {
            "data": { "type": "licenses", "id": validation["data"]["id"] }
          }
        }
      }
    })
  ).json()

  # If we get back an error, our activation failed.
  if "errors" in activation:
    errs = activation["errors"]

    return False, "license activation failed: {}".format(
      map(lambda e: "{} - {}".format(e["title"], e["detail"]).lower(), errs)
    )

  return True, "Next-VIS Beta license activated"

# Run from the command line:
#   python main.py some_license_key
#status, msg = activate_license(sys.argv[1])

def get_input(settings = None):
    Welcome = "Next Vis - Proprocessing SES Output files"
    q_start = "Select the type of post-processing to perform or exit program: \n"
    q_repeat = 'Repeat last processing Y/N: '
    q_simname = '''Enter SES output file name with suffix (.OUT for SES v6): 
  Current working directory is same as NextVis Executable.
  If desired, specify abolute pathway (C:\\) or simply \\ for sub-folders of working directory.
  Enter "ALL" for all files in folder, 
  or blank to quit. 
'''
    ext_simname = ['.OUT', '.PRN']
    e = 'Cannot find file, please try again or enter blank to quit. \n'
    q_visname = 'Visio template with suffix (*.vsdx) or blank to quit: '
    ext_visname = ['.VSDX']
    q_simtime = 'Enter simulation time for Visio template or -1 for last time: '
    repeat = 'no'
    if settings['control'] != 'First':
        repeat = pyip.inputYesNo(q_repeat, yesVal='yes', noVal='no')
    else:
        settings['control'] = 'Single'
    if repeat == 'no':
        #TODO determine version type from simname
        print(Welcome)
        settings['output'] = pyip.inputMenu(['Visio', 'Excel', 'Both', 'Analyses','Exit'],q_start,numbered=True)
        if settings['output'] in ['Visio', 'Excel', 'Both']:       
            #Get name of output file
            settings['simname'] = nfm.validate_file(q_simname, e, ext_simname)
            if settings['simname'][-3:].upper() == "ALL":
                settings['control']="ALL"
            elif settings['simname'] == "":
                settings['control'] = "Stop"
            else:
                settings['control']="Single"
        if settings['output'] in ['Visio', 'Both']:
            settings['visname'] = nfm.validate_file(q_visname, e, ext_visname)
            if settings['visname'] != "":
                settings['simtime'] = pyip.inputNum(q_simtime, min=-1)
            else:
                settings['control'] = "Stop"
        elif settings['output'] == 'Analyses':
          settings['control'] = 'Analyses'
        elif  settings['output'] == 'Exit':
          settings['control'] = "Stop"
    return settings

def single_sim(settings, multi_processor_name =''):
    if multi_processor_name != '':
        settings['simname'] = multi_processor_name
    data = nvp.parse_file(settings['simname'])
    base_name = settings['simname'][:-4]
    if len(data) == 0:
      return
    if settings['output'] != 'Excel':
        for item in data: 
          if item.name == 'PIT':
            df_PIT = item #Pass dataframe 
            break
        settings['simtime'] = nvv.valid_simtime(settings['simtime'], df_PIT)
        time_4_name = int(settings['simtime'])
        settings['new_visio']  = base_name +"-" + str(time_4_name)+ ".vsdx"
        nvv.update_visio(settings, df_PIT)
    if settings['output'] != 'Visio': #Create Excel File
        #TODO Add error checker if excel file is open
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
          print("Created Excel File " + base_name +".xlsx")
        except:
          print("ERROR creating Excel file " + base_name + ".xlsx.  Try closing this file in excel and process again")

def main(testing=False):
    #TODO Update security to allow entering license key only once?
    try:
      [license_key, keygen_account_id, keygen_activation_token] = read_lic()
    except:
      quit()
    legit, msg = activate_license(license_key, keygen_account_id, keygen_activation_token)
    #Confirm license is activated
    #initialize variable
    multiprocessing.freeze_support() #Required for multiprocess to work with Pyinstaller on windows computers
    settings = {} #Container for settings
    settings['control'] = 'First' #Change to 'testing' when necessary
    print(legit, msg)
    if not legit:
        print("Your license is not valid. Please contact Justin@NeverGray.biz to continue using the program.")
        input('Program will exit when you hit enter')
        return
    if testing:
        print('In testing mode')
        settings={
            'simname' : 'coolpipe.out',
            'visname' : 'Test020.vsdx',
            'simtime' : 9999.0,
            'version' : 'tbd',
            'control' : 'First',
            'output'  : 'Excel'
        }
        #single_sim(settings)
        single_sim(settings)
    elif legit:
        while settings['control'] != 'Stop' and legit:
            if settings['control'] != 'Testing':
                settings = get_input(settings)
            if settings['control'] == 'Single':
                #TODO add Try statement to incase there are errors
                single_sim(settings)
            elif settings['control'] == 'ALL':
                if settings['simname'].upper()=='ALL':
                  #all_files = nfm.find_all_files(pathway = settings['simname'])
                  all_files = nfm.find_all_files()
                  p = "this is in the active directory"
                else:
                  p = settings['simname'][:-4] #pathway
                  all_files = nfm.find_all_files(pathway = p)
                num_files = len(all_files)
                if num_files == 0:
                  print("No output files found")
                elif num_files == 1:
                  settings['simname'] = all_files[0]
                  single_sim(settings)
                else:  
                  num_of_p = max(multiprocessing.cpu_count() -1,1) #Use all processors except 1
                  num_of_p = min(num_of_p, len(all_files))
                  print("Processing " + str(len(all_files)) + " SES Output files using " + str(num_of_p)+" threads" )
                  pool = multiprocessing.Pool(num_of_p, maxtasksperchild=1)
                  finished_files = 0
                  for file in all_files:
                    # Reference2 code for multiprocess https://pymotw.com/2/multiprocessing/basics.html
                    # Another code for multiprocessing https://stackoverflow.com/questions/20886565/using-multiprocessing-process-with-a-maximum-number-of-simultaneous-processes
                    if p != "this is in the active directory":
                      filepath = p + '\\' + file
                    else:
                      filepath = file
                    pool.apply_async(single_sim, args=(settings,filepath))
                    #single_sim(settings,file)
                  pool.close()
                  pool.join()
            elif settings['control'] == 'Analyses':
              nva.analyses_menu(settings)
            else: #Something has gone wrong!
                #print("Error in inputing data to control variable")
                c = pyip.inputYesNo(prompt='Do you want to quit the program? Yes or No: ')
                settings = {} #Clear container for settings
                if c == 'no':
                    settings['control'] = 'First'
                else:
                    settings['control'] = 'Stop'
                    return
    else:
      print('Something has gone horribly wrong! Your licese may no longer be valid or something weird happened. Try restrating')
      input('Program will exit when you hit enter')
      return
    4
if __name__ == '__main__':
    main(testing=False)