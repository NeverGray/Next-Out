# Project Name: Next-Out
# Description: List of version number, column names and units for SI and IP, and conversion factors.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

VERSION_NUMBER = "3B"
#Added pressure data to summary file.
#Added next-in iterations from command line
#Version C is skipped. New Version is D.
#Next-In SI inputs to IP
#Optimized for large files

#Column name : [SI Unit, IP Unit]
COLUMN_UNITS={
    "Airflow":	["m^3/s","kcfm","SSA"], #SSA Values
    "Air_Velocity":["m/s","fpm","SSA"],
    "Segment":["#","#","SSA"],
    "Sub":["#","#","SSA"],
    "Sensible":["W","Btu/s","SSA"],
    "Latent":["W","Btu/s","SSA"],
    "Air_Temp":["\u00B0C","\u00B0F","SST"], #Unicode \u00B0 are used for degree symbols
    "Humidity":["kg/kg","lb/lb","SST"],
    "Wall_Temp":["\u00B0C","\u00B0F","SST"],
    "Convection_to_Wall":["W","Btu/h","SST"],
    "Radiation_to_Wall":["W","Btu/h","SST"],
    "Working_Fluid_Temp":["\u00B0C","\u00B0F","SST"],
    "Heat_Absorbed_by_Pipe":["W","Btu/h","SST"],
    "Actual_Airflow_NO":["m^3/s","kcfm","SST"], #Next-Out calculated data
    "Section" :["#","#","SSP"],                 # SSP Values
    "Pressure_Change" : ["Pa", "IN. WG", "SSP"],
    "Train_Number":["#","#","TRA"],          #Train Information
    "Route_Number":["#","#","TRA"],
    "Train_Type_Number":["#","#","TRA"],
    "Location":["m","ft","TRA"],
    "Speed":["kph","mph","TRA"],
    "Accel":["m/s^2","mph/s","TRA"],
    "Air_Drag":["kN","lbs","TRA"],
    "Air_Drag_Coeff":["#","#","TRA"],
    "Tractive_Effort":["N/motor","lbs/motor","TRA"],
    "Motor_Current":["amps","amps","TRA"],
    "Line_Current":["amps","amps","TRA"],
    "Fly_Wheel":["rpm","rpm","TRA"],
    "Motor_Eff":["%","%","TRA"],
    "Grid_Temp_Accel":["\u00B0C","\u00B0F","TRA"],
    "Grid_Temp_Decel":["\u00B0C","\u00B0F","TRA"],
    "Heat_Gen":["W/m","Btu/s-ft","TRA"],
    "Heat_Reject":["W/m","Btu/s-ft","TRA"],
    # Train Supplementary Data
    "Mode"                        :["#",        "#",          "TRA"],
    "Auxilaries"                  :["kW/train", "kW/train",    "TRA"],
    "Propulsion_3rd_Rail"         :["kW/train", "kW/train",    "TRA"],
    "Regenerated_3rd_Rail"        :["kW/train", "kW/train",    "TRA"],
    "From_Flywheel_TRA"           :["kW/train", "kW/train",    "TRA"],
    "Accel_Grid"                  :["kW/train", "Btu/s-train","TRA"],
    "Decel_Grid"                  :["kW/train", "Btu/s-train","TRA"],
    "Mech"                        :["kW/train", "Btu/s-train","TRA"],
    "Propul_Sens"                 :["W/m",      "Btu/s-ft",   "TRA"],
    "Aux_Sens"                    :["W/m",      "Btu/s-ft",   "TRA"],
    "Aux_Latent"                  :["W/m",      "Btu/s-ft",   "TRA"],
    "Train_Length_NO"             :["m",        "ft",         "TRA"],
    "Propul_Sens_per_Train_NO"    :["kW/train", "Btu/s-train","TRA"],
    "Aux_Sens_per_Train_NO"       :["kW/train", "Btu/s-train","TRA"],
    "Aux_Latent_per_Train_NO"     :["kW/train", "Btu/s-train","TRA"],
    "Calculated_Energy_NO"     :["kW/train", "Btu/s-train","TRA"],
    # SA Values
    "Max_Airflow":["m^3/s","kcfm","SA"],
    "Max_Airflow_Time":["seconds","second","SA"],
    "Min_Airflow":["m^3/s","kcfm","SA"],
    "Min_Airflow_Time":["seconds","second","SA"],
    "Average_Positive_Airflow":["m^3/s","kcfm","SA"],
    "Average_Negative_Airflow":["m^3/s","kcfm","SA"],
    "Max_Velocity":["m/s","fpm","SA"],
    "Max_Velocity_Time":["seconds","second","SA"],
    "Min_Velocity":["m/s","fpm","SA"],
    "Min_Velocity_Time":["seconds","second","SA"],
    "Average_Velocity_Positive":["m/s","fpm","SA"],
    "Average_Velocity_Negative":["m/s","fpm","SA"],
    "Airflow_Direction_Positive":["%","%","SA"],
    "Airflow_Direction_Negative":["%","%","SA"],
    "Train_Propulsion_and_Braking_Heat":["W","Btu/h","SA"],
    "Train_Aux_and_Passenger_Sensible":["W","Btu/h","SA"],
    "Train_Aux_and_Passenger_Latent":["W","Btu/h","SA"],
    "Steady_State_Heat_Sensible":["W","Btu/h","SA"],
    "Steady_State_Heat_Latent":["W","Btu/h","SA"],
    "Unsteady_State_Heat_Sensible":["W","Btu/h","SA"],
    "Unsteady_State_Heat_Latent":["W","Btu/h","SA"],
    "Environental_Control_System_Sensible":["W","Btu/h","SA"],
    "Environental_Control_System_Latent":["W","Btu/h","SA"],
    "Cooling_Pipes_Sensible":["W","Btu/h","SA"],
    "Cooling_Pipes_Latent":["W","Btu/h","SA"],
    "Heat_Sink":["W","Btu/h","SA"],
    "Outflow_Velocity_Exceedance":["m/s","fpm","SA"],
    "Percentage_of_Velocity_Exceedance":["%","%","SA"],
    "Max_Dry_Bulb":["\u00B0C","\u00B0F","ST"],  #Start of ST values
    "Max_Dry_Bulb_Time":["seconds","second","ST"],
    "Min_Dry_Bulb":["\u00B0C","\u00B0F","ST"],
    "Min_Dry_Bulb_Time":["seconds","second","ST"],
    "Average_Positive_Dry_Bulb":["\u00B0C","\u00B0F","ST"],
    "Average_Negative_Dry_Bulb":["\u00B0C","\u00B0F","ST"],
    "Max_Humidity":["kg/kg","lb/lb","ST"],
    "Max_Humidity_Time":["seconds","second","ST"],
    "Min_Humidity":["kg/kg","lb/lb","ST"],
    "Min_Humidity_Time":["seconds","second","ST"],
    "Average_Humidity":["kg/kg","lb/lb","ST"],
    "Average_Dry_Bulb_NO":["\u00B0C","\u00B0F","ST"],
    "Percentage_Above_T1":["%","%","PER"], #Start of PER values
    "Percentage_Above_T2":["%","%","PER"],
    "Percentage_Above_T3":["%","%","PER"],
    "Percentage_Above_T4":["%","%","PER"],
    "Percentage_Above_T5":["%","%","PER"],
    "Percentage_Above_T6":["%","%","PER"],
    "T1":["\u00B0C","\u00B0F","PER"],
    "T2":["\u00B0C","\u00B0F","PER"],
    "T3":["\u00B0C","\u00B0F","PER"],
    "T4":["\u00B0C","\u00B0F","PER"],
    "T5":["\u00B0C","\u00B0F","PER"],
    "T6":["\u00B0C","\u00B0F","PER"],
    "Percentage_Above_TA_1":["%","%","PER"],
    "Percentage_Above_TA_2":["%","%","PER"],
    "Percentage_Above_TA_3":["%","%","PER"],
    "Percentage_Above_TA_4":["%","%","PER"],
    "Percentage_Above_TA_5":["%","%","PER"],
    "Percentage_Above_TA_6":["%","%","PER"],
    "Energy_Sector":["#","#","PER"],
    "From_Third_Rail":["KWh","KWh","TES"], #TES Values
    "From_Flywheel":["KWh","KWh","TES"],
    "Auxiliary_Energy":["KWh","KWh","TES"],
    "Regenerated_Energy_to_Third_Rail":["KWh","KWh","TES"],
    "ZN":["#","#","TES"],
    "Morning_Wall_Temp":["\u00B0C","\u00B0F","HSA"], #HSA Values
    "Evening_Wall_Temp":["\u00B0C","\u00B0F","HSA"],
    "Morning_Air_Temp":["\u00B0C","\u00B0F","HSA"],
    "Evening_Air_Temp":["\u00B0C","\u00B0F","HSA"],
    "Morning_Humidity":["kg/kg","lb/lb","HSA"],
    "Evening_Humidity":["kg/kg","lb/lb","HSA"],
    "Trains_and_Misc_Sensible":["W","Btu/h","ECS"], #ECS Values
    "Trains_and_Misc_Latent":["W","Btu/h","ECS"],
    "Steady_State_Sensible":["W","Btu/h","ECS"],
    "Steady_State_Latent":["W","Btu/h","ECS"],
    "Heat_Sink_Sensible":["W","Btu/h","ECS"],
    "Airflow_Sensible":["W","Btu/h","ECS"],
    "Airflow_Latent":["W","Btu/h","ECS"],
    "EC_Sensible":["W","Btu/h","ECS"],
    "EC_Latent":["W","Btu/h","ECS"],
    "EC_Requirement_Sensible":["W","Btu/h","ECS"],
    "EC_Requirement_Latent":["W","Btu/h","ECS"],
    "EC_Requirement_Total":["W","Btu/h","ECS"]
}
# IP Unit : Conversion Output to SI
IP_TO_SI={
    "Btu/h":	    0.2930711,
    "Btu/s":	    1055.056, 
    "Btu/s-train":  1.055056, # Convert Btu/s-train to kW/train
    "Btu/s-ft":	    3463.123, # Convert to watts per meter
    "fpm":	        0.00508,
    "ft":	        0.3048,
    "IN. WG":       249.08976,
    "kcfm":	        0.471947,
    "lbs":	        4.448222E-3,
    "lbs/motor":	4.448222,
    "mph":	        1.609344,
    "mph/s":	    0.447,
}
#Values to convert SI input to IP input
SI_Conversion = {
    1.0: 1.0, 
    "C_F":          1.8,
    "C_F_Increment": 1.8, # Used for max and min temps where the increment should be converted but not the value itself.
    "C_F_Not_Zero": 0, # Used for average temps columns (ST_temp_exception) where some zero values should not be converted.
    "J/kg-K_Btu/lb-F": 0.238846/1000,
    "kPa_inhg":     0.2953,
    "kg/m^3_lb/ft^3": 0.06242796,
    "kg_lbs":        2.20462,
    "kg_lbs/ton-mph/s": 0.000621371,
    "kph_mph":      0.621371,
    "m/s_fpm":      196.8504,
    "m/s^2_mph/s":  2.236936,
    "m^2/s_ft^2/hr": 38750.0775,
    "m^2_ft^2":     10.7639,
    "m^3/s_cfm":    2118.88,
    "m_ft":         3.28084,
    "mm_ft":        0.00328084,
    "mm_in":        0.0393701,
    "N-m^2_lbs-ft^2": 23.730, # Reverse calculated from normal2SI.inp (250/10.535)
    "N_lbs":        0.224809,
    "Pa_inwg":      0.00401463,
    "tonnes_tons":  1.10231,
    "W/m-K_Btu/ft-hr-F": 0.577789,
    "W_Btu/hr":     3.41214,
    "Rolling_C1": 1.3/6.374, #Reverse calculated
    "Rolling_C2": 116/515.994, #Reverse calculated from inferno.inp
    "Rolling_C3": .045/0.1371, #Reverse calculated from inferno.inp
    "Equivalent_Mass": 8.8/2626.0613, #Reverse calculated from Normal2SI.inp
    "R_air": 287.058, #Specific gas constant for air, used for calculating density from pressure and temperature"
    "Zero": 0, # Use to erase values, such as Air Density in Form 7C.
    #TODO Inferno and Normal give difference values for equivalent mass
}
Form_SI_2_IP = {
    "Form 1B": [1]*3,
    "Form 1C": [1]*8,
    "Form 1D": [1]*7,
    "Form 1E": [1]*8,
    "Form 1F": ["C_F","C_F","kPa_inhg","C_F","C_F","C_F","C_F","C_F_Increment"],
    "Form 1G": ["kg_lbs",1,1,1,1,"kph_mph",1,1],
    "Form 1H": [1]*5,    
    "Form_3A_2": ["m_ft","m^2_ft^2","m_ft",1,1],
    "Form_3B_1": ["m_ft"] * 8,
    "Form_3B_2": ["mm_ft"] * 8,
    "Form_3D": [1,1,1,"W_Btu/hr","W_Btu/hr",1,1,1],
    "Form_3E": [1,1,"C_F","C_F","C_F"],
    "Form_3F": ["m_ft","m_ft","W/m-K_Btu/ft-hr-F","m^2/s_ft^2/hr","W/m-K_Btu/ft-hr-F","m^2/s_ft^2/hr","C_F"],
    "Form_4B": ["W_Btu/hr","W_Btu/hr",1,1,"C_F","m^2_ft^2" ],
    "Form_5B": [1,1,"m^2_ft^2","m/s_fpm","C_F","C_F","C_F","m_ft"],
    "Form_5D": ["m_ft","m^2_ft^2","m_ft",1,1,1,1],
    "Form_6B": ["C_F_Not_Zero"] * 6,
    "Form_7A": [1,1,1,1,"kg/m^3_lb/ft^3",1,"m^3/s_cfm","m^3/s_cfm"],
    "Form_7B": ["Pa_inwg", "m^3/s_cfm"] *4,
    "Form_7C": ["Thrust_2_cfm",1,"m/s_fpm",1,1,"air_density","Zero"],
    #TODO Form 7C Change "Zero" to "One" when jet fan derating is added.
    "Form_8A_2": ["m_ft",1,1,1,1,"kph_mph",1],
    "Form_8C": ["m_ft", "m_ft",1,"m_ft","kph_mph",1,1,1],
    "Form_8D": ["m_ft",1,1],
    "Form_8E": [1,"kph_mph",1,1,1],
    "Form_8F_1":[1,"m_ft"],
    "Form_9A": [1,1,1,1,1,1,"m_ft","m^2_ft^2"],
    "Form_9B": ["m_ft",1,"m^2_ft^2",1,1],
    "Form_9C": ["W_Btu/hr","W_Btu/hr","W_Btu/hr","W_Btu/hr",1,1],
    "Form_9D_1": ["kg_lbs","kg_lbs","mm_in","mm_in","m^2_ft^2","m^2_ft^2","m^2_ft^2","m^2_ft^2"],
    "Form_9D_2": [1,1,"J/kg-K_Btu/lb-F","J/kg-K_Btu/lb-F","C_F","C_F","m/s_fpm","m/s_fpm"],
    "Form_9E"  :   ["tonnes_tons",1,"Rolling_C1","Rolling_C2","Rolling_C3","Equivalent_Mass"],
    "Form_9F_1" : [1,1,1,1,"mm_in","mm_in"],
    "Form_9F_2" : [1] * 5,
    "Form_9G_1" : ["kph_mph","kph_mph","kph_mph","kph_mph"],
    "Form_9G_2" : ["N_lbs"] * 4,    
    "Form_9G_3" : [1] * 4,
    "Form_9G_4" : [1],
    "Form_9H_1" : [1,1,1,1,1],
    "Form_9H_2" : [1,"kph_mph",1,1,1],
    "Form_9I" : ["kph_mph","kph_mph",1,1,1],
    "Form_9J" : ["m/s^2_mph/s","m/s^2_mph/s","kph_mph","m/s^2_mph/s","kph_mph","m/s^2_mph/s"],
    "Form_9K" : ["N-m^2_lbs-ft^2",1,1,1,1],
    "Form_10" : ["m_ft","kph_mph",1,1,"C_F","C_F",1,1],
    "Form_11A" : [1,1,"C_F","C_F","C_F","C_F"],
    "Form_12" : ["C_F_Increment",1],
    }

# Added to allow minify to work on all other modules
DEGREE_SYMBOL="\u00B0"
