import datetime
import logging
import os
import re
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.DEBUG, format=" %(asctime)s - %(levelname)s - %(message)s"
)

# Second by Second parser definitions
PIT = {
    "time": re.compile(
        r"TIME.\s+(?P<Time>\d+.\d{2}).+SECONDS.+TRAIN"
    ),  # Find the first time Simulation
    "detail_segment_1": re.compile(
        r"""(
        \s{9,}\d+\s-                        #Section #Added \s{9.} to stop processing heat sink summaries
        (?P<Segment>\s{0,2}\d+)+\s-\s+    #Segment
        (?P<Sub>\s{0,2}\d+)\s{1,12}       #Sub-segment
        (?:(?P<Sensible>-?\d+\.\d+)\s+       #Sensible for tunnels
        (?P<Latent>-?\d+\.\d+)\s+|\s{28,})       #Latent for tunnels
        (?P<Air_Temp>-?\d+\.\d+)\s+        #Air Temperature
        (?P<Humidity>-?\d+\.\d+)\s+       #Humidity
        (?:(?P<Airflow>-?\d+\.\d+)\s+     #Airflow for first line
        (?P<Air_Velocity>-?\d+\.\d+)\s?|\s?)  #Air_Velocity for first line #TODO add $ to speed code?
        )""",
        re.VERBOSE,
    ),
    "abb_segment_1": re.compile(
        r"""(
        ^\s{2,4}\d{1,3}\s-\s{0,2}        #Section (Adjusted for Option 5 outputs)
        (?P<Segment>\d+)\s{1,11}         #Segment
        (?P<Airflow>-?\d+\.\d+)\s{1,6}   #Sub-segment
        (?P<Air_Velocity>-?\d+\.\d+)\s{1,8}    #Air Velocity
        (?P<Air_Temp>-?\d+\.\d+)\s{1,8}   #Air Temperature #TODO add $ to speed code?
        \s?
        )""",
        re.VERBOSE,
    ),
    "wall": re.compile(
        r"""(
        \d+\s-                        #Section
        (?P<Segment>\s{0,2}\d+)+\s-\s+    #Segment
        (?P<Sub>\s{0,2}\d+)\s{1,13}       #Sub-segment
        (?P<Wall_Temp>-?\d+\.\d+)\s{1,17}  #Wall Surface Temperature
        (?P<Convection_to_Wall>-?\d+\.\d+)\s{1,17} #Wall Convection
        (?P<Radiation_to_Wall>-?\d+\.\d+)$   #Wall Radition and End of string($) nothing else afterwards
        )""",
        re.VERBOSE,
    ),
    "train": re.compile(
        r"""(
        \s(?P<Train_Number>\d+)\s+    #Number
		(?P<Route_Number>\d+)\s?         #RTE
		(?P<Train_Type_Number>\d+)\s+         #Train_Type_Number
		(?P<Location>\d+\.\d*)\s+  #Location
		(?P<Speed>-?\d+\.\d*)\s+     #Speed
		(?P<Accel>-?\d+\.\d*)\s+     #Accel
		(?P<Air_Drag>-?\d+\.\d*)\s+
		(?P<Air_Drag_Coeff>-?\d+\.\d*)\s+
		(?P<Tractive_Effort>-?\d+\.\d*)\s+
		(?P<Motor_current>-?\d+\.\d*)\s+
		(?P<Line_Current>-?\d+\.\d*)\s+
		(?P<Fly_WHeel>-?\d+\.\d*)\s+
		((?P<M_Eff>-?\d+\.\d*)\s+|\s+) #Motor efficiency or NOTHING in IP
		(?P<Grid_Temp_Accel>-?\d+\.\d*)\s+
		(?P<Grid_Temp_Decel>-?\d+\.\d*)\s+	
		(?P<Heat_Gen>-?\d+\.\d*)\s+
		(?P<Heat_Reject>-?\d+\.\d*)
        )""",
        re.VERBOSE,
    ),
    "sum_time": re.compile(
        r"SUMMARY OF SIMULATION FROM\s+\d+\.\d+\sTO\s+(?P<Time>\d+.\d{2})\sSECONDS"
    ),  # Find the first time Simulation
    "fluid": re.compile(
        r"""(
        \s{15,}\d+\s-\s{0,2}        #Section #Added \s{9.} to stop processing heat sink summaries
        (?P<Segment>\d+)+\s-\s+     #Segment
        (?P<Sub>\s{0,2}\d+)\s{5,15} #Sub-segment
        (?P<Working_Fluid_Temp>-?\d+\.\d+)\s{5,22}  #Fluid_Temp
        (?P<Heat_Absorbed_by_Pipe>-?\d+\.\d+)   #Fluid_Temp
        )""",
        re.VERBOSE,
    ),
}

