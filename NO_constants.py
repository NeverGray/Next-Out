# Project Name: Next-Out
# Description: List of version number, column names and units for SI and IP, and conversion factors.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

VERSION_NUMBER = "1.0"
#Column name : [SI Unit, IP Unit]
COLUMN_UNITS={
    "Airflow":	["m^3/s","kcfm","SSA"], #SSA Values
    "Air_Velocity":["m/s","fpm","SSA"],
    "Segment":["#","#","SSA"],
    "Sub":["#","#","SSA"],
    "Sensible":["W","Btu/s","SSA"],
    "Latent":["W","Btu/s","SSA"],
    "Air_Temp":["\u00B0C","\u00B0F","SST"], #SST Values
    "Humidity":["kg/kg","lb/lb","SST"],
    "Wall_Temp":["\u00B0C","\u00B0F","SST"],
    "Convection_to_Wall":["W","Btu/h","SST"],
    "Radiation_to_Wall":["W","Btu/h","SST"],
    "Working_Fluid_Temp":["\u00B0C","\u00B0F","SST"],
    "Heat_Absorbed_by_Pipe":["W","Btu/h","SST"],
    "Actual_Airflow_NV":["m^3/s","kcfm","SST"], #Next-Out calculated data
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
    "Max_Airflow":["m^3/s","kcfm","SA"], #SA Values
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
    "Average_Dry_Bulb_NV":["\u00B0C","\u00B0F","ST"],
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
#IP Unit : Conversion to SI
IP_TO_SI={
    "Btu/h":	    0.2930711,
    "Btu/s":	    1055.056,
    "Btu/s-ft":	    3461.470,
    "fpm":	        0.00508,
    "ft":	        0.3048,
    "kcfm":	        0.471947,
    "lbs":	        4.448222E-3,
    "lbs/motor":	4.448222,
    "mph":	        1.609344,
    "mph/s":	    0.447
}
#Added to allow minify to work on all other modules
DEGREE_SYMBOL="\u00B0"