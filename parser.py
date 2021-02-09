import re
import pandas as pd
import logging
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
				(?P<Sensible>-?\d+\.\d+)\s+       #Sensible
                (?P<Latent>-?\d+\.\d+)\s+)       #Latent
				(?P<AirTemp>-?\d+\.\d+)\s+        #Air Temperature
                (?P<Humidity>-?\d+\.\d+)\s+       #Humidity
                ((?P<Airflow>-?\d+\.\d+)\s+       #Airflow if first line
                (?P<AirVel>-?\d+\.\d+)\s+|\s+  #AirVel if first line
                )''', re.VERBOSE),
            'detail_vent_1': re.compile(r'''(
               \s+\d+\s-\s{0,2}                     #Section
                (?P<Segment>\d+)\s-\s{0,2}           #Segment
                (?P<Sub>\d)\s{29,}                   #Sub-segment
                (?P<AirTemp>-?\d+\.\d+)\s+           #Air Temperature
                (?P<Humidity>-?\d+\.\d+)\s+          #Humidity
                ((?P<Airflow>-?\d+\.\d+)\s+          #Airflow
                (?P<AirVel>-?\d+\.\d+)\s?|\s?)\n     #Air Velocity
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
    return data_segment

if __name__ == '__main__':
    repeat = True #Run the program the first time
    #[simname, simtime, visname, version, outtype]= get_input () #Call to get input file names
    simname = 'siinfern.out'
    #simname = 'NV-6p0-Base02.out'
    version = 'S'
    data = parse_file(simname, version)#Creates a panda with the airflow out at all time steps
    #simtime = simtime_check(data,simtime)