# Input data praser
INPUT = {
    "f3a": re.compile(
        r"INPUT VERIFICATION FOR (?P<type>LINE SEGMENT|VENTILATION SHAFT)\s+\d+\s\-\s*(?P<segment>\d+)\s+(?P<title>\S.+)+FORM"
    ),
    "f3a_2": re.compile(
        r"LINE SEGMENT TYPE.{72}\s*(?P<segment_type>\d+)\s+"
    ),
    "f12": re.compile(r"INPUT VERIFICATION OF CONTROL GROUP INFORMATION\s+FORM 12"),
    "f5a": re.compile(
        r"INPUT VERIFICATION FOR VENTILATION SHAFT\s+\d+\s\-\s*(?P<segment>\d+)\s+(?P<title>\S.+)+FORM"
    ),
    "f5c_fan_type": re.compile(r"FAN TYPE\s+(?P<fan_type>\d+)\s+FORM 5C"),
    "f5c_fan_on":re.compile(r"SIMULATION TIME AFTER WHICH FAN SWITCHES ON\s+(?P<fan_on>\d+)\s+SECONDS"),
    "f5c_fan_off":re.compile(r"SIMULATION TIME AFTER WHICH FAN SWITCHES OFF\s+(?P<fan_off>\d+)\s+SECONDS"),
    "f5c_fan_direction":re.compile(r"DIRECTION OF FAN OPERATION\s+(?P<fan_direction>\-?\d+)\s+"),
    "f5d_head_loss": re.compile(
        r"""(
        .{18}\..{15}.{15}\.\d+\s{12,} #Left hand side of line
        (?P<for_pos>\d+\.\d+)\s+
        (?P<for_neg>\d+\.\d+)\s+
        (?P<back_pos>\d+\.\d+)\s+
        (?P<back_neg>\d+\.\d+)\n
        )""",
        re.VERBOSE
    ),
    "f7c_A": re.compile(
        r"IMPULSE FAN TYPE\s{49,}(?P<fan_type>\d+)"
    ),
    "f7c_B":re.compile(
        r"FOR LINE SEGMENT TYPE\s{44,}(?P<segment_type>\d+)"
    ),
    "f7c_3":re.compile(
        r"IMPULSE FAN NOZZLE DISCHARGE VELOCITY\s+(?P<discharge_velocity>-?\d+\.\d+)\s+"
    ),
    "f7c_4":re.compile(
        r"SIMULATION TIME AFTER WHICH IMPULSE FAN SWITCHES ON\s+(?P<jet_fan_on>-?\d+\.\d+)\s+"
    ),
    "f7c_5":re.compile(
        r"SIMULATION TIME AFTER WHICH IMPULSE FAN SWITCHES OFF\s+(?P<jet_fan_off>-?\d+\.\d+)\s+"
    ),
    "f8a": re.compile(
        r"INPUT VERIFICATION FOR TRAIN ROUTE\s+(?P<Route_Number>\d+)\s+(?P<Title>\S.+)FORM"
    ),
    "f8f": re.compile(
        r"""(
        .{46}
        (?P<Segment>-?\d+)\s+
        (?P<Start>\d+\.\d+)\s{2}TO\s+
        (?P<End>\d+\.\d+)\n
        )""",
        re.VERBOSE
    ),

    "sum_op": re.compile(
        r"""(
        \d+\s+     #Group Number
        \d+\s+     #Number of intervals
        \d+.\d+\s+ #Interval length
        (?P<abb>\d+)\s+ #Number of abbreviated prints
        (?P<sum>\d+)\s-\s #Summary Option
        .+\d+\s+\d+\s+\d+\.\d+ #Remaining stuff
        )""",
        re.VERBOSE,
    ),
}
# Search pattern to determine if fill is in IP (instead of SI by default)
# Format of list is [[Line Number of text output, "Search String"]]
# Used in the function select_version
IP_INDICATION = [[1, "SES VER 4"], [52, "VERSION 4."], [9, "4.2"], [61, "4.2"]]

