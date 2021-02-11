import re
import pandas as pd
import logging
import zipfile
import xml.etree.ElementTree as ET
import os
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


# Select the appropriate dictionary
def select_dic(version): 
    if version =='i': #Parser key for SES v4.1 Emergency simualtions 
        rx_dict = { 
        #TODO add parser for start of where data is located
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

def get_input(simname= None, simtime= None, visname= None, version= None, outtype=None):
    #TODO update input with "Input Validation" from 'Automate Everything' book'
    no_error = False
    option_check=['S','I','Q','R'] #Valid values of version check
    while not no_error:
        print('Next Vis 06 Options:')
        print('       S for SI Version (SES 6.0 with output of *.out)')
        print('       I for IP Version (SES 4.1 with output of *.prn)')
        print('       R to repeat last creation')
        print('       Q or blank to quit program')
        option = input('Select Options (S, I, R, Q): ')
        option = option.upper()
        if option == None:
            option = 'Q'  
        if (option in option_check):
            no_error = True
        else:
            print('Error! You did not select options (S, I, R, Q)')
    if option =='R':
        return simname, simtime, visname, version, outtype
    elif option =='Q':
        version = option
        return simname, simtime, visname, version, outtype
    else:
        version = option
        outtype = input('Enter E for Excel, V for Visio, or B for both: ')
        outtype = outtype.upper()
        simname = input('Name of SES Output File for Emergency Simulation (without suffix, .out or .prn): ')
        if version == 'I':
            simname=simname + ".prn"
        else:
            simname=simname + ".out"
        if outtype != "E":    
            visname = input('Name visio temlpate (without suffix, .vsdx): ')
            visname = visname + '.vsdx'
            simtime = input('Emergency Simulation Time or E for End (Number or E): ')
            #TODO Check that simtime is number
            simtime = float(simtime)
            if simtime == 'e':
                simtime = 'E'
        else:
            simtime = -1
            visname = "NA"
        ##FF - Future Feature - Check validity of input 
        return simname, simtime, visname, version, outtype
   
def parse_file(filepath, version):
    data_segment = []  # create an empty list to collect the data
    # open the file and read through it line by line
    with open(filepath, 'r') as file_object:
        rx_dict = select_dic(version) #Select appropriate parser key
        lines = file_object.readlines() #Gets list of string values from the file, one string for each line of text
        #Find line where simulation time starts
        #TODO update code to work with lines in a list
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
    return df_segment

def get_visXML(visname):
    VZip = zipfile.ZipFile(visname)
    vxml = VZip.read('visio/pages/page1.xml') #reads the string TODO - Just bring over the string name, not the xml
    vxmlname = 'page1.xml' #FF Eventually read all pages in this directory
    return vxml, vxmlname

#code to modify XML file for emergency simualtions
def emod_visXML(vxml, data, simname="Not Available", simtime = 0.00): 
    P1root=ET.fromstring(vxml) #create XML element from the string
    ET.register_namespace('','http://schemas.microsoft.com/office/visio/2012/main') #Need to register name space to reproduce file.
    ET.register_namespace('r','http://schemas.openxmlformats.org/officeDocument/2006/relationships')
    ns = {'Visio': 'http://schemas.microsoft.com/office/visio/2012/main'} #Namespace dictionary to ease file navigation
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
    #Find all shape with sub-child NV01_SegID. The "../.." at the end of the string moves the selection up two tiers to Shape
    for Shape in P1root.findall(".//Visio:Shape[@Name='NV01_SimNam']../..",ns):
        ShapeChild=Shape.find(".//Visio:Shape[@Name='NV01_SimNam']/Visio:Text",ns)#Finds all NV01_Airflow Shapes with text elements originally in file
        if ET.iselement(ShapeChild): #If an original text element exists, replace with proper value.
            ShapeChild.text = simname #previously str(Airflow)
        else:
            ShapeChild2=Shape.find(".//Visio:Shape[@Name='NV01_SimNam']/Text",ns)
            if ET.iselement(ShapeChild2):
                ShapeChild2.text = simname
            else: #Create a text element because none existed 
                ShapeChild3=Shape.find(".//Visio:Shape[@Name='NV01_SimNam']",ns)
                ET.SubElement(ShapeChild3,"Text").text=simname #previously str(Airflow)
    #Simulation Time
    for Shape in P1root.findall(".//Visio:Shape[@Name='NV01_SimTime']../..",ns):
        ShapeChild=Shape.find(".//Visio:Shape[@Name='NV01_SimTime']/Visio:Text",ns)#Finds all NV01_Airflow Shapes with text elements originally in file
        time = int(simtime)
        if ET.iselement(ShapeChild): #If an original text element exists, replace with proper value.
            ShapeChild.text = str(time) #previously str(Airflow)
        else:
            ShapeChild2=Shape.find(".//Visio:Shape[@Name='NV01_SimTime']/Text",ns)
            if ET.iselement(ShapeChild2):
                ShapeChild2.text = str(time)
            else: #Create a text element because none existed 
                ShapeChild3=Shape.find(".//Visio:Shape[@Name='NV01_SimTime']",ns)
                ET.SubElement(ShapeChild3,"Text").text = str(time) #previously str(Airflow)

    ET.ElementTree(P1root).write("page1.xml",encoding='utf-8',xml_declaration=True) #TODO eliminate writing to disk in this procedure

def write_visio(visname, new_visio):
    #Sample Zip source code from https://stackoverflow.com/questions/513788/delete-file-from-zipfile-with-the-zipfile-module
    zin = zipfile.ZipFile (visname, 'r')
    zout = zipfile.ZipFile (new_visio, 'w')
    for item in zin.infolist(): 
        buffer = zin.read(item.filename)
        if (item.filename != 'visio/pages/page1.xml'): #writes all files except the page2.xml file to a new zip
            zout.writestr(item, buffer)
            #print(item.filename)
    zin.close()
    zout.close()
    zappend = zipfile.ZipFile (new_visio, 'a') #open file for appending
    zappend.write('page1.xml','visio/pages/page1.xml')
    zappend.close()
    os.remove('page1.xml')

if __name__ == '__main__':
    repeat = True #Run the program the first time
    testing = True
    if testing:
        simname = 'siinfern.out'
        visname = "Sample021.vsdx"
        simtime = 500.0
        version = 'S'
        data=[] #Data variable
    else:
        [simname, simtime, visname, version, outtype]= get_input () #Call to get input file names
        data = parse_file(simname, version)#Creates a panda with the airflow out at all time steps
    if True: #Create Visio Diagram
        [vxml,vxmlname] = get_visXML(visname) #gets the Page 1 XML. TODO - Will search all Pages in Visio
        emod_visXML(vxml,data, simname[:-4], simtime)
        new_visio = simname[:-4] + "-" + str(int(simtime)) + ".vsdx"
        write_visio(visname, new_visio)
        print('\n     Created Visio Diagram',new_visio)
        #open_v = input('Open Visio file (Y/N): ') 
        #if open_v.upper() == 'Y':
        #    os.startfile(new_visio)