import parser
import re
import pandas as pd

def sum_parser(filepath): #Parser for summary prints
    version = "i"
    data_segment = []  # create an empty list to collect the data
    data_sub =[] #create an empty list to collect data for subsegments
    data_percentage = []
    data_te = []
    data_hsc = []
    data_hsu = []
    with open(filepath, 'r') as file_object:
        lines = file_object.readlines() #Gets list of string values from the file, one string for each line of text
    i = 0 #Start at first line
    m = None #Sets the value equal to none to start while loop
    SUM = { 
        'sum_time': re.compile(r'SUMMARY OF SIMULATION FROM\s+\d+\.\d+\sTO\s+(?P<Time>\d+.\d{2})\sSECONDS'), #Find the first time Simulation
        'airflow': re.compile(r'''(
            AIR\sFLOW\sRATE.+
            (?:\d+)+\s-\s*            #Section number (not used)
            (?P<Segment>\d+)\s{5,}    #Segment number
            (?P<A_Max>\d+\.\d*)\s+    #Airflow rate maximum
            (?P<A_Max_T>\d+\.\d*)\s+  #Time of airflow rate maximum
            (?P<A_Min>\d+\.\d*)\s+    #Airflow rate minimum
            (?P<A_Min_T>\d+\.\d*)\s+  #Time of airflow rate minimum
            (?P<A_P>\d+\.\d*)\s+      #Percentage of time airflow is positive
            (?P<A_N>\d+\.\d*)$         #Percentage of time airflow is negative
            )''', re.VERBOSE),
        'velocity': re.compile(r'''(
            AIR\sVELOCITY\s.+
            (?:\d+)+\s-\s*  
            (?P<Segment>\d+)\s{5,}
            (?P<V_Max>\d+\.\d*)\s+    #Velocity maximum
            (?P<V_Max_T>\d+\.\d*)\s+  #time of velocity maximum
            (?P<V_Min>\d+\.\d*)\s+    #velocity minimum
            (?P<V_Min_T>\d+\.\d*)\s+  #time of velocity minimjum
            (?P<V_P>\d+\.\d*)\s+      #average value positive
            (?P<V_N>\d+\.\d*)$         #average value negative
            )''', re.VERBOSE),
        'airflow_direction': re.compile(r'''(
            AIR\sFLOW\sDIRECTION.+
            (?:\d+)+\s-\s*            #Section number (not used)
            (?P<Segment>\d+)\s{5,}    #Segment number
            (?P<A_P_P>\d+\.\d*)\s+    #Airflow direction percentage positive
            (?P<A_P_N>\d+\.\d*)$       #Airflow direction precentage negative
            )''', re.VERBOSE),
        'temperature': re.compile(r'''(
            .{33,}                       #Space or 'Dry-Bulb Temperature'
            (?:\d+)\s-                   #Section number (not used)
            (?P<Segment>\s*\d+)\s-       #Segment number
            (?P<Sub>\s*\d+)\s{4,}            #Segment number
            (?P<T_Max>-?\d+\.\d*)\s+    #Velocity maximum
            (?P<T_Max_T>-?\d+\.\d*)\s{7,}  #time of velocity maximum. {7,} to prevent precentage of time
            (?P<T_Min>-?\d+\.\d*)\s+    #velocity minimum
            (?P<T_Min_T>-?\d+\.\d*)\s+  #time of velocity minimjum
            (?P<T_P>-?\d+\.\d*)\s+      #average value positive
            (?P<T_N>-?\d+\.\d*)$         #average value negative
            )''', re.VERBOSE),
        'humidity':re.compile(r'''(
            .{33,}
            (?:\d+)\s-                   #Section number (not used)
            (?P<Segment>\s*\d+)\s-       #Segment number
            (?P<Sub>\s*\d+)\s{4,}        #Segment number
            (?P<W_Max>-?\d+\.\d*)\s+     #Humidity maximum
            (?P<W_Max_T>-?\d+\.\d*)\s+   #time of humidity maximum
            (?P<W_Min>-?\d+\.\d*)\s+     #humidity minimum
            (?P<W_Min_T>-?\d+\.\d*)\s+   #time of humidity minimum
            (?P<W_A>-?\d+\.\d*)$       #average value
            )''', re.VERBOSE),
        'percentage':re.compile(r'P E R C E N T A G E  O F  T I M E  T E M P E R A T U R E  I S  A B O V E'),
        'V_E':re.compile(r'EXCEEDS\s+(?P<V_E>-?\d+\.\d+).+(?:\d+)\s-\s*(?P<Segment>\d+)\s{57,}(?P<V_EP>-?\d+\.\d*)$'),
        'HTPB': re.compile(r'TRAIN PROPULSION AND BRAKING SYSTEM HEAT\s+(?P<HTPB>-?\d+\.\d*)$'),
        'HTA': re.compile(r'TRAIN AUXILIARY SYSTEM AND PASSENGER HEAT\s+(?P<HTAS>-?\d+\.\d*)\s+(?P<HTAL>-?\d+\.\d*)$'),
        'HSS':re.compile(r'SEGMENT STEADY-STATE HEAT SOURCES\s+(?P<HSS>-?\d+\.\d*)\s+(?P<HSL>-?\d+\.\d*)$'),
        'HU':re.compile(r'SEGMENT UNSTEADY-STATE HEAT SOURCES, EVAPORATION AND VISCOUS HEATING\s+(?P<HUS>-?\d+\.\d*)\s+(?P<HUL>-?\d+\.\d*)$'),
        'HE':re.compile(r'SEGMENT ENVIRONMENTAL CONTROL SYSTEM\s+(?P<HES>-?\d+\.\d*)\s+(?P<HEL>-?\d+\.\d*)$'),
        'HC':re.compile(r'SEGMENT COOLING PIPES\s+(?P<HCS>-?\d+\.\d?)\s+(?P<HCL>-?\d+\.\d*)$'),
        'HS':re.compile(r'HEAT SINK\s+(?P<HS>-?\d+\.\d*)$'),
        'train_energy':re.compile(r'\s{50,}TRAIN ENERGY SUMMARY'),
        'heat_sink':re.compile(r'\s{50,}SES HEAT SINK ANALYSIS')
        #May need to update 'segmentdetail' in SI to Match IP by replace '-..1' with '-\s{2}1'
        #test parser using https://www.debuggex.com/
        }
    while m is None and i < len(lines):
            rx = SUM['sum_time']
            m = rx.search(lines[i])
            i +=1
    assert (i < (len(lines) - 1)), 'Cannot find first time! Line variable number is ' + str(i) 
    time = float(m.group('Time'))
    last_segment = 0
    while i < len(lines):
        # at each line check for a match with a regex
        m = False
        if lines[i] != '\n':
            for key, rx in SUM.items(): #change dictionary as necessary
                m = rx.search(lines[i]) #using .match searched the beginning of the line
                if m is not None:
                    m_dict = m.groupdict()
                    m_dict['Time'] = time
                    if key == 'sum_time': #sets time interval
                        time = float(m.group('Time'))
                    elif key == 'percentage': #Found precentage of time temperature is above data
                        start_line = i + 2
                        end_line = start_line +3
                        while lines[end_line] != '\n': #Find the lines containing the percentage of time data
                            end_line +=1   
                            assert (i < (len(lines) - 1)), 'Error with precentage of time temperature is above, line ' + str(i) 
                        percentage = percentage_parser(lines[start_line:end_line],time)
                        for item in percentage:
                            data_percentage.append(item)
                        i = end_line
                    #TODO Update function
                    elif key == 'train_energy':
                        start_line = i
                        end_line = start_line
                        end_found = False
                        while not end_found: #Find the lines containing the percentage of time data
                            if '\f' in lines[end_line]:
                                m = SUM['train_energy'].search(lines[end_line + 1])
                                if m is None: #Train Energy does not continue
                                    end_found = True
                                    i = end_line
                                    end_line -=1
                            end_line +=1   
                            assert (i < (len(lines) - 1)), 'Error with Train Energeny Summary, Line ' + str(i) 
                        train_energy = te_parser(lines[start_line:end_line],time)
                        for item in train_energy:
                            data_te.append(item)
                        i = end_line
                        #TODO Heat_Sink post processing
                    elif key == 'heat_sink':
                        start_line = i
                        end_line = start_line
                        end_found = False
                        while not end_found:
                            if '\f' in lines[end_line]:
                                if lines[end_line+3].startswith('TIME'):
                                    end_found = True
                                elif 'END OF SIMULATION' in lines[end_line-1]:
                                    end_found = True
                            end_line +=1
                        [hsc, hsu] = he_parser(lines[start_line:end_line],time)
                        for item in hsc:
                            data_hsc.append(item)
                        for item in hsu:
                            data_hsu.append(item)
                        i = end_line
                    elif not 'Segment' in m_dict:
                        m_dict['Segment'] = last_segment 
                    elif not 'Sub' in m_dict: #no subsegment information
                        data_segment.append(m_dict)
                        last_segment = m_dict['Segment']
                    else:
                        data_sub.append(m_dict)
                        last_segment = m_dict['Segment']
                    break
        i +=1
    #TODO Conversions to use "def to_dataframe(data)"
    #Convert data_segment to Dataframe
    df = pd.DataFrame(data_segment)
    to_integers=['Segment'] #Columns to become integer
    df = df.apply(pd.to_numeric, errors='coerce')
    for col in to_integers:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    df.set_index(['Time', 'Segment'], inplace=True)
    df = df.groupby(['Time','Segment']).sum()
    
    #Convert data_sub to Dataframe
    df_sub = pd.DataFrame(data_sub)
    to_integers=['Segment','Sub'] #Columns to become integer
    df_sub = df_sub.apply(pd.to_numeric, errors='coerce')
    for col in to_integers:
        df_sub[col] = pd.to_numeric(df_sub[col], downcast='integer')
    df_sub.set_index(['Time', 'Segment','Sub'], inplace=True)
    df_sub = df_sub.groupby(['Time','Segment','Sub']).sum()
    
    #Convert data_percent to dataframe
    df_percent = pd.DataFrame(data_percentage)
    to_integers=['Segment','Sub'] #Columns to become integer
    df_percent = df_percent.apply(pd.to_numeric, errors='coerce')
    for col in to_integers:
        df_percent[col] = pd.to_numeric(df_percent[col], downcast='integer')
    df_percent.set_index(['Time', 'Segment','Sub'], inplace=True)
    
    #Convert data_percent to dataframe
    df_te = pd.DataFrame(data_te)
    to_integers=['ES'] #Columns to become integer
    df_te = df_te.apply(pd.to_numeric, errors='coerce')
    for col in to_integers:
        df_te[col] = pd.to_numeric(df_te[col], downcast='integer')
    df_te.set_index(['Time', 'ES'], inplace=True)
    
    #Convert heat sinks to dataframe
    df_hsu = pd.DataFrame(data_hsu)
    to_integers=['Segment','Sub'] #Columns to become integer
    df_hsu = df_hsu.apply(pd.to_numeric, errors='coerce')
    for col in to_integers:
        df_hsu[col] = pd.to_numeric(df_hsu[col], downcast='integer')
    df_hsu.set_index(['Time','ZN','Segment','Sub'], inplace=True) 

    df_hsc = pd.DataFrame(data_hsc)
    to_integers=['Segment','Sub'] #Columns to become integer
    df_hsc = df_hsc.apply(pd.to_numeric, errors='coerce')
    for col in to_integers:
        df_hsc[col] = pd.to_numeric(df_hsc[col], downcast='integer')
    df_hsc.set_index(['Time','ZN','Segment','Sub'], inplace=True) 

    return df, df_sub, df_percent, df_te, df_hsu, df_hsc