SUM = {
    "sum_time": re.compile(
        r"SUMMARY OF SIMULATION FROM\s+\d+\.\d+\sTO\s+(?P<Time>\d+.\d{2})\sSECONDS"
    ),  # Find the first time Simulation
    "airflow": re.compile(
        r"""(
            AIR\sFLOW\sRATE.+
            (?:\d+)+\s-\s*            #Section number (not used)
            (?P<Segment>\d+)\s{5,}    #Segment number
            (?P<Max_Airflow>-?\d+\.\d*)\s+    #Airflow rate maximum
            (?P<Max_Airflow_Time>\d+\.\d*)\s+  #Time of airflow rate maximum
            (?P<Min_Airflow>-?\d+\.\d*)\s+    #Airflow rate minimum
            (?P<Min_Airflow_Time>\d+\.\d*)\s+  #Time of airflow rate minimum
            (?P<Average_Positive_Airflow>\d+\.\d*)\s+      #Percentage of time airflow is positive
            (?P<Average_Negative_Airflow>-?\d+\.\d*)$         #Percentage of time airflow is negative
            )""",
        re.VERBOSE,
    ),
    "velocity": re.compile(
        r"""(
            AIR\sVELOCITY\s.+
            (?:\d+)+\s-\s*  
            (?P<Segment>\d+)\s{5,}
            (?P<Max_Velocity>-?\d+\.\d*)\s+    #Velocity maximum
            (?P<Max_Velocity_Time>-?\d+\.\d*)\s+  #time of velocity maximum
            (?P<Min_Velocity>-?\d+\.\d*)\s+    #velocity minimum
            (?P<Min_Velocity_Time>-?\d+\.\d*)\s+  #time of velocity minimjum
            (?P<Average_Velocity_Positive>-?\d+\.\d*)\s+      #average value positive
            (?P<Average_Velocity_Negative>-?\d+\.\d*)$         #average value negative
            )""",
        re.VERBOSE,
    ),
    "airflow_direction": re.compile(
        r"""(
            AIR\sFLOW\sDIRECTION.+
            (?:\d+)+\s-\s*            #Section number (not used)
            (?P<Segment>\d+)\s{5,}    #Segment number
            (?P<Airflow_Direction_Positive>\d+\.\d*)\s+    #Airflow direction percentage positive
            (?P<Airflow_Direction_Negative>\d+\.\d*)$       #Airflow direction precentage negative
            )""",
        re.VERBOSE,
    ),
    "temperature": re.compile(
        r"""(
            .{33,}                       #Space or 'Dry-Bulb Temperature'
            (?:\d+)\s-                   #Section number (not used)
            (?P<Segment>\s*\d+)\s-       #Segment number
            (?P<Sub>\s*\d+)\s{4,}            #Segment number
            (?P<Max_Dry_Bulb>-?\d+\.\d*)\s+    #Velocity maximum
            (?P<Max_Dry_Bulb_Time>-?\d+\.\d*)\s{7,}  #time of velocity maximum. {7,} to prevent precentage of time
            (?P<Min_Dry_Bulb>-?\d+\.\d*)\s+    #velocity minimum
            (?P<Min_Dry_Bulb_Time>-?\d+\.\d*)\s+  #time of velocity minimjum
            (?P<Average_Positive_Dry_Bulb>-?\d+\.\d*)\s+      #average value positive
            (?P<Average_Negative_Dry_Bulb>-?\d+\.\d*)$         #average value negative
            )""",
        re.VERBOSE,
    ),
    "humidity": re.compile(
        r"""(
            .{33,}
            (?:\d+)\s-                   #Section number (not used)
            (?P<Segment>\s*\d+)\s-       #Segment number
            (?P<Sub>\s*\d+)\s{4,}        #Segment number
            (?P<Max_Humidity>-?\d+\.\d*)\s+     #Humidity maximum
            (?P<Max_Humidity_Time>-?\d+\.\d*)\s+   #time of humidity maximum
            (?P<Min_Humidity>-?\d+\.\d*)\s+     #humidity minimum
            (?P<Min_Humidity_Time>-?\d+\.\d*)\s+   #time of humidity minimum
            (?P<Average_Humidity>-?\d+\.\d*)$       #average value
            )""",
        re.VERBOSE,
    ),
    "percentage": re.compile(
        r"P E R C E N T A G E  O F  T I M E  T E M P E R A T U R E  I S  A B O V E"
    ),
    "V_E": re.compile(
        r"EXCEEDS\s+(?P<Outflow_Velocity_Exceedance>-?\d+\.\d+).+(?:\d+)\s-\s*(?P<Segment>\d+)\s{57,}(?P<Percentage_of_Velocity_Exceedance>-?\d+\.\d*)$"
    ),
    "HTPB": re.compile(
        r"TRAIN PROPULSION AND BRAKING SYSTEM HEAT\s+(?P<Train_Propulsion__and_Braking_Heat>-?\d+\.\d*)$"
    ),
    "HTA": re.compile(
        r"TRAIN AUXILIARY SYSTEM AND PASSENGER HEAT\s+(?P<Train_Aux_and_Passenger_Sensible>-?\d+\.\d*)\s+(?P<Train_Aux_and_Passenger_Latent>-?\d+\.\d*)$"
    ),
    "HSS": re.compile(
        r"SEGMENT STEADY-STATE HEAT SOURCES\s+(?P<Steady_State_Heat_Sensible>-?\d+\.\d*)\s+(?P<Steady_State_Heat_Latent>-?\d+\.\d*)$"
    ),
    "HU": re.compile(
        r"SEGMENT UNSTEADY-STATE HEAT SOURCES, EVAPORATION AND VISCOUS HEATING\s+(?P<Unsteady_State_Heat_Sensible>-?\d+\.\d*)\s+(?P<Unsteady_State_Heat_Latent>-?\d+\.\d*)$"
    ),
    "HE": re.compile(
        r"SEGMENT ENVIRONMENTAL CONTROL SYSTEM\s+(?P<Environental_Control_System_Sensible>-?\d+\.\d*)\s+(?P<Environental_Control_System_Latent>-?\d+\.\d*)$"
    ),
    "HC": re.compile(
        r"SEGMENT COOLING PIPES\s+(?P<Cooling_Pipes_Sensible>-?\d+\.\d?)\s+(?P<Cooling_Pipes_Latent>-?\d+\.\d*)$"
    ),
    "HS": re.compile(r"HEAT SINK\s+(?P<Heat_Sink>-?\d+\.\d*)$"),
    "train_energy": re.compile(r"\s{50,}TRAIN ENERGY SUMMARY"),
    "heat_sink": re.compile(r"\s{50,}SES HEAT SINK ANALYSIS")
}

PERCENTAGE = {
    "percent_temperature": re.compile(
        r"""(
        \s{50,}
        (?P<T1>-?\d+\.\d*)\s{5,} #Above Temperature 1 through 6
        (?P<T2>-?\d+\.\d*)\s{5,}
        (?P<T3>-?\d+\.\d*)\s{5,}
        (?P<T4>-?\d+\.\d*)\s{5,}
        (?P<T5>-?\d+\.\d*)\s{5,}
        (?P<T6>-?\d+\.\d*)$
        )""",
        re.VERBOSE,
    ),
    "percent_time": re.compile(
        r"""(
        \s{35,}
        (?:\d+)\s-                   #Section number (not used)
        (?P<Segment>\s*\d+)\s-       #Segment number
        (?P<Sub>\s*\d+)\s{3,}        #Segment number
        (?P<Percentage_Above_T1>-?\d+\.\d*)\s{5,}  #Pertentage of time above Temperature 1 through 6
        (?P<Percentage_Above_T2>-?\d+\.\d*)\s{5,}
        (?P<Percentage_Above_T3>-?\d+\.\d*)\s{5,}
        (?P<Percentage_Above_T4>-?\d+\.\d*)\s{5,}
        (?P<Percentage_Above_T5>-?\d+\.\d*)\s{5,}
        (?P<Percentage_Above_T6>-?\d+\.\d*)$
        )""",
        re.VERBOSE,
    ),
}

