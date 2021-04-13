#Import of standard modules
from uuid import getnode as get_mac
import requests
import json
import hashlib
import pyinputplus as pyip
import multiprocessing #When trying to make a multiprocessing
from pathlib import Path
import os
import pandas as pd
import logging
#Import of scripts
import NV_parser as nvp
import NV_visio as nvv


def read_lic():
  #TODO Error checking if file doesn't exist
  filepath = 'Next_Vis_Beta.lic'
  path = Path() / filepath #Creates a path object
  if not path.is_file():
    print('Cannot find ' + filepath + '. Put file in same folder as EXE file and try again.')
    repeat = pyip.inputYesNo("Ready to try reading license again? Y/N ", yesVal='yes', noVal='no')
    if repeat == 'no':
      print('Please acquire proper license from Justin@NeverGray.biz')
      quit()
    elif not path.is_file():
      print('Still cannot license file' + filepath + '. Please acquire proper license from Justin@NeverGray.biz')
      quit()
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
    q_simname = 'SES output file name with suffix (.OUT for SES v6), blank to quit, or ALL: '
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
        settings['output'] = pyip.inputMenu(['Visio', 'Excel', 'Both', 'Exit'],q_start,numbered=True)
        if settings['output'] == 'Exit':
            settings['control'] = "Stop"
        if settings['control'] !="Stop":       
            settings['simname'] = validate_file(q_simname, e, ext_simname)
            if settings['simname'].upper() == "ALL":
                settings['control']="ALL"
            elif settings['simname'] == "":
                settings['control'] = "Stop"
            else:
                settings['control']="Single"
        if settings['output'] != 'Excel' and settings['control'] != "Stop":
            settings['visname'] = validate_file(q_visname, e, ext_visname)
            if settings['visname'] != "":
                settings['simtime'] = pyip.inputNum(q_simtime, min=-1)
            else:
                settings['control'] = "Stop"
    return settings

def validate_file(q, e, ext): #Q is for prompt, e is for error, ext is for extension
    invalid = True
    while invalid: #Output File name
        answer = pyip.inputFilename(prompt = q,blank = True, limit=5)
        if answer.upper() != "ALL":
            path_answer = Path() / answer #Creates a path object
            if path_answer.is_file():
                if path_answer.suffix.upper() in ext:
                    invalid = False
                else:
                    print("Invalid file extension")
            elif answer == '':
                invalid = False
            else:
                print(e,end='')
        else:
            invalid = False
    return answer

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
    if settings['output'] != 'Visio':
        #TODO Add error checker if excel file is open
        try:
          with pd.ExcelWriter(base_name+".xlsx") as writer:
              for item in data:
                  item.to_excel(writer, sheet_name = item.name, merge_cells=False)
                  #Add code to create filters
                  #https://stackoverflow.com/questions/51566349/openpyxl-how-to-add-filters-to-all-columns
                  #https://stackoverflow.com/questions/17326973/is-there-a-way-to-auto-adjust-excel-column-widths-with-pandas-excelwriter/17811984
                  worksheet = writer.sheets[item.name]
                  worksheet.auto_filter.ref = worksheet.dimensions
          print("Created Excel File " + base_name +".xlsx")
        except:
          print("ERROR creating Excel file " + base_name + ".xlsx.  Try closing this file in excel and process again")

def find_all_files():
    all_files = []
    Extensions = [".OUT", ".PRN"]
    try:
      with os.scandir() as it: #Return an iterator of os.DirEntr, see https://docs.python.org/3/library/os.html
          for entry in it: #For each item in iterator
              if entry.name[-4:].upper() in Extensions and entry.is_file(): 
                  all_files.append(entry.name)
    except:
      print('Error finding all files to process')
    return all_files  

def main(testing=False):
    #TODO Update security to allow entering license key only once?
    [license_key, keygen_account_id, keygen_activation_token] = read_lic()
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
            #'simname' : 'siinfern-detailed.out',
            'simname' : 'sinorm-detailed.out',
            'visname' : 'Test020.vsdx',
            'simtime' : 9999.0,
            'version' : 'tbd',
            'control' : 'Stop',
            'output'  : 'Excel'
        }
        single_sim(settings)
    elif legit:
        while settings['control'] != 'Stop' and legit:
            if settings['control'] != 'Testing':
                settings = get_input(settings)
            if settings['control'] == 'Single':
                #TODO add Try statement to incase there are errors
                single_sim(settings)
            elif settings['control'] == 'ALL':
                all_files = find_all_files()
                num_files = len(all_files)
                if num_files == 0:
                  print("No output files found")
                elif num_files == 1:
                  settings['simname'] = all_files[0]
                  single_sim(settings)
                else:  
                  num_of_p = max(multiprocessing.cpu_count() -1,1) #Use all processors except 1
                  num_of_p = min(num_of_p, len(all_files))
                  print("Processing " + str(len(all_files)) + " SES Output files using "+str(num_of_p)+" processes" )
                  
                  pool = multiprocessing.Pool(num_of_p, maxtasksperchild=1)
                  for file in all_files:
                    # Reference2 code for multiprocess https://pymotw.com/2/multiprocessing/basics.html
                    # Another code for multiprocessing https://stackoverflow.com/questions/20886565/using-multiprocessing-process-with-a-maximum-number-of-simultaneous-processes
                    pool.apply_async(single_sim, args=(settings,file))
                    #single_sim(settings,file)
                  pool.close()
                  pool.join()
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
    
if __name__ == '__main__':
    main(testing=False)