import re
import pandas as pd
import os
import string
import zipfile
import xml.etree.ElementTree as ET
from openpyxl.writer.excel import ExcelWriter
from openpyxl.reader.excel import load_workbook

rx_dict = { #Parser key for SES v6.0 Emergency simualtions 
    'time': re.compile(r'TIME(?P<time>.{11})SECONDS'), #Find the first time Simulation
    'segment': re.compile(r'.{6}-(?P<segment>..\d)(?P<airflow>.{11}\.\d{3})(?P<airvel>.{6}\.\d{2})'), #Find segement data in abbreviated print 
    'segmentdetail': re.compile(r'.{13}-(?P<segment>..\d.)-..1.{56}(?P<airflow>.{8}\.\d{3})(?P<airvel>.{7}\.\d.)') #Find segement in detailed print
    #May need to update 'segmentdetail' in SI to Match IP by replace '-..1' with '-\s{2}1'
    #test parser using https://www.debuggex.com/
    }

rx_dict4p1 = { #Parser key for SES v6.0 Emergency simualtions 
    'time': re.compile(r'TIME(?P<time>.{11})SECONDS'), #Find the first time Simulation
    'segment': re.compile(r'.{6}-(?P<segment>..\d)(?P<airflow>.{13}\.\d{1})(?P<airvel>.{7}\.\d{1})'), #Find segement data in abbreviated print 
    #'segmentdetail': re.compile(r'.{13}-(?P<segment>\d{3}).-\s{2}1.{28}(?P<temperature>.{16})(?P<humidity>.{12})(?P<airflow>.{12})(?P<airvel>.{10})') #Find segement in detailed print
    'segmentdetail': re.compile(r'.{13}-(?P<segment>\d{3}).-\s{2}7.{28}(?P<temperature>.{16})(?P<humidity>.{12})')
    #test parser using https://www.debuggex.com/
    }

def _parse_line(line,version):
    """
    Do a regex search against all defined regexes and
    return the key and match result of the first matching regex

    """    
    if version !='I':
        for key, rx in rx_dict.items(): #change dictionary as necessary
            match = rx.match(line) #using .match searched the beginning of the line
            if match:
                return key, match
    else:
        for key, rx in rx_dict4p1.items(): #change dictionary as necessary
            match = rx.match(line) #using .match searched the beginning of the line
            if match:
                return key, match
    # if there are no matches
    return None, None
    

def parse_file(filepath, version):
    """
    Parse text at given filepath

    Parameters
    ----------
    filepath : str
        Filepath for file_object to be parsed

    Returns
    -------
    data : pd.DataFrame
        Parsed data

    """

    data = []  # create an empty list to collect the data
    # open the file and read through it line by line
    with open(filepath, 'r') as file_object:
        if version == "I":
            rx_dict = rx_dict4p1
        lines = file_object.readlines() #Gets list of string values from the file, one string for each line of text
        #Find line where simulation time starts
        #TODO update code to work with lines in a list
        Proceed = re.compile("               EXECUTION OF THIS SUBWAY ENVIRONMENT SIMULATION IS TO PROCEED.")
        match = False
        while not match:
            match = re.match(Proceed,line)
            line = file_object.readline()   
        #Search simulation results
        while line:
            # at each line check for a match with a regex
            key, match = _parse_line(line,version)

            # extract school name
            if key == 'time':
                time = match.group('time')
                time = float(time)
                line = file_object.readline()    
            if key == 'segment' or key == 'segmentdetail':
                segment = int(match.group('segment'))
                #airflow = float(match.group('airflow'))
                #airvel = float(match.group('airvel'))
                airflow = float(0.00)
                airvel = float(0.00)
                if key == 'segmentdetail':
                    humidity = float(match.group('humidity'))
                    temperature = float(match.group('temperature'))
                else:
                    humidity = -1
                    temperature = -1
                if version == "I":
                    #airflow = round(airflow/1000,1)
                    airflow = airflow/1000
                if key == 'segmentdetail':
                    row={
                            'Time'    : time,
                            'Segment' : segment,
                            'Airflow' : airflow,
                            'AirVel'  : airvel,
                            'Humidity' : humidity,
                            'Temperature' : temperature
                    }
                else:
                    row={
                            'Time'    : time,
                            'Segment' : segment,
                            'Airflow' : airflow,
                            'AirVel'  : airvel
                    }
                data.append(row)
            line = file_object.readline()
    data = pd.DataFrame(data)
    # set the Time and Segment as the index
    data.set_index(['Time', 'Segment'], inplace=True)
    return data