TES = {
    "es": re.compile(r"\s+ENERGY SECTOR\s*(?P<Energy_Sector>-?\d+)$"),
    "et": re.compile(r"\s+PROPULSION ENERGY FROM THIRD RAIL\s+(?P<From_Third_rail>-?\d*\.\d*)\s+"),
    "ef": re.compile(
        r"\s+EQUIVALENT THIRD RAIL PROPULSION ENERGY FROM FLYWHEEL\s+(?P<From_Flywheel>-?\d*\.\d*)\s+"
    ),
    "ea": re.compile(r"\s+AUXILIARY ENERGY\s+(?P<Auxiliary_Energy>-?\d*\.\d*)\s+"),
    "er": re.compile(
        r"\s+REGENERATED ENERGY ACCEPTED BY THIRD RAIL\s+(?P<Regenerated_Energy_to_Third_Rail>-?\d*\.\d*)\s+"
    ),
}

HE = {
    "ZN": re.compile(r"ZONE NUMBER\s*(?P<ZN>\d+)($|\s\s-)"),
    "uncontrolled": re.compile(
        r"""(
            \d+\s-                        #Section
            (?P<Segment>\s{0,2}\d+)+\s-\s+    #Segment
            (?P<Sub>\s{0,2}\d+)\s{1,12}       #Sub-segment
            (?P<Morning_Wall_Temp>-?\d+\.\d+)\s+       #Morning Wall Temperature
            (?P<Evening_Wall_Temp>-?\d+\.\d+)\s+       #Evening wall temperature
            (?P<Morning_Air_Temp>-?\d+\.\d+)\s+        #Morning air Temperature
            (?P<Evening_Air_Temp>-?\d+\.\d+)\s+       #Evening air temperature
            (?P<Morning_Humidity>-?\d+\.\d+)\s+     #Morning humidity
            (?P<Evening_Humidity>-?\d+\.\d+)$  #Evening humidity
            )""",
        re.VERBOSE,
    ),
    "controlled": re.compile(
        r"""(
            \d+\s-                        #Section
            (?P<Segment>\s{0,2}\d+)+\s-\s+    #Segment
            (?P<Sub>\s{0,2}\d+)\s{1,8}       #Sub-segment
            (?P<Trains_and_Misc_Sensible>\s{0,2}-?\d+)\s{1,8}       #Sensible heat load from trains and misc
            (?P<Trains_and_Misc_Latent>\s{0,2}-?\d+)\s{1,8}       #Latent
            (?P<Steady_State_Sensible>\s{0,2}-?\d+)\s{1,8}       #Sensible
            (?P<Steady_State_Latent>\s{0,2}-?\d+)\s{1,8}       #Latent
            (?P<Heat_Sink_Sensible>\s{0,2}-?\d+)\s{1,8}       #Sensible
            (?P<Airflow_Sensible>\s{0,2}-?\d+)\s{1,8}       #Sensible
            (?P<Airflow_Latent>\s{0,2}-?\d+)\s{1,8}       #Latent
            (?P<EC_Sensible>\s{0,2}-?\d+)\s{1,8}       #Sensible
            (?P<EC_Latent>\s{0,2}-?\d+)\s{1,8}       #Latent
            (?P<EC_Requirement_Sensible>\s{0,2}-?\d+)\s{1,8}       #Sensible
            (?P<EC_Requirement_Latent>\s{0,2}-?\d+)\s{1,8}       #Latent
            (?P<EC_Requirement_Total>\s{0,2}-?\d+)\s{1,8}$       #Latent
            )""",
        re.VERBOSE,
    ),
}