def percentage_parser(p_lines,time):
    PERCENTAGE = {    
    'percent_temperature': re.compile(r'''(
        \s{50,}
        (?P<TA_1>-?\d+\.\d*)\s{5,} #Above Temperature 1 through 6
        (?P<TA_2>-?\d+\.\d*)\s{5,}
        (?P<TA_3>-?\d+\.\d*)\s{5,}
        (?P<TA_4>-?\d+\.\d*)\s{5,}
        (?P<TA_5>-?\d+\.\d*)\s{5,}
        (?P<TA_6>-?\d+\.\d*)$
        )''', re.VERBOSE),
    'percent_time': re.compile(r'''(
        \s{35,}
        (?:\d+)\s-                   #Section number (not used)
        (?P<Segment>\s*\d+)\s-       #Segment number
        (?P<Sub>\s*\d+)\s{3,}        #Segment number
        (?P<TAP_1>-?\d+\.\d*)\s{5,}  #Pertentage of time above Temperature 1 through 6
        (?P<TAP_2>-?\d+\.\d*)\s{5,}
        (?P<TAP_3>-?\d+\.\d*)\s{5,}
        (?P<TAP_4>-?\d+\.\d*)\s{5,}
        (?P<TAP_5>-?\d+\.\d*)\s{5,}
        (?P<TAP_6>-?\d+\.\d*)$
        )''', re.VERBOSE),
    }
    m = PERCENTAGE['percent_temperature'].search(p_lines[0])
    ta = m.groupdict()
    i = 3
    percent_list = []
    while i < len(p_lines):
        m = PERCENTAGE['percent_time'].search(p_lines[i])
        line_dict = {}
        line_dict['Time'] = time
        line_dict.update(m.groupdict())
        line_dict.update(ta)
        percent_list.append(line_dict)
        i +=1
    return percent_list

