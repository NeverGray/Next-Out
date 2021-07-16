import logging
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
        (?P<AirTemp>-?\d+\.\d+)\s+        #Air Temperature
        (?P<Humidity>-?\d+\.\d+)\s+       #Humidity
        (?:(?P<Airflow>-?\d+\.\d+)\s+     #Airflow for first line
        (?P<AirVel>-?\d+\.\d+)\s?|\s?)  #AirVel for first line #TODO add $ to speed code?
        )""",
        re.VERBOSE,
    ),
    "abb_segment_1": re.compile(
        r"""(
        ^\s{2,4}\d{1,3}\s-\s{0,2}        #Section (Adjusted for Option 5 outputs)
        (?P<Segment>\d+)\s{1,11}         #Segment
        (?P<Airflow>-?\d+\.\d+)\s{1,6}   #Sub-segment
        (?P<AirVel>-?\d+\.\d+)\s{1,8}    #Air Velocity
        (?P<AirTemp>-?\d+\.\d+)\s{1,8}   #Air Temperature #TODO add $ to speed code?
        \s?
        )""",
        re.VERBOSE,
    ),
    "wall": re.compile(
        r"""(
        \d+\s-                        #Section
        (?P<Segment>\s{0,2}\d+)+\s-\s+    #Segment
        (?P<Sub>\s{0,2}\d+)\s{1,13}       #Sub-segment
        (?P<WallTemp>-?\d+\.\d+)\s{1,17}  #Wall Surface Temperature
        (?P<WallConvection>-?\d+\.\d+)\s{1,17} #Wall Convection
        (?P<WallRadiation>-?\d+\.\d+)$   #Wall Radition and End of string($) nothing else afterwards
        )""",
        re.VERBOSE,
    ),
    "train": re.compile(
        r"""(
        \s(?P<Number>\d+)\s+    #Number
		(?P<RTE>\d+)\s?         #RTE
		(?P<TYP>\d+)\s+         #TYP
		(?P<Location>\d+\.\d*)\s+  #Location
		(?P<Speed>-?\d+\.\d*)\s+     #Speed
		(?P<Accel>-?\d+\.\d*)\s+     #Accel
		(?P<Draf_KN>-?\d+\.\d*)\s+
		(?P<Draf_COEFF>-?\d+\.\d*)\s+
		(?P<Tractive>-?\d+\.\d*)\s+
		(?P<M_Current>-?\d+\.\d*)\s+
		(?P<L_Current>-?\d+\.\d*)\s+
		(?P<FLY>-?\d+\.\d*)\s+
		((?P<M_Eff>-?\d+\.\d*)\s+|\s+) #Motor efficiency or NOTHING in IP
		(?P<G_Accel>-?\d+\.\d*)\s+
		(?P<G_Decel>-?\d+\.\d*)\s+	
		(?P<H_Gen>-?\d+\.\d*)\s+
		(?P<H_Reject>-?\d+\.\d*)
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
        (?P<FluidTemp>-?\d+\.\d+)\s{5,22}  #Fluid_Temp
        (?P<FluidHeat>-?\d+\.\d+)   #Fluid_Temp
        )""",
        re.VERBOSE,
    ),
}

# Input data praser
INPUT = {
    "f3a": re.compile(
        r"INPUT VERIFICATION FOR (LINE SEGMENT|VENTILATION SHAFT)\s+\d+\s\-\s*(?P<segment>\d+)\s+(?P<title>\S.+)+FORM"
    ),
    "f12": re.compile(r"INPUT VERIFICATION OF CONTROL GROUP INFORMATION\s+FORM 12"),
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

SUM = {  # TODO replace sum_time value with PIT value of PIT['sum_time']?
    "sum_time": re.compile(
        r"SUMMARY OF SIMULATION FROM\s+\d+\.\d+\sTO\s+(?P<Time>\d+.\d{2})\sSECONDS"
    ),  # Find the first time Simulation
    "airflow": re.compile(
        r"""(
            AIR\sFLOW\sRATE.+
            (?:\d+)+\s-\s*            #Section number (not used)
            (?P<Segment>\d+)\s{5,}    #Segment number
            (?P<A_Max>-?\d+\.\d*)\s+    #Airflow rate maximum
            (?P<A_Max_T>\d+\.\d*)\s+  #Time of airflow rate maximum
            (?P<A_Min>-?\d+\.\d*)\s+    #Airflow rate minimum
            (?P<A_Min_T>\d+\.\d*)\s+  #Time of airflow rate minimum
            (?P<A_P>\d+\.\d*)\s+      #Percentage of time airflow is positive
            (?P<A_N>-?\d+\.\d*)$         #Percentage of time airflow is negative
            )""",
        re.VERBOSE,
    ),
    "velocity": re.compile(
        r"""(
            AIR\sVELOCITY\s.+
            (?:\d+)+\s-\s*  
            (?P<Segment>\d+)\s{5,}
            (?P<V_Max>-?\d+\.\d*)\s+    #Velocity maximum
            (?P<V_Max_T>-?\d+\.\d*)\s+  #time of velocity maximum
            (?P<V_Min>-?\d+\.\d*)\s+    #velocity minimum
            (?P<V_Min_T>-?\d+\.\d*)\s+  #time of velocity minimjum
            (?P<V_P>-?\d+\.\d*)\s+      #average value positive
            (?P<V_N>-?\d+\.\d*)$         #average value negative
            )""",
        re.VERBOSE,
    ),
    "airflow_direction": re.compile(
        r"""(
            AIR\sFLOW\sDIRECTION.+
            (?:\d+)+\s-\s*            #Section number (not used)
            (?P<Segment>\d+)\s{5,}    #Segment number
            (?P<A_P_P>\d+\.\d*)\s+    #Airflow direction percentage positive
            (?P<A_P_N>\d+\.\d*)$       #Airflow direction precentage negative
            )""",
        re.VERBOSE,
    ),
    "temperature": re.compile(
        r"""(
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
            )""",
        re.VERBOSE,
    ),
    "humidity": re.compile(
        r"""(
            .{33,}
            (?:\d+)\s-                   #Section number (not used)
            (?P<Segment>\s*\d+)\s-       #Segment number
            (?P<Sub>\s*\d+)\s{4,}        #Segment number
            (?P<W_Max>-?\d+\.\d*)\s+     #Humidity maximum
            (?P<W_Max_T>-?\d+\.\d*)\s+   #time of humidity maximum
            (?P<W_Min>-?\d+\.\d*)\s+     #humidity minimum
            (?P<W_Min_T>-?\d+\.\d*)\s+   #time of humidity minimum
            (?P<W_A>-?\d+\.\d*)$       #average value
            )""",
        re.VERBOSE,
    ),
    "percentage": re.compile(
        r"P E R C E N T A G E  O F  T I M E  T E M P E R A T U R E  I S  A B O V E"
    ),
    "V_E": re.compile(
        r"EXCEEDS\s+(?P<V_E>-?\d+\.\d+).+(?:\d+)\s-\s*(?P<Segment>\d+)\s{57,}(?P<V_EP>-?\d+\.\d*)$"
    ),
    "HTPB": re.compile(
        r"TRAIN PROPULSION AND BRAKING SYSTEM HEAT\s+(?P<HTPB>-?\d+\.\d*)$"
    ),
    "HTA": re.compile(
        r"TRAIN AUXILIARY SYSTEM AND PASSENGER HEAT\s+(?P<HTAS>-?\d+\.\d*)\s+(?P<HTAL>-?\d+\.\d*)$"
    ),
    "HSS": re.compile(
        r"SEGMENT STEADY-STATE HEAT SOURCES\s+(?P<HSS>-?\d+\.\d*)\s+(?P<HSL>-?\d+\.\d*)$"
    ),
    "HU": re.compile(
        r"SEGMENT UNSTEADY-STATE HEAT SOURCES, EVAPORATION AND VISCOUS HEATING\s+(?P<HUS>-?\d+\.\d*)\s+(?P<HUL>-?\d+\.\d*)$"
    ),
    "HE": re.compile(
        r"SEGMENT ENVIRONMENTAL CONTROL SYSTEM\s+(?P<HES>-?\d+\.\d*)\s+(?P<HEL>-?\d+\.\d*)$"
    ),
    "HC": re.compile(
        r"SEGMENT COOLING PIPES\s+(?P<HCS>-?\d+\.\d?)\s+(?P<HCL>-?\d+\.\d*)$"
    ),
    "HS": re.compile(r"HEAT SINK\s+(?P<HS>-?\d+\.\d*)$"),
    "train_energy": re.compile(r"\s{50,}TRAIN ENERGY SUMMARY"),
    "heat_sink": re.compile(r"\s{50,}SES HEAT SINK ANALYSIS")
    # May need to update 'segmentdetail' in SI to Match IP by replace '-..1' with '-\s{2}1'
    # test parser using https://www.debuggex.com/
}

PERCENTAGE = {
    "percent_temperature": re.compile(
        r"""(
        \s{50,}
        (?P<TA_1>-?\d+\.\d*)\s{5,} #Above Temperature 1 through 6
        (?P<TA_2>-?\d+\.\d*)\s{5,}
        (?P<TA_3>-?\d+\.\d*)\s{5,}
        (?P<TA_4>-?\d+\.\d*)\s{5,}
        (?P<TA_5>-?\d+\.\d*)\s{5,}
        (?P<TA_6>-?\d+\.\d*)$
        )""",
        re.VERBOSE,
    ),
    "percent_time": re.compile(
        r"""(
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
        )""",
        re.VERBOSE,
    ),
}

TES = {
    "es": re.compile(r"\s+ENERGY SECTOR\s*(?P<ES>-?\d+)$"),
    "et": re.compile(r"\s+PROPULSION ENERGY FROM THIRD RAIL\s+(?P<ET>-?\d*\.\d*)\s+"),
    "ef": re.compile(
        r"\s+EQUIVALENT THIRD RAIL PROPULSION ENERGY FROM FLYWHEEL\s+(?P<EF>-?\d*\.\d*)\s+"
    ),
    "ea": re.compile(r"\s+AUXILIARY ENERGY\s+(?P<EA>-?\d*\.\d*)\s+"),
    "er": re.compile(
        r"\s+REGENERATED ENERGY ACCEPTED BY THIRD RAIL\s+(?P<ER>-?\d*\.\d*)\s+"
    ),
}

HE = {
    "ZN": re.compile(r"ZONE NUMBER\s*(?P<ZN>\d+)($|\s\s-)"),
    "uncontrolled": re.compile(
        r"""(
            \d+\s-                        #Section
            (?P<Segment>\s{0,2}\d+)+\s-\s+    #Segment
            (?P<Sub>\s{0,2}\d+)\s{1,12}       #Sub-segment
            (?P<MWT>-?\d+\.\d+)\s+       #Morning Wall Temperature
            (?P<EWT>-?\d+\.\d+)\s+       #Evening wall temperature
            (?P<MAT>-?\d+\.\d+)\s+        #Morning air Temperature
            (?P<EAT>-?\d+\.\d+)\s+       #Evening air temperature
            (?P<MH>-?\d+\.\d+)\s+     #Morning humidity
            (?P<EH>-?\d+\.\d+)$  #Evening humidity
            )""",
        re.VERBOSE,
    ),
    "controlled": re.compile(
        r"""(
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
            )""",
        re.VERBOSE,
    ),
}

# TODO Eliminate NumExpr detected 16 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
def parse_file(path_string, gui=""):  # Parser
    # Variables for all referenced functions
    data_pit = []  # All Point in Time data
    data_train = []
    wall_pit = []
    fluid_pit = []
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
    file_path = Path(path_string)
    file_name = file_path.name
    # Read output file into variable. Errors="replace" needed for OpenSES files
    with open(path_string, "r", errors="replace") as file_object:
        lines = file_object.readlines()
    i = 0  # Start at first line
    version = select_version(lines)
    m = None  # Sets the value equal to none to start while loop
    # TODO get title information for Form 3 and 5
    rx = INPUT["f12"]  # Matching string for Form 12 Output
    while m is None and i < len(lines):
        m = rx.search(lines[i])
        i += 1
        assert i < (len(lines) - 1), "Cannot find Form 12! Line variable " + str(i)
    summary = False
    abbreviated = False
    rx = PIT["time"]
    rx2 = INPUT["sum_op"]
    m = None
    # Determine if there are abbreviated prints from Fom 12.
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

    segment_titles = get_segment_titles(lines)

    df_ssa, df_sst, df_train = create_ss_dfs(
        data_pit,
        data_train,
        wall_pit,
        fluid_pit,
        duplicate_pit,
        segment_titles,
        version,
    )

    # TODO Create post process all dataframes
    if summary:
        df_segment = to_dataframe2(
            data_segment,
            to_integers=["Segment"],
            to_index=["Time", "Segment"],
            groupby=["Time", "Segment"],
        )
        df_segment.name = "SEG"
        if version == "ip":
            to_convert = ["A_Max", "A_Min", "A_P", "A_N"]
            for item in to_convert:
                df_segment[item] = df_segment[item] / 1000
        df_sub = to_dataframe2(data_sub, groupby=["Time", "Segment", "Sub"])
        df_sub.name = "SUB"
        df_percentage = to_dataframe2(data_percentage)
        df_percentage.name = "PER"
        df_te = to_dataframe2(data_te, to_integers=["ES"], to_index=["Time", "ES"])
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
        parser_msg(gui, "Read data form " + file_name)
        # Reduce memory requirements when multiple files are being processed.
        data_segment = []
        data_sub = []
        data_percentage = []
        data_te = []
        data_esc = []
        data_hsa = []
        return [
            df_ssa,
            df_sst,
            df_train,
            df_segment,
            df_sub,
            df_percentage,
            df_te,
            df_hsa,
            df_ecs,
        ]
    elif len(data_train) > 0:
        data_train = []
        parser_msg(gui, "Read data from " + file_name)
        return [df_ssa, df_sst, df_train]
    else:
        parser_msg(gui, "Read data from " + file_name)
        return [df_ssa, df_sst]


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
    df_train = to_dataframe2(data_train, ["Number", "RTE", "TYP"], ["Time", "Number"])
    df_train.name = "TRA"
    if duplicate_pit:
        [df_pit, df_train] = delete_duplicate_pit(df_pit, df_train)
    # Add title to segments in df_pit
    # TODO Add title name to PIT from segment_data to Segment number
    # Create df_ssa
    df_ssa = df_pit.query("Sub == 1")
    df_ssa = df_ssa.loc[:, {"Airflow", "AirVel"}]
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
        ["ID", "Title", "Airflow", "AirVel"]
    ]  # Reorders and Drops Sub column
    df_ssa.name = "SSA"
    # Create df_sst
    df_sst = df_pit.drop(["Airflow", "AirVel"], axis=1)
    df_sst["ID"] = (
        df_sst.index.get_level_values(0).astype(str)
        + "_"
        + df_sst.index.get_level_values(1).astype(str)
        + "_"
        + df_sst.index.get_level_values(2).astype(str)
    )
    column_names = df_sst.columns.values.tolist()
    if len(column_names) > 5:
        df_sst = df_sst[
            [
                "ID",
                "AirTemp",
                "Humidity",
                "Sensible",
                "Latent",
                "WallTemp",
                "WallConvection",
                "WallRadiation",
            ]
        ]
    else:
        df_sst = df_sst[["ID", "AirTemp", "Humidity", "Sensible", "Latent",]]

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
                m = rx.search(
                    lines[i]
                )  # using .match searched the beginning of the line
                if m is not None:
                    m_dict = m.groupdict()
                    m_dict["Time"] = time
                    if key == "sum_time":  # sets time interval
                        time = float(m.group("Time"))
                        m_dict["Time"] = time
                    elif (
                        key == "percentage"
                    ):  # Found precentage of time temperature is above data
                        start_line = i + 2
                        end_line = start_line + 3
                        while (
                            lines[end_line] != "\n"
                        ):  # Find the lines containing the percentage of time data
                            end_line += 1
                            assert i < (len(lines) - 1), (
                                "Error with precentage of time temperature is above, line "
                                + str(i)
                            )
                        percentage = percentage_parser(lines[start_line:end_line], time)
                        for item in percentage:
                            data_percentage.append(item)
                        i = end_line
                    # TODO Update function
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
                            ), "Error with Train Energeny Summary, Line " + str(i)
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
    TES = {
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
    }
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
    path_string = "C:/Users/msn/OneDrive - Never Gray/Software Development/Next-Vis/Python2021/inferno4p2.OUT"
    list = parse_file(path_string)
    print("test finished")