# TODO Eliminate NumExpr detected 16 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
def parse_file(file_path, gui=""):  # Parser
    # Variables for all referenced functions
    data_pit = []  # All Point in Time data
    data_train = []
    wall_pit = []
    fluid_pit = []
    output_meta_data = {"file_path": file_path}
    duplicate_pit = False
    # Global variables for all referenced functions
    global data_segment, data_sub, data_percentage, data_te, data_esc, data_hsa
    # Create empty lists to collect the data (and erase previous data)
    data_segment = []
    data_sub = []  # create an empty list to collect data for subsegments
    data_percentage = []
    data_te = []
    data_esc = []
    data_hsa = []
    file_name = file_path.name
    # Read output file into variable. OpenSES files require errors="replace" because of extended ASCII
    with open(file_path, "r", errors="replace") as file_object:
        lines = file_object.readlines()
        # Get modified time of file https://thispointer.com/python-get-last-modification-date-time-of-a-file-os-stat-os-path-getmtime/
        file_time_seconds = os.path.getmtime(file_path)
        file_time_str = datetime.datetime.fromtimestamp(file_time_seconds).strftime('%Y-%m-%d, %H:%M:%S')
        output_meta_data.update({"file_time": file_time_str})
    
    # Read input verification information form outputfile before Form 1
    version = select_version(lines)
    output_meta_data.update({"ses_version": version})
    
    # Read segment titles from Form 3 and Form 5 and types from form 3
    segment_titles, form3_type = get_titles_and_form3(lines)

    # Read damper position and fan data from Form 5
    # TODO Update to get open or closed status for Form 3. Combine with get_titles_and_form3.
    try:
        damper_position_dict, form5_fan_data_df = get_form5(lines)
        output_meta_data.update({"damper_position": damper_position_dict})
        output_meta_data.update({"form5_fan_data": form5_fan_data_df})
    except:
        msg = 'Error Processing Form 5 position'
        parser_msg(gui, msg)
    
    # Read jet fan data from Form 7C
    try:
        form7c_data = get_form7c(lines)
        jet_fan_data = get_jet_fan_data(form7c_data, form3_type)
        output_meta_data.update({"jet_fan_data": jet_fan_data})
    except:
        msg = 'Error Processing Form 7C, Jet Fan Data'
        parser_msg(gui, msg)

    # Read route data from Form 8F
    try:
        form8f_df = get_form8fs(lines)
        output_meta_data.update({"form_8f": form8f_df})
    except:
        msg = 'Error Processing Form 8F'
        parser_msg(gui, msg)

    # Determine if there are abbreviated prints from Form 12.
    m = None  # Sets the value equal to none to start while loop
    rx = INPUT["f12"]  # Matching string for Form 12 Output
    i = 0  # Start at first line
    while m is None and i < len(lines):
        m = rx.search(lines[i])
        i += 1
        assert i < (len(lines) - 1), "Cannot find Form 12! Line variable " + str(i)
    summary = False
    abbreviated = False
    rx = PIT["time"]
    rx2 = INPUT["sum_op"]
    m = None
    while m is None and i < len(lines):
        m = rx.search(lines[i])  # Find time variable for start of simulation output
        m2 = rx2.search(lines[i])
        if m2 is not None:
            if int(m2.group("abb")) > 0:
                abbreviated = True
            if int(m2.group("sum")) > 1:
                summary = True
        i += 1
        if i > (len(lines) - 1):
            parser_msg(
                gui,
                "Error in reading output file "
                + file_name
                + ". Simulation never started.",
            )
            return []
        assert i < (len(lines)), "Cannot find first time! Line variable " + str(i)
    if abbreviated:  # First time an abbreviated print is read
        parser_msg(
            gui,
            "Warning - "
            + file_name
            + " has abbreviated prints. Use detailed prints for more thermal data.",
        )
    time = float(m.group("Time"))  # Finds first line with simulation output with Time.
    # Post process Point in Time information
    while i < len(lines):
        # at each line check for a match with a regex
        m = False
        for key, rx in PIT.items():  # change dictionary as necessary
            m = rx.search(lines[i])  # using .match searched the beginning of the line
            if m is not None:
                m_dict = m.groupdict()
                m_dict["Time"] = time
                if key == "time":  # sets time interval
                    # Needed to delete duplicates created by Summary output option 4
                    if float(m.group("Time")) == time:
                        duplicate_pit = True
                    time = float(m.group("Time"))
                # If key is other than time
                elif key == "detail_segment_1" or key == "abb_segment_1":
                    if key == "abb_segment_1":
                        # Code only includes information for segment 1 for abbreviated prints
                        i += 1
                        m_dict.update({"Sub": int(1.0)})
                        s = lines[i]
                        s = s[1:45].strip()  # HUmidity from one line below
                        m_dict.update(
                            {"Humidity": s}
                        )  # Add humidity from one line below, only first segement
                    data_pit.append(m_dict)
                elif key == "wall":
                    wall_pit.append(m_dict)
                elif (
                    key == "sum_time"
                ):  # TODO - Create code to find where all summary data is located
                    start_line = i
                    end_line = start_line
                    end_found = False
                    while (
                        not end_found
                    ):  # Find the lines containing the percentage of time data
                        assert end_line < (
                            len(lines)
                        ), "Error with Train Energy Summary, Line " + str(i)
                        m_sum = PIT["time"].search(lines[end_line + 1])
                        if (m_sum is not None) or (
                            end_line > len(lines) - 3
                        ):  # Train Energy does not continue
                            end_found = True
                            i = end_line
                            end_line -= 1
                        end_line += 1
                    sum_parser(lines[start_line:end_line], time)
                elif key == "train":  # Create worksheet for train information
                    data_train.append(m_dict)
                elif key == "fluid":
                    fluid_pit.append(m_dict)
        i += 1



    df_ssa, df_sst, df_train = create_ss_dfs(
        data_pit,
        data_train,
        wall_pit,
        fluid_pit,
        duplicate_pit,
        segment_titles,
        version,
    )

    if summary:
        df_segment = to_dataframe2(
            data_segment,
            to_integers=["Segment"],
            to_index=["Time", "Segment"],
            groupby=["Time", "Segment"],
        )
        df_segment.name = "SA"
        if version == "ip":
            to_convert = ["Max_Airflow", "Min_Airflow", "Average_Positive_Airflow", "Average_Negative_Airflow"]
            for item in to_convert:
                df_segment[item] = df_segment[item] / 1000
        df_sub = to_dataframe2(data_sub, groupby=["Time", "Segment", "Sub"])
        df_sub.name = "ST"
        df_percentage = to_dataframe2(data_percentage)
        df_percentage.name = "PER"
        df_te = to_dataframe2(data_te, to_integers=["Energy_Sector"], to_index=["Time", "Energy_Sector"])
        df_te.name = "TES"
        df_hsa = to_dataframe2(
            data_hsa,
            to_integers=["Segment", "Sub", "ZN"],
            to_index=["Time", "ZN", "Segment", "Sub"],
        )
        df_hsa.name = "HSA"
        df_ecs = to_dataframe2(
            data_esc,
            to_integers=["Segment", "Sub", "ZN"],
            to_index=["Time", "ZN", "Segment", "Sub"],
        )
        df_ecs.name = "ECS"
        parser_msg(gui, "Read data from " + file_name)
        # Reduce memory requirements when multiple files are being processed.
        data_segment = []
        data_sub = []
        data_percentage = []
        data_te = []
        data_esc = []
        data_hsa = []
        data = create_dictionary_from_list([
            df_ssa,
            df_sst,
            df_train,
            df_segment,
            df_sub,
            df_percentage,
            df_te,
            df_hsa,
            df_ecs,
        ])
        return data, output_meta_data
    elif len(data_train) > 0:
        data_train = []
        parser_msg(gui, "Read data from " + file_name)
        data = create_dictionary_from_list([df_ssa, df_sst, df_train])
        return data, output_meta_data
    else:
        parser_msg(gui, "Read data from " + file_name)
        data = create_dictionary_from_list([df_ssa, df_sst])
        return data, output_meta_data

