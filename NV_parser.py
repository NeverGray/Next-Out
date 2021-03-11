import re
import pandas as pd
import numpy as np 
import logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

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
                \s{9,}\d+\s-                        #Section #Added \s{9.} to stop processing heat sink summaries
                (?P<Segment>\s{0,2}\d+)+\s-\s+    #Segment
                (?P<Sub>\s{0,2}\d+)\s{1,12}       #Sub-segment
				(?:(?P<Sensible>-?\d+\.\d+)\s+       #Sensible for tunnels
                (?P<Latent>-?\d+\.\d+)\s+|\s{28,})       #Latent for tunnels
				(?P<AirTemp>-?\d+\.\d+)\s+        #Air Temperature
                (?P<Humidity>-?\d+\.\d+)\s+       #Humidity
                (?:(?P<Airflow>-?\d+\.\d+)\s+     #Airflow for first line
                (?P<AirVel>-?\d+\.\d+)\s?|\s?)  #AirVel for first line #TODO add $ to speed code?
                )''', re.VERBOSE),
            'abb_segment_1': re.compile(r'''(
                \s+\d+\s-\s{0,2}                 #Section
                (?P<Segment>\d+)\s{1,11}         #Segment
                (?P<Airflow>-?\d+\.\d+)\s{1,6}   #Sub-segment
				(?P<AirVel>-?\d+\.\d+)\s{1,8}    #Air Velocity
				(?P<AirTemp>-?\d+\.\d+)\s{1,8}   #Air Temperature #TODO add $ to speed code?
                \s?
                )''', re.VERBOSE),
            'wall': re.compile(r'''(
                \d+\s-                        #Section
                (?P<Segment>\s{0,2}\d+)+\s-\s+    #Segment
                (?P<Sub>\s{0,2}\d+)\s{1,13}       #Sub-segment
                (?P<WallTemp>-?\d+\.\d+)\s{1,17}  #Wall Surface Temperature
                (?P<WallConvection>-?\d+\.\d+)\s{1,17} #Wall Convection
                (?P<WallRadiation>-?\d+\.\d+)$   #Wall Radition and End of string($) nothing else afterwards
                )''', re.VERBOSE)
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
   
def parse_file(filepath): #Parser for Point in Time data
    data_segment = []  # create an empty list to collect the data
    wall = []
    # open the file and read through it line by line
    with open(filepath, 'r') as file_object:
        lines = file_object.readlines() #Gets list of string values from the file, one string for each line of text
        #TODO determine version
        version = select_version(lines[0])
        version = 'i' #forced to be 4p1
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
    a = False #Starting value is there are no abbreviated prints
    while i < len(lines):
        # at each line check for a match with a regex
        m = False
        for key, rx in rx_dict.items(): #change dictionary as necessary
            m = rx.search(lines[i]) #using .match searched the beginning of the line
            if m is not None:
                m_dict = m.groupdict()
                m_dict['Time'] = time
                if key == 'time': #sets time interval
                    time = float(m.group('Time'))
                elif (key == 'detail_segment_1' or key == 'abb_segment_1'): #If key is other than time    
                    if key == 'abb_segment_1':
                        #Code only includes information for segment 1 for abbreviated prints
                        i +=1
                        m_dict.update({'Sub':int(1.0)})
                        s = lines[i]
                        s = s[1:45].strip() #HUmidity from one line below
                        m_dict.update({'Humidity':s}) #Add humidity from one line below, only first segement
                        if not a:
                            print("Warning - Not all thermal data is available with abbreviated prints. Eliminate abbreviated prints for more data.")
                            a = True
                    data_segment.append(m_dict) 
                elif key == "wall":
                    wall.append(m_dict)
                #break #TODO Would this break save time?
        i +=1
    df_segment = to_dataframe(data_segment)
    df_wall = to_dataframe(wall)
    df_segment = df_segment.join(df_wall, how='outer') #https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html
    if version == "i":
        df_segment['Airflow'] = df_segment['Airflow']/1000
    print("Post processed ",filepath)
    return df_segment

def to_dataframe(data):
     #convert all values to numbers, remove non-numbers. Then turn Segments and Sub into integers
    df = pd.DataFrame(data)
    to_integers=['Segment', 'Sub'] #Columns to become integer
    df = df.apply(pd.to_numeric, errors='coerce')
    for col in to_integers:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    df.set_index(['Time', 'Segment','Sub'], inplace=True)
    return df