def te_parser(p_lines,time):
    TE = {    
    'es':re.compile(r'\s+ENERGY SECTOR\s*(?P<ES>\d+)$'),
    'et': re.compile(r'\s+PROPULSION ENERGY FROM THIRD RAIL\s+(?P<ET>-?\d*\.\d*)\s+'),
    'ef': re.compile(r'\s+EQUIVALENT THIRD RAIL PROPULSION ENERGY FROM FLYWHEEL\s+(?P<EF>-?\d*\.\d*)\s+'),
    'ea': re.compile(r'\s+AUXILIARY ENERGY\s+(?P<EA>-?\d*\.\d*)\s+'),
    'er': re.compile(r'\s+REGENERATED ENERGY ACCEPTED BY THIRD RAIL\s+(?P<ER>-?\d*\.\d*)\s+'),
    }
    #TODO write pseduo code
    i = 7
    te_list = []
    te_dict = {}
    while i < len(p_lines):
        m = TE['es'].search(p_lines[i])
        if m:
            te_dict = {} #reset values in te_dict
            te_dict['Time'] = time 
            te_dict.update(m.groupdict())
            i += 3
            m = TE['et'].search(p_lines[i])
            te_dict.update(m.groupdict())
            i +=2
            m = TE['ef'].search(p_lines[i])
            te_dict.update(m.groupdict())
            i +=2
            m = TE['ea'].search(p_lines[i])
            te_dict.update(m.groupdict())
            i +=2
            m = TE['er'].search(p_lines[i])
            te_dict.update(m.groupdict())
            te_list.append(te_dict)
        i +=1
    return te_list

