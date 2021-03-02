import parser
import re

def sum_parser(filepath): #Parser for Point in Time data
    version = "i"
    data = []  # create an empty list to collect the data
    with open(filepath, 'r') as file_object:
        lines = file_object.readlines() #Gets list of string values from the file, one string for each line of text
    i = 0 #Start at first line
    m = None #Sets the value equal to none to start while loop
    rx_dict = { 
        'sum_time': re.compile(r'SUMMARY OF SIMULATION FROM\s+\d+\.\d+\sTO\s+(?P<Time>\d+.\d{2})\sSECONDS'), #Find the first time Simulation
        'airflow': re.compile(r'''(
            AIR\sFLOW\sRATE.+
            (?P<Section>\d+)+\s-\s+   
            (?P<Segment>\d+)\s{5,}
            (?P<A_Max>\d+\.\d?)\s+    #Airflow rate maximum
            (?P<A_Max_T>\d+\.\d?)\s+  #Time of airflow rate maximum
            (?P<A_Min>\d+\.\d?)\s+    #Airflow rate minimum
            (?P<A_Min_T>\d+\.\d?)\s+  #Time of airflow rate minimum
            (?P<A_P>\d+\.\d?)\s+      #Percentage of time airflow is positive
            (?P<A_N>\d+\.\d?)\s+      #Percentage of time airflow is negative
            )''', re.VERBOSE),
        'velocity': re.compile(r'''(
            AIR\sVELOCITY\s.+
            (?P<Section>\d+)+\s-\s+  
            (?P<Segment>\d+)\s{5,}
            (?P<V_Max>\d+\.\d?)\s+    #Velocity maximum
            (?P<V_Max_T>\d+\.\d?)\s+  #time of velocity maximum
            (?P<V_Min>\d+\.\d?)\s+    #velocity minimum
            (?P<V_Min_T>\d+\.\d?)\s+  #time of velocity minimjum
            (?P<V_P>\d+\.\d?)\s+      #average value positive
            (?P<V_N>\d+\.\d?)\s+      #average value negative
            )''', re.VERBOSE),
        'heat': re.compile(r'''(
            
            )''', re.VERBOSE),
        #May need to update 'segmentdetail' in SI to Match IP by replace '-..1' with '-\s{2}1'
        #test parser using https://www.debuggex.com/
        }    
    while m is None and i < len(lines):
            rx = rx_dict['sum_time']
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
                    data.append(m_dict) 
                elif key == "wall":
                    wall.append(m_dict)
        i +=1
    df_segment = to_dataframe(data_segment)
    df_wall = to_dataframe(wall)
    df_segment = df_segment.join(df_wall, how='outer') #https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html
    if version == "i":
        df_segment['Airflow'] = df_segment['Airflow']/1000
    print("Post processed ",filepath)
    return df_segment

if __name__ == '__main__':
    multiprocessing.freeze_support() #Required for multiprocess to work with Pyinstaller on windows computers
    #initialize a few variables
    Testing = True
    settings = {}
    #TODO Create arguments for command line   Follow further instructions at https://docs.python.org/3/howto/argparse.html
    #parser = argparse.ArgumentParser()
    #parser.parse_args()    
    if Testing:
        settings={
            'simname' : 'inferno4p1.PRN',
            'visname' : 'Template20210209.vsdx',
            'simtime' : 2000.0,
            'version' : 'tbd',
            'control' : 'Stop'
        }
        data = sum_parser(settings['simname'])
        with pd.HDFStore('inferno.h5') as store:
            store['i4p1']=data
        print('Done')