def create_dictionary_from_list(df_list):
    df_dict = {}
    for df in df_list:
        df_dict.update({df.name: df})
    return df_dict

def get_segment_titles(lines):
    title_rx = INPUT["f3a"]
    time_rx = PIT["time"]
    time_match = None
    i = 0
    segment_titles = {}
    while time_match is None and i < len(lines):
        title_match = title_rx.search(lines[i])
        time_match = time_rx.search(lines[i])
        if title_match is not None:
            title_dict = title_match.groupdict()
            segment_titles.update(
                {int(title_dict["segment"]): title_dict["title"].strip()}
            )
        i += 1
    return segment_titles

def get_titles_and_form3(lines):
    title_rx = INPUT["f3a"]
    time_rx = PIT["time"]
    time_match = None
    i = 0
    segment_titles = {}
    form3_type = {}
    while time_match is None and i < len(lines):
        title_match = title_rx.search(lines[i])
        time_match = time_rx.search(lines[i])
        if title_match is not None:
            title_dict = title_match.groupdict()
            segment_titles.update(
                {int(title_dict["segment"]): title_dict["title"].strip()}
            )
            #Form 3 data
            if title_dict['type'] == "LINE SEGMENT":
                i +=2
                form3_type.update(
                    {int(title_dict["segment"]):int(INPUT['f3a_2'].search(lines[i])[1])}
                )
        i += 1
    return segment_titles, form3_type

def get_form5(lines):
    title_rx = INPUT["f5a"]
    f5d_head_loss = INPUT["f5d_head_loss"]
    time_rx = PIT["time"] #signals start of simualtion and end of input
    time_match = None
    i = 0
    form5_data = {}
    form5_fan_data = []
    segment_number = 0
    while time_match is None and i < len(lines):
        title_match = title_rx.search(lines[i])
        head_loss_match = f5d_head_loss.search(lines[i])
        time_match = time_rx.search(lines[i])
        fan_type_match = INPUT['f5c_fan_type'].search(lines[i])
        if title_match is not None:
            title_dict = title_match.groupdict()
            segment_number = int(title_dict["segment"])
            form5_data.update(
                {segment_number: "OPEN"}
            )
        elif fan_type_match is not None:
            fan_dict = {'Segment': segment_number}
            fan_dict.update(fan_type_match.groupdict())
            i +=2
            fan_dict.update(INPUT['f5c_fan_on'].search(lines[i]).groupdict())
            i +=2
            fan_dict.update(INPUT['f5c_fan_off'].search(lines[i]).groupdict())
            i +=2
            fan_dict.update(INPUT['f5c_fan_direction'].search(lines[i]).groupdict())
            form5_fan_data.append(fan_dict) 
        elif head_loss_match is not None:
            head_loss_dict = head_loss_match.groupdict()
            head_loss_list = list(map(float,head_loss_dict.values()))
            if sum(head_loss_list) >= 1998:
                form5_data[segment_number] = "CLOSED"
        i +=1
    form5_fan_data_df = pd.DataFrame(form5_fan_data)
    form5_fan_data_df.set_index("Segment", inplace=True)
    return form5_data, form5_fan_data_df  

def get_form7c(lines):
    first_line = INPUT["f7c_A"]
    time_rx = PIT["time"] #signals start of simualtion and end of input
    time_match = None
    i = 0
    form7c_data = []
    segment_number = 0
    while time_match is None and i < len(lines):
        time_match = time_rx.search(lines[i])
        first_line_match = first_line.search(lines[i])
        if first_line_match is not None:
            form7c_dict = first_line_match.groupdict()
            i +=1
            form7c_dict.update(INPUT['f7c_B'].search(lines[i]).groupdict())
            i +=7
            form7c_dict.update(INPUT['f7c_3'].search(lines[i]).groupdict())
            i +=2
            form7c_dict.update(INPUT['f7c_4'].search(lines[i]).groupdict())
            i +=2
            form7c_dict.update(INPUT['f7c_5'].search(lines[i]).groupdict())
            form7c_data.append(form7c_dict)
        i +=1
    return form7c_data

def get_jet_fan_data(form7c_data, form3_type):
    jet_fan_data = []
    form7c_df = pd.DataFrame(form7c_data)
    form7c_df = form7c_df.apply(pd.to_numeric, errors="coerce")
    form7c_df.set_index("segment_type",inplace=True)
    form3_type_df = pd.DataFrame.from_dict(form3_type,orient='index',columns=['segment_type'])
    form3_type_df.index.set_names('segment_ID',inplace=True)
    form3_type_df = form3_type_df .apply(pd.to_numeric, errors="coerce")
    jet_fan_data = form3_type_df.join(form7c_df,on="segment_type",how="inner")
    return jet_fan_data

def get_form8fs(lines):
    title_rx = INPUT["f8a"]
    form_8f = INPUT["f8f"]
    time_rx = PIT["time"] #signals start of simualtion and end of input
    time_match = None
    i = 0
    form8f_data = []
    while time_match is None and i < len(lines):
        title_match = title_rx.search(lines[i])
        form_8f_match = form_8f.search(lines[i])
        time_match = time_rx.search(lines[i])
        if title_match is not None:
            title_dict = title_match.groupdict()
            route_number = int(title_dict['Route_Number'])
        elif form_8f_match is not None:
            form_8f_dict = form_8f_match.groupdict()
            form_8f_dict.update({"Route_Number" : route_number})
            form8f_data.append(form_8f_dict)
        i +=1
    #Convert from list to dataframes
    form8f_df = pd.DataFrame(form8f_data)
    form8f_df = form8f_df.apply(pd.to_numeric, errors="coerce")
    form8f_df.set_index(['Route_Number','Segment'], inplace=True)
    return form8f_df 