def Excel_file(data):
    data=data.reset_index()
    data=data.sort_values(by=['Segment','Time'])
    data.set_index(['Segment', 'Time'], inplace=True)
    #data=data.rename(columns={'Airflow':'SES Airflow','AirVel':'SES AirVel','Humidity':'SES Humidity','Temperature':'Temperature (F)'})
    data=data.rename(columns={'Airflow':'SES Airflow','AirVel':'SES AirVel','Humidity':'SES Humidity','Temperature':'Temperature (F)'})
    d1=0.07020 #LB/CU FT from SES Output
    t1=107.0 + 459.67 #Ambient temperature in Rankine
    d1t1=d1*t1 #Ambient Density * Temperature in Rankine

    data['Density (lbm/ft^3)']=d1t1/(data['Temperature (F)']+459.67)
    data['Airflow (kcfm)']=data['SES Airflow']*d1/data['Density (lbm/ft^3)']
    data['Burnt Fuel (lbm/min)']=data['SES Humidity']*data['Airflow (kcfm)']*data['Density (lbm/ft^3)']*1000
    data['Airflow (m^3/s)']=data['Airflow (kcfm)']*0.47194745
    data['Temperature (C)']=(data['Temperature (F)']-32)*5/9
    data['Density (kg/m^3)']=data['Density (lbm/ft^3)']*16.0185
    data['Burnt Fuel (grams/sec)']=data['Burnt Fuel (lbm/min)']*453.592/60
    data['Air Mass Flow (kg/sec)']=data['Density (kg/m^3)']*data['Airflow (m^3/s)']
    data=data.reindex(columns=['SES Airflow','SES AirVel','SES Humidity',
                        'Airflow (kcfm)','Temperature (F)','Density (lbm/ft^3)','Burnt Fuel (lbm/min)',
                        'Airflow (m^3/s)','Temperature (C)','Density (kg/m^3)',  'Burnt Fuel (grams/sec)',
                        'Air Mass Flow (kg/sec)'])
    #Change sign convention for Segements
    #segs=[141,241]
    #cols=['Airflow (kcfm)','Burnt Fuel (lbm/min)','Airflow (m^3/s)','Burnt Fuel (grams/sec)','Air Mass Flow (kg/sec)']
    #for seg in segs:
    #    for col in cols:
    #        data.loc[(seg,slice(None)),col]=data.loc[(seg,slice(None)),col]*-1
    return data

#Function to get Output File to Parse
def get_input(simname= None, simtime= None, visname= None, version= None, outtype=None):
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
            if simtime == 'e':
                simtime = 'E'
        else:
            simtime = -1
            visname = "NA"
        ##FF - Future Feature - Check validity of input 
        return simname, simtime, visname, version, outtype


## FF - Future Feature to check for vailitidy
## def checkinput(filenames):
def get_visXML(visname):
    VZip = zipfile.ZipFile(visname)
    vxml = VZip.read('visio/pages/page2.xml') #reads the string FF - Just bring over the string name, not the xml
    vxmlname = 'page2.xml' #FF Eventually read all pages in this directory
    return vxml, vxmlname

def emod_visXML(vxml, airflow_dic, simname="Not Available", simtime="0.00"): #code to modify XML file for emergency simualtions
    P1root=ET.fromstring(vxml) #create XML element from the string
    ET.register_namespace('','http://schemas.microsoft.com/office/visio/2012/main') #Need to register name space to reproduce file.
    ns = {'Visio': 'http://schemas.microsoft.com/office/visio/2012/main'} #Namespace dictionary to ease file navigation

    #Find all shape with sub-child NV01_SegID. The "../.." at the end of the string moves the selection up two tiers to Shape
    for Shape in P1root.findall(".//Visio:Row[@N='NV01_SegID']../..",ns): 
        SegID=int(Shape.find(".//Visio:Row[@N='NV01_SegID']/Visio:Cell",ns).get('V')) #Get the value for the Segment ID from XML and save as SegID
        #airflow=str(abs(airflow_dic.get(SegID,0))) #Get absolute value of airflow from dictionary and change to string to update visio
        airflow=str(round(abs(airflow_dic.get(SegID,0)),1))
        ShapeChild=Shape.find(".//Visio:Shape[@Name='NV01_AirFlow']/Visio:Text",ns)#Finds all NV01_Airflow Shapes with text elements originally in file
        #ShapeChild2=Shape.find(".//Viqsio:Shape[@Name='NV01_AirFlow']/Text",ns)#FF - Move to Else statement to speed code. Code below finds all NV01_Airflow Shapes, text elements modified in file 
        if ET.iselement(ShapeChild): #If an original text element exists, replace with proper value.
            ShapeChild.text=airflow #previously str(Airflow)
        else:
            ShapeChild2=Shape.find(".//Visio:Shape[@Name='NV01_AirFlow']/Text",ns)
            if ET.iselement(ShapeChild2):
                ShapeChild2.text=airflow
            else: #Create a text element because none existed 
                ShapeChild3=Shape.find(".//Visio:Shape[@Name='NV01_AirFlow']",ns)
                ET.SubElement(ShapeChild3,"Text").text=airflow #previously str(Airflow)
        #Determine arrow direction
        if (airflow_dic.get(SegID,0) >= 0):
            Flip=0
        else:
            Flip=1    
        ShapeChild=Shape.find(".//Visio:Cell[@N='FlipX']",ns) #Find all Flipx properties originally in the file       
        if ET.iselement(ShapeChild):
            ShapeChild.set('V',str(Flip))
        else:
            ShapeChild2=Shape.find(".//Cell[@N='FlipX']",ns) #Find all Flipx properities create by modifications (something is wrong with namespace)
            if ET.iselement(ShapeChild2): 
                ShapeChild2.set('V',str(Flip))
            else: #Create a flip element because none existed
                ET.SubElement(Shape,"Cell",V=str(Flip),N='FlipX')
    #Simulation Name
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
        time = simtime
        if ET.iselement(ShapeChild): #If an original text element exists, replace with proper value.
            ShapeChild.text = str(time) #previously str(Airflow)
        else:
            ShapeChild2=Shape.find(".//Visio:Shape[@Name='NV01_SimTime']/Text",ns)
            if ET.iselement(ShapeChild2):
                ShapeChild2.text = str(time)
            else: #Create a text element because none existed 
                ShapeChild3=Shape.find(".//Visio:Shape[@Name='NV01_SimTime']",ns)
                ET.SubElement(ShapeChild3,"Text").text = str(time) #previously str(Airflow)
    ET.ElementTree(P1root).write("page2.xml",encoding='utf-8') #FF eliminate writing to disk in this procedure

