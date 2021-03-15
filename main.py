#Import of standard modules
from uuid import getnode as get_mac
import requests
import json
import hashlib
import pyinputplus as pyip
import multiprocessing #When trying to make a multiprocessing
from pathlib import Path
from os import scandir
import pandas as pd
#Import of scripts
import NV_parser as nvp
import NV_visio as nvv

def activate_license(license_key, keygen_account_id):
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
  kegen_activation_token = input('Provide Activation Token to license the program: ') #Added to allow kegen activation
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
    q_start = "Select the type of output file to create: \n"
    q_repeat = 'Repeat last processing Y/N: '
    q_simname = 'SES output file name with suffix (.OUT for SES v6), blank to quit, or ALL: '
    ext_simname = ['.OUT', '.PRN']
    e = 'Cannot find file, please try again or enter blank to quit. \n'
    q_visname = 'Visio template with suffix (*.vsdx) or blank to quit: '
    ext_visname = ['.VSDX']
    q_simtime = 'Emergency Simulation Time or -1 for last time: '
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

def validate_file(q, e, ext):
    invalid = True
    while invalid: #Output File name
        answer = pyip.inputFilename(prompt = q,blank = True, limit=5)
        if answer.upper() != "ALL":
            path_answer = Path() / answer#Creates a path object
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
    if settings['output'] != 'Excel':
        for item in data: #TODO - Need to get PIT from Data list
          if item.name == 'PIT':
            df_PIT = item #Pass dataframe 
            break
        settings['simtime'] = nvv.valid_simtime(settings['simtime'], df_PIT)
        time_4_name = int(settings['simtime'])
        settings['new_visio']  = base_name +"-" + str(time_4_name)+ ".vsdx"
        nvv.update_visio(settings, df_PIT)
    if settings['output'] != 'Visio':
        with pd.ExcelWriter(base_name+".xlsx") as writer:
            for item in data:
                item.to_excel(writer, sheet_name = item.name, merge_cells=False)
        print("Created Excel File " + base_name +".xlsx \n")

def find_all_files():
    all_files = []
    Extensions = [".OUT", ".PRN"]
    with scandir() as it: #Return an iterator of os.DirEntr, see https://docs.python.org/3/library/os.html
        for entry in it: #For each item in iterator
            if entry.name[-4:].upper() in Extensions and entry.is_file(): 
                all_files.append(entry.name)
    return all_files  

def main(testing=False):
    #initialize variable
    multiprocessing.freeze_support() #Required for multiprocess to work with Pyinstaller on windows computers
    settings = {} #Container for settings
    settings['control'] = 'First' #Change to 'testing' when necessary
    #Confirm license is activated
    keygen_account_id = '11635372-552d-48aa-aa1b-8b927fcaccd2' 
    #TODO Update security to allow entering license key only once?
    key = 'key/RVlDVy05N0pLLVZYTjMtVFdDMy1UN1hZLVhQNEMtV0xQUC05TkFB.gWse8XGjklxZ0z6DV-6SEelPefBxOLggVWAwEr99DbpFI6KKwunIHxRY0xlQHWNx3L4coWIlT--DtfenfmPIYPUNFIqjzH2tk3PnzfQh2tE1-QZfVAQvUhe9oePd1biKuGAtr6pwQ82vU-nUyjIiOAEwWU2_e4jKnp3so8a3BGpV8gPRQ70tz2Avh2gcsRydJb3meOOwuSGVTLaQRTNb9ypzTcHEcbN8CCPScq3gyFyRNHJtY2Tgm1J44NpAiAuI28JCJlI4gDing7nDn_0nAzEKYM8m3txq8ZDPR5IwjQF9WOKe9lHqDE-noWAJ_49oSUkQGek_7MfhVlrEmLr_ww=='
    legit, msg = activate_license(key, keygen_account_id)
    print(legit, msg)
    if not legit:
        return
    if testing:
        print('In testing mode')
        settings={
            'simname' : 'inferno.prn',
            'visname' : 'inferno.vsdx',
            'simtime' : 9999.0,
            'version' : 'tbd',
            'control' : 'Stop',
            'output'  : 'Both'
        }
        single_sim(settings)
    else:
        while settings['control'] != 'Stop':
            if settings['control'] != 'Testing':
                settings = get_input(settings)
            if settings['control'] == 'Single':
                #TODO add Try statement to incase there are errors
                single_sim(settings)
            elif settings['control'] == 'ALL':
                all_files = find_all_files()
                print("Processing " + str(len(all_files)) + " SES Output files")
                num_of_p = max(multiprocessing.cpu_count() -1,1) #Use all processors except 1
                pool = multiprocessing.Pool(num_of_p)
                for file in all_files:
                    # Reference code for multiprocess https://pymotw.com/2/multiprocessing/basics.html
                    # Another code for multiprocessing https://stackoverflow.com/questions/20886565/using-multiprocessing-process-with-a-maximum-number-of-simultaneous-processes
                    pool.apply_async(single_sim, args=(settings,file))
                    #single_sim(settings,file)
                pool.close()
                pool.join()
            else: #Something has gone wrong!
                print("Error in inputing data to control variable")
                c = pyip.inputYesNo(prompt='Do you want to try post-processing again? Yes to try, No to quit: ')
                settings = {} #Clear container for settings
                if c == 'yes':
                    settings['control'] = 'First'
                else:
                    settings['control'] = 'Stop'
                    return
    
if __name__ == '__main__':
    main(testing=True)