def create_ss_dfs(
    data_pit, data_train, wall_pit, fluid_pit, duplicate_pit, segment_titles, version
):
    df_pit = to_dataframe2(data_pit)
    # Merge additional data based on https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html
    if len(wall_pit) > 0:  # If wall tempature exists
        df_wall_pit = to_dataframe2(wall_pit)
        df_pit = df_pit.join(df_wall_pit, how="outer")
    if len(fluid_pit) > 0:  # If fluid tempature exists
        df_fluid_pit = to_dataframe2(fluid_pit)
        df_pit = df_pit.join(df_fluid_pit, how="outer")
    if version == "ip":
        df_pit["Airflow"] = df_pit["Airflow"] / 1000
    df_pit.name = "PIT"
    df_train = to_dataframe2(data_train, ["Train_Number", "Route_Number", "Train_Type_Number"], ["Time","Train_Number"])
    df_train.name = "TRA"
    if duplicate_pit:
        [df_pit, df_train] = delete_duplicate_pit(df_pit, df_train)
    # Add title to segments in df_pit
    # TODO Add title name to PIT from segment_data to Segment number
    # Create df_ssa
    df_ssa = df_pit.query("Sub == 1")
    df_ssa = df_ssa.loc[:, {"Airflow", "Air_Velocity"}]
    df_ssa.reset_index(level=2, inplace=True)
    # Create Unique ID with code from https://stackoverflow.com/questions/19377969/combine-two-columns-of-text-in-pandas-dataframe
    df_ssa["ID"] = (
        df_ssa.index.get_level_values(0).astype(str)
        + "_"
        + df_ssa.index.get_level_values(1).astype(str)
    )
    df_segment_titles = pd.DataFrame.from_dict(
        segment_titles, orient="index", columns=["Title"]
    )
    df_segment_titles.index.name = "Segment"
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.join.html#pandas.DataFrame.join
    df_ssa = df_ssa.join(df_segment_titles, on="Segment")
    df_ssa = df_ssa[
        ["ID", "Title", "Airflow", "Air_Velocity"]
    ]  # Reorders and Drops Sub column
    df_ssa.name = "SSA"
    # Create df_sst
    df_sst = df_pit.drop(["Airflow", "Air_Velocity"], axis=1)
    df_sst["ID"] = (
        df_sst.index.get_level_values(0).astype(str)
        + "_"
        + df_sst.index.get_level_values(1).astype(str)
        + "_"
        + df_sst.index.get_level_values(2).astype(str)
    )
    column_names = df_sst.columns.values.tolist()
    if len(column_names) == 5:
        df_sst = df_sst[
            [
                "ID",
                "Air_Temp",
                "Humidity",
                "Sensible",
                "Latent",
            ]
        ]
    elif len(column_names) == 7:
        df_sst = df_sst[
            [
                "ID",
                "Air_Temp",
                "Humidity",
                "Sensible",
                "Latent",
                'Working_Fluid_Temp', 
                'Heat_Absorbed_by_Pipe'
            ]
        ]
    elif len(column_names) == 8:
        df_sst = df_sst[
            [
                "ID",
                "Air_Temp",
                "Humidity",
                "Sensible",
                "Latent",
                'Wall_Temp', 
                'Convection_to_Wall', 
                'Radiation_to_Wall',
            ]
        ]
    else:
        df_sst = df_sst[["ID", "Air_Temp", "Humidity", "Sensible", "Latent",]]

    df_sst.name = "SST"
    # TODO Change order of columns, add ID
    return df_ssa, df_sst, df_train


def to_dataframe2(
    data,
    to_integers=["Segment", "Sub"],
    to_index=["Time", "Segment", "Sub"],
    groupby=[],
):
    # convert all values to numbers, remove non-numbers. Then turn Segments and Sub into integers
    if len(data) > 0:
        df = pd.DataFrame(data)
        df = df.apply(pd.to_numeric, errors="coerce")
        for col in to_integers:
            df[col] = pd.to_numeric(df[col], downcast="integer")
        df.set_index(to_index, inplace=True)
        if len(groupby) > 0:
            df = df.groupby(groupby).sum()
        if not df.index.is_lexsorted():
            df = (
                df.sort_index()
            )  # Speeds up future referencing and prevents errors with finding data
    else:
        df = pd.DataFrame([{"No Data": "No Data"}])
    return df


def select_version(lines):
    version = "si"
    for item in IP_INDICATION:
        line_number = item[0]
        array_number = line_number - 1
        if item[1] in lines[array_number]:
            version = "ip"
    return version