def he_parser(p_lines,time):
    HE = {    
        'ZN':re.compile(r'ZONE NUMBER\s*(?P<ZN>\d+)($|\s\s-)'),
        'uncontrolled': re.compile(r'''(
                \d+\s-                        #Section
                (?P<Segment>\s{0,2}\d+)+\s-\s+    #Segment
                (?P<Sub>\s{0,2}\d+)\s{1,12}       #Sub-segment
				(?P<MWT>-?\d+\.\d+)\s+       #Morning Wall Temperature
                (?P<EWT>-?\d+\.\d+)\s+       #Evening wall temperature
				(?P<MAT>-?\d+\.\d+)\s+        #Morning air Temperature
                (?P<EAT>-?\d+\.\d+)\s+       #Evening air temperature
                (?P<MH>-?\d+\.\d+)\s+     #Morning humidity
                (?P<EH>-?\d+\.\d+)$  #Evening humidity
                )''', re.VERBOSE),
        'controlled':re.compile(r'''(
                \d+\s-                        #Section
                (?P<Segment>\s{0,2}\d+)+\s-\s+    #Segment
                (?P<Sub>\s{0,2}\d+)\s{1,8}       #Sub-segment
                (?P<TM_S>\s{0,2}-?\d+)\s{1,8}       #Sensible heat load from trains and misc
                (?P<TM_L>\s{0,2}-?\d+)\s{1,8}       #Latent
                (?P<SS_S>\s{0,2}-?\d+)\s{1,8}       #Sensible
                (?P<SS_L>\s{0,2}-?\d+)\s{1,8}       #Latent
                (?P<HS_S>\s{0,2}-?\d+)\s{1,8}       #Sensible
                (?P<A_S>\s{0,2}-?\d+)\s{1,8}       #Sensible
                (?P<A_L>\s{0,2}-?\d+)\s{1,8}       #Latent
                (?P<EC_S>\s{0,2}-?\d+)\s{1,8}       #Sensible
                (?P<EC_L>\s{0,2}-?\d+)\s{1,8}       #Latent
                (?P<TR_S>\s{0,2}-?\d+)\s{1,8}       #Sensible
                (?P<TR_L>\s{0,2}-?\d+)\s{1,8}       #Latent
                (?P<TR_T>\s{0,2}-?\d+)\s{1,8}$       #Latent
                )''', re.VERBOSE),
    }
    #TODO write pseduo code to process uncontrolled zones
    i = 6
    he_dict = {}
    hec_list = [] #List for controlled
    heu_list = [] #list for uncontrolled
    while i < len(p_lines):
        for key, rx in HE.items(): #change dictionary as necessary
            m = rx.search(p_lines[i]) #using .match searched the beginning of the line
            if m is not None:
                he_dict = {} #reset dictionary
                he_dict = m.groupdict()
                if key == 'ZN':
                    zn = he_dict['ZN']
                elif key == 'uncontrolled':
                    he_dict['Time'] = time
                    he_dict['ZN'] = zn
                    heu_list.append(he_dict)
                else: #Controlled
                    he_dict['Time'] = time
                    he_dict['ZN'] = zn
                    hec_list.append(he_dict)
                break
        i+=1
    return hec_list, heu_list

if __name__ == '__main__':
    #multiprocessing.freeze_support() #Required for multiprocess to work with Pyinstaller on windows computers
    #initialize a few variables
    Testing = True
    settings = {}
    #TODO Create arguments for command line   Follow further instructions at https://docs.python.org/3/howto/argparse.html
    #parser = argparse.ArgumentParser()
    #parser.parse_args()    
    if Testing:
        settings={
            'simname' : 'sinorm.out',
            'visname' : 'Template20210209.vsdx',
            'simtime' : 2000.0,
            'version' : 'tbd',
            'control' : 'Stop'
        }
        answers = sum_parser(settings['simname'])
        #with pd.HDFStore('sinormal.h5') as store:
        #    store['sinorm']=data
        print('Done')