def write_visio(visname, new_visio):
    #Sample Zip source code from https://stackoverflow.com/questions/513788/delete-file-from-zipfile-with-the-zipfile-module
    zin = zipfile.ZipFile (visname, 'r')
    zout = zipfile.ZipFile (new_visio, 'w')
    for item in zin.infolist(): 
        buffer = zin.read(item.filename)
        if (item.filename != 'visio/pages/page2.xml'): #writes all files except the page2.xml file to a new zip
            zout.writestr(item, buffer)
            #print(item.filename)
    zin.close()
    zout.close()
    zappend = zipfile.ZipFile (new_visio, 'a') #open file for appending
    zappend.write('page2.xml','visio/pages/page2.xml')
    zappend.close()
    os.remove('page2.xml')

def data_frame_2_Excel(data, excel_name = "Test.xlsx"): #Pass in Data Frame and excel_name
    # Write Panda to Excel File
    data.to_excel(excel_name)

def simtime_check(data,simtime):
    valid_times = data.index.get_level_values(0).unique().tolist()
    if simtime == 'E':
        simtime = str(int(valid_times[-1]))
    elif not (float(simtime) in valid_times): #check if simtime is valid
        print('Error - Requested time not in simulation. Using last time step')
        simtime = str(int(valid_times[-1]))
    return simtime

if __name__ == '__main__':
    repeat = True #Run the program the first time
    [simname, simtime, visname, version, outtype]= get_input () #Call to get input file names
    while repeat:
        if version != 'Q':
            data = parse_file(simname, version)#Creates a panda with the airflow out at all time steps
            simtime=simtime_check(data,simtime)
            #simname = simname[:-4] #eliminate four characters of suffix, such as .prn or .out
            if outtype !="E": #Create Visio Diagram
                airflow_dic=data.loc[float(simtime),'Airflow'].to_dict(dict) #Creates dictionary of airflow at specificed time
                [vxml,vxmlname] = get_visXML(visname) #gets the Page 1 XML. FF - Will search all Pages in Visio
                emod_visXML(vxml,airflow_dic, simname[:-4], str(simtime))
                new_visio = simname[:-4] + "-" + simtime + ".vsdx"
                write_visio(visname, new_visio)
                print('\n     Created Visio Diagram',new_visio)
                open_v = input('Open Visio file (Y/N): ') 
                if open_v.upper() == 'Y':
                    os.startfile(new_visio)
            print()
            if outtype !="V": #Create excel file of data
                # Write Panda to Excel File
                #segs = input('Enter segment numbers seperated by space: ')
                data=Excel_file(data)
                sample=data.loc[[141,122,241,222]]
                excel_name = simname[:-4] + ".xlsx"
                data_frame_2_Excel(sample,excel_name = excel_name)
                print('\n     Created Excel',excel_name)
            [simname, simtime, visname, version, outtype]=get_input(simname, simtime, visname, version, outtype)
        else: 
            repeat = False
    