def sum_parser(lines, time):  # Parser for summary portion of output, between times
    i = 0  # start at line zero
    while i < len(lines):
        # at each line check for a match with a regex
        m = False
        if lines[i] != "\n":
            for key, rx in SUM.items():
                # using .match searched the beginning of the line
                m = rx.search(lines[i])  
                if m is not None:
                    m_dict = m.groupdict()
                    m_dict["Time"] = time
                    if key == "sum_time":  # sets time interval
                        time = float(m.group("Time"))
                        m_dict["Time"] = time
                    # Found precentage of time temperature is above data
                    elif (key == "percentage"):  
                        start_line = i + 2
                        end_line = start_line + 3
                        # Find the lines containing the percentage of time data
                        while (lines[end_line] != "\n"):  
                            end_line += 1
                            assert i < (len(lines) - 1), (
                                "Error with precentage of time temperature is above, line "
                                + str(i)
                            )
                        percentage = percentage_parser(lines[start_line:end_line], time)
                        for item in percentage:
                            data_percentage.append(item)
                        i = end_line
                    elif key == "train_energy":
                        start_line = i
                        end_line = start_line
                        end_found = False
                        while (
                            not end_found
                        ):  # Find the lines containing the percentage of time data
                            if "\f" in lines[end_line]:
                                m = SUM["train_energy"].search(lines[end_line + 1])
                                if m is None:  # Train Energy does not continue
                                    end_found = True
                                    i = end_line
                                    end_line -= 1
                            end_line += 1
                            assert i < (
                                len(lines) - 1
                            ), "Error with Train Energny Summary, Line " + str(i)
                        train_energy = te_parser(lines[start_line:end_line], time)
                        for item in train_energy:
                            data_te.append(item)
                        i = end_line
                        # TODO Heat_Sink post processing
                    elif key == "heat_sink":
                        start_line = i
                        end_line = len(lines)
                        [hsu, esc] = he_parser(lines[start_line:end_line], time)
                        for item in hsu:
                            data_hsa.append(item)
                        for item in esc:
                            data_esc.append(item)
                        i = end_line
                    elif not "Segment" in m_dict:
                        m_dict["Segment"] = last_segment
                        data_segment.append(m_dict)
                    elif not "Sub" in m_dict:  # no subsegment information
                        data_segment.append(m_dict)
                        last_segment = m_dict["Segment"]
                    else:
                        data_sub.append(m_dict)
                        last_segment = m_dict["Segment"]
                    break
        i += 1


def percentage_parser(p_lines, time):
    m = PERCENTAGE["percent_temperature"].search(p_lines[0])
    ta = m.groupdict()
    i = 3
    percent_list = []
    while i < len(p_lines):
        m = PERCENTAGE["percent_time"].search(p_lines[i])
        line_dict = {}
        line_dict["Time"] = time
        line_dict.update(m.groupdict())
        line_dict.update(ta)
        percent_list.append(line_dict)
        i += 1
    return percent_list


def te_parser(p_lines, time):
    '''TES = {
        "es": re.compile(r"\s+ENERGY SECTOR\s*(?P<ES>\d+)$"),
        "et": re.compile(
            r"\s+PROPULSION ENERGY FROM THIRD RAIL\s+(?P<ET>-?\d*\.\d*)\s+"
        ),
        "ef": re.compile(
            r"\s+EQUIVALENT THIRD RAIL PROPULSION ENERGY FROM FLYWHEEL\s+(?P<EF>-?\d*\.\d*)\s+"
        ),
        "ea": re.compile(r"\s+AUXILIARY ENERGY\s+(?P<EA>-?\d*\.\d*)\s+"),
        "er": re.compile(
            r"\s+REGENERATED ENERGY ACCEPTED BY THIRD RAIL\s+(?P<ER>-?\d*\.\d*)\s+"
        ),
    }'''
    # TODO write pseduo code
    i = 7
    te_list = []
    te_dict = {}
    while i < len(p_lines):
        m = TES["es"].search(p_lines[i])
        if m:
            te_dict = {}  # reset values in te_dict
            te_dict["Time"] = time
            te_dict.update(m.groupdict())
            i += 3
            m = TES["et"].search(p_lines[i])
            te_dict.update(m.groupdict())
            i += 2
            m = TES["ef"].search(p_lines[i])
            te_dict.update(m.groupdict())
            i += 2
            m = TES["ea"].search(p_lines[i])
            te_dict.update(m.groupdict())
            i += 2
            m = TES["er"].search(p_lines[i])
            te_dict.update(m.groupdict())
            te_list.append(te_dict)
        i += 1
    return te_list


def he_parser(p_lines, time):
    i = 6
    he_dict = {}
    hec_list = []  # List for controlled
    heu_list = []  # list heat sink analysis
    while i < len(p_lines):
        for key, rx in HE.items():  # change dictionary as necessary
            m = rx.search(p_lines[i])  # using .match searched the beginning of the line
            if m is not None:
                he_dict = {}  # reset dictionary
                he_dict = m.groupdict()
                if key == "ZN":
                    zn = he_dict["ZN"]
                elif key == "uncontrolled":
                    he_dict["Time"] = time
                    he_dict["ZN"] = zn
                    heu_list.append(he_dict)
                else:  # Controlled
                    he_dict["Time"] = time
                    he_dict["ZN"] = zn
                    hec_list.append(he_dict)
                break
        i += 1
    return heu_list, hec_list

def delete_duplicate_pit(df_pit, df_train):
    # One set of answers https://stackoverflow.com/questions/13035764/remove-pandas-rows-with-duplicate-indices
    new_df_pit = df_pit[~df_pit.index.duplicated(keep="last")]
    new_df_pit.name = df_pit.name
    new_df_train = df_train[~df_train.index.duplicated(keep="last")]
    new_df_train.name = df_train.name
    return [new_df_pit, new_df_train]


def parser_msg(gui, text):
    if gui != "":
        gui.gui_text(text)
    else:
        print("Parser msg: " + text)


if __name__ == "__main__":
    path_string = "C:/Users/msn/OneDrive - Never Gray/Software Development/Next-Vis/Projects and Issues/2021-09-01 Stencils/sinorm-detailed.out"
    file_path = Path(path_string)
    d, output_meta_data = parse_file(file_path)
    print(list, output_meta_data, "test finished", sep = '\n')