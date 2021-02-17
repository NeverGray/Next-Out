import re
import pandas as pd
import logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
import zipfile
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED
import xml.etree.ElementTree as ET
import os
import pyinputplus as pyip
from pathlib import Path
import argparse

def select_version(str):
    v41 = "SES VER 4.10"
    if v41 in str:
        version = 'i' 
    else:
        version = 's'
    return version


# Select the appropriate dictionary
def select_dic(version): 
    if version =='i': #Parser key for SES v4.1 Emergency simualtions. Currently identical to v6.0 
        rx_dict = { 
            'time': re.compile(r'TIME.\s+(?P<Time>\d+.\d{2}).+SECONDS.+TRAIN'), #Find the first time Simulation
            'detail_segment_1': re.compile(r'''(
                \d+\s-                        #Section
                (?P<Segment>\s{0,2}\d+)+\s-\s+    #Segment
                (?P<Sub>\s{0,2}\d+)\s{1,12}       #Sub-segment
				(?:(?P<Sensible>-?\d+\.\d+)\s+       #Sensible for tunnels
                (?P<Latent>-?\d+\.\d+)\s+|\s{28,})       #Latent for tunnels
				(?P<AirTemp>-?\d+\.\d+)\s+        #Air Temperature
                (?P<Humidity>-?\d+\.\d+)\s+       #Humidity
                (?:(?P<Airflow>-?\d+\.\d+)\s+     #Airflow for first line
                (?P<AirVel>-?\d+\.\d+)\s?|\s?)  #AirVel for first line 
                )''', re.VERBOSE),
            'abb_segment_1': re.compile(r'''(
                \s+\d+\s-\s{0,2}                 #Section
                (?P<Segment>\d+)\s{1,11}         #Segment
                (?P<Airflow>-?\d+\.\d+)\s{1,6}   #Sub-segment
				(?P<AirVel>-?\d+\.\d+)\s{1,8}    #Air Velocity
				(?P<AirTemp>-?\d+\.\d+)\s{1,8}   #Air Temperature
                \s?
                )''', re.VERBOSE),
        }
    else: #Parser key for SES v6.0 Emergency simualtions 
        rx_dict = { 
            'time': re.compile(r'TIME.\s+(?P<Time>\d+.\d{2}).+SECONDS.+TRAIN'), #Find the first time Simulation
            'detail_segment_1': re.compile(r'''(
                \d+\s-                        #Section
                (?P<Segment>\s{0,2}\d+)+\s-\s+    #Segment
                (?P<Sub>\s{0,2}\d+)\s{1,12}       #Sub-segment
				(?:(?P<Sensible>-?\d+\.\d+)\s+       #Sensible for tunnels
                (?P<Latent>-?\d+\.\d+)\s+|\s{28,})       #Latent for tunnels
				(?P<AirTemp>-?\d+\.\d+)\s+        #Air Temperature
                (?P<Humidity>-?\d+\.\d+)\s+       #Humidity
                (?:(?P<Airflow>-?\d+\.\d+)\s+     #Airflow for first line
                (?P<AirVel>-?\d+\.\d+)\s?|\s?)  #AirVel for first line 
                )''', re.VERBOSE),
            'abb_segment_1': re.compile(r'''(
                \s+\d+\s-\s{0,2}                 #Section
                (?P<Segment>\d+)\s{1,11}         #Segment
                (?P<Airflow>-?\d+\.\d+)\s{1,6}   #Sub-segment
				(?P<AirVel>-?\d+\.\d+)\s{1,8}    #Air Velocity
				(?P<AirTemp>-?\d+\.\d+)\s{1,8}   #Air Temperature
                \s?
                )''', re.VERBOSE),
            #May need to update 'segmentdetail' in SI to Match IP by replace '-..1' with '-\s{2}1'
            #test parser using https://www.debuggex.com/
            }
    return rx_dict
   
def parse_file(filepath):
    data_segment = []  # create an empty list to collect the data
    # open the file and read through it line by line
    with open(filepath, 'r') as file_object:
        lines = file_object.readlines() #Gets list of string values from the file, one string for each line of text
        #TODO determine version
        version = select_version(lines[0])
        rx_dict = select_dic(version) #Select appropriate parser key
        #Find line where simulation time starts
    
    i = 0 #Start at first line
    m = None #Sets the value equal to none to start while loop
    while m is None and i < len(lines):
            rx = rx_dict['time']
            m = rx.search(lines[i])
            i +=1
    assert (i < (len(lines) - 1)), 'Cannot find first time! Line variable ' + str(i) 
    time = float(m.group('Time'))
    while i < len(lines):
        # at each line check for a match with a regex
        m = False
        for key, rx in rx_dict.items(): #change dictionary as necessary
            m = rx.search(lines[i]) #using .match searched the beginning of the line
            if m is not None:
                if key == 'time': #sets time interval
                    time = float(m.group('Time'))
                    break
                else: #If key is other than time
                    row={'Time':time} #should erase row and reset the values
                    m_dict = m.groupdict()
                    for name, variable in m_dict.items():
                        if variable is not None:
                            #temp=float(variable)
                            row.update({name:float(variable)})    
                    if key == 'abb_segment_1':
                        #Code only includes information for segment 1 for abbreviated prints
                        #TODO Capture data for all sub-segments
                        i +=1
                        row.update({'Sub':float(1.0)})
                        s = lines[i]
                        s = s[1:45]
                        row.update({'Humidity':s.strip()}) #Add humidity from one line below, only first segement
                    data_segment.append(row)
                break
        i +=1
    df_segment = pd.DataFrame(data_segment)
    # set the Time and Segment as the index
    df_segment.set_index(['Time', 'Segment','Sub'], inplace=True)
    if version == "i":
        df_segment['Airflow'] = df_segment['Airflow']/1000
    print("Post processed ",filepath)
    return df_segment

def valid_simtime(simtime, data):
    timeseries_index = data.index.unique(0) #Creates a series of unique times
    timeseries_list = timeseries_index.tolist()
    time = float(simtime)
    if time == -1 or time > timeseries_list[-1]:
        time = timeseries_list[-1]
        print('Using last simulation time ', time)
    elif not time in timeseries_list:
        for x in timeseries_list:
            if (x - time >0):
                time = x
                break
        print('Could not find requested simulation time. Using ',time)
    return time

def get_visXML(visname):
    VZip = zipfile.ZipFile(visname)
    names = VZip.namelist()
    vxmls={}
    for name in names:
        m = re.match('visio/pages/[^/]+[.xml]$',name)
        if m:
            vxmls[name] = VZip.read(name) #Create dictionary of name paths and files
    return vxmls

#TODO Write function to update text of elements in Visio XML file

#code to modify XML file for emergency simualtions
def emod_visXML(vxml, data, simname="Not Available", simtime = 0.00): 
    P1root=ET.fromstring(vxml) #create XML element from the string
    ET.register_namespace('','http://schemas.microsoft.com/office/visio/2012/main') #Need to register name space to reproduce file.
    ET.register_namespace('r','http://schemas.openxmlformats.org/officeDocument/2006/relationships')
    ns = {'Visio': 'http://schemas.microsoft.com/office/visio/2012/main'} #Namespace dictionary to ease file navigation
    #Airflow arrow shape update
    #Find all shape with sub-child NV01_SegID. The "../.." at the end of the string moves the selection up two tiers to Shape
    for Shape in P1root.findall(".//Visio:Row[@N='NV01_SegID']../.." , ns): 
        SegID=int(Shape.find(".//Visio:Row[@N='NV01_SegID']/Visio:Cell",ns).get('V')) #Get the value for the Segment ID from XML and save as SegID
        SubID=1
        try: #Pull airflow from the dataframe, if it does not exist, use an airflow 999.9
            ses_airflow = data.loc[(simtime,SegID,SubID),"Airflow"]
        except:
            ses_airflow = -999.9
        airflow=str(round(abs(ses_airflow),1)) #The absolute airflow as a string
        ShapeChild=Shape.find(".//Visio:Shape[@Name='NV01_AirFlow']",ns) #Selects the NV01_Airflow Object
        #ET.SubElement(ShapeChild,"Text").text=airflow 
        ShapeBabe=ShapeChild.find(".//Visio:Text",ns) #Select the child's babe with text value
        if ET.iselement(ShapeBabe): #If element already exists, change the value
            ShapeBabe.text=airflow
        else:     
            ET.SubElement(ShapeChild,"Text").text=airflow #Adds text element and value if elemnt doesn't exist
        #Determine arrow direction
        if (ses_airflow >= 0):
            Flip=0
        else:
            Flip=1    
        ShapeChild=Shape.find(".//Visio:Cell[@N='FlipX']",ns) #Find all Flipx propertiesin the file       
        if ET.iselement(ShapeChild):
            ShapeChild.set('V',str(Flip))
        else:
            ET.SubElement(Shape,"Cell",V=str(Flip),N='FlipX')
    #Update all shapes with simple text
    text_shapes = [ #Define all simple shates with simple text
        [".//Visio:Shape[@Name='NV01_SimNam']",simname],
        [".//Visio:Shape[@Name='NV01_SimTime']",str(int(simtime))]
        ]
    for ts in text_shapes: #Iterate through all samples with simple text
        P1root = text_update(ts[0],ts[1],P1root,ns)
    #ET.ElementTree(P1root).write("page1.xml",encoding='utf-8',xml_declaration=True) #TODO eliminate writing to disk in this procedure
    return P1root

def text_update(find_string, text_value, root, ns):
    for Shape in root.findall(find_string,ns):
        ShapeChild=Shape.find(".//Visio:Text",ns)
        if ET.iselement(ShapeChild):
            ShapeChild.text = text_value
        else:
            ET.SubElement(Shape,"Text").text= text_value #previously str(Airflow)#TODO eliminate writing to disk in this procedure
    return root


def write_visio(vxmls, visname, new_visio):
    #Sample Zip source code from https://stackoverflow.com/questions/513788/delete-file-from-zipfile-with-the-zipfile-module
    with zipfile.ZipFile(visname, 'r') as zin:
        with zipfile.ZipFile(new_visio, 'w') as zout:
            for item in zin.infolist(): 
                buffer = zin.read(item.filename)
                if not (item.filename in vxmls): #File was not updated by this code
                    zout.writestr(item, buffer,compress_type=compression)                   
            zout.comment= b'Mfwfs_Hsbz'
    with zipfile.ZipFile (new_visio, 'a') as zappend:
        for name, vxml in vxmls.items():
            #TODO speedup file writing after updating to Python 8. Otherwise, cannot write xml_declaration easily
            ET.ElementTree(vxml).write("temp.xml",encoding='utf-8',xml_declaration=True)
            zappend.write('temp.xml',name,compress_type = compression)
            os.remove('temp.xml')
    print("Created Visio Diagram ",new_visio)

def update_visio(settings,data):
    vxmls = get_visXML(settings['visname']) #gets the pages in the VISIO XML.
    #emod_visXML(vxmls["visio/pages/page1.xml"],data, settings['simname'][:-4], settings['simtime'])    
    #For each file, in bype form replace with a the XML root type
    for name, vxml in vxmls.items():
        vxmls[name] = emod_visXML(vxmls[name],data, settings['simname'][:-4], settings['simtime'])
    write_visio(vxmls, settings['visname'], settings['new_visio'])
    #open_v = input('Open Visio file (Y/N): ') 
    #if open_v.upper() == 'Y':
    #    os.startfile(new_visio)

def get_input(settings = None):
    q_repeat = 'Repeat last processing Y/N: '
    q_simname = 'Enter output file name with suffix (.OUT for SES v6), blank to quit, or ALL: '
    ext_simname = ['.OUT', '.PRN']
    e = 'Cannot find file, please try again or enter blank to quit. \n'
    q_visname = 'Enter name of visio temlpate wiht suffix (*.vsdx): '
    ext_visname = ['.VSDX']
    q_simtime = 'Emergency Simulation Time or -1 for last time: '
    repeat = 'no'
    if settings['Control'] != 'First':
        repeat = pyip.inputYesNo(q_repeat, yesVal='yes', noVal='no')
    else:
        settings['Control'] = 'Single'
    if repeat == 'no':
        #TODO determine version type from simname
        settings['simname'] = validate_file(q_simname, e, ext_simname)
        if settings['simname'] != "":
            settings['visname'] = validate_file(q_visname, e, ext_visname)
            if settings['visname'] != "":
                settings['simtime'] = pyip.inputNum(q_simtime, min=-1)
            else:
                settings['Control'] = "Stop"
                settings['simname'] != "Stop" #Needed to prevent the ALL function
        else:
            settings['Control'] = "Stop"
    if settings['simname'].endswith('.prn'): #Could eliminate because it is automated now
        #TODO Add version switch for 4.1 and 4.2
        settings['version']='i'
    else:
        settings['version']='s'
    if settings['simname'].upper() == "ALL":
        settings['Control']="ALL"
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

def find_all_files():
    all_files = []
    Extensions = [".OUT", ".PRN"]
    with os.scandir() as it: #Return an iterator of os.DirEntr, see https://docs.python.org/3/library/os.html
        for entry in it: #For each item in iterator
            if entry.name[-4:].upper() in Extensions and entry.is_file(): 
                all_files.append(entry.name)
    return all_files  

def single_visio(settings):
    data = parse_file(settings['simname'])#Creates a panda with the airflow out at all time steps
    settings['simtime'] = valid_simtime(settings['simtime'],data)
    time_4_name = int(settings['simtime'])
    settings['new_visio']  = settings['simname'][:-4] +"-" + str(time_4_name)+ ".vsdx"
    update_visio(settings,data)


if __name__ == '__main__':
    #initialize a few variables
    Testing = False
    settings = {}
    #TODO Create arguments for command line   Follow further instructions at https://docs.python.org/3/howto/argparse.html
    #parser = argparse.ArgumentParser()
    #parser.parse_args()    
    if Testing:
        settings={
            'simname' : 'inferno.prn',
            'visname' : 'Template20210209.vsdx',
            'simtime' : 2000.0,
            'version' : 'tbd',
            'Control' : 'Testing'
        }
    else:
        settings['Control'] = 'First'
    while settings['Control'] != 'Stop':
        if settings['Control'] != 'Testing':
            settings = get_input(settings)
        if settings['Control'] == 'Single':
            single_visio(settings)
            if Testing:
                settings['Control'] = 'Stop'
        elif settings['Control'] == 'ALL':
            all_files = find_all_files()
            for file in all_files:
                settings['simname'] = file
                single_visio(settings)

