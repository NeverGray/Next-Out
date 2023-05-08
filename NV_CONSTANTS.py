VERSION_NUMBER = '1.31'
#Column name : [SI Unit, IP Unit]
COLUMN_UNITS={
    "Airflow":	["m^3/s","kcfm"], #SSA Values
    "Air_Velocity":["m/s","fpm"],
    "Segment":["#","#"],
    "Sub":["#","#"],
    "Sensible":["W","Btu/s"],
    "Latent":["W","Btu/s"],
    "Air_Temp":["\u00B0C","\u00B0F"], #SST Values
    "Humidity":["kg/kg","lb/lb"],
    "Wall_Temp":["\u00B0C","\u00B0F"],
    "Convection_to_Wall":["W","Btu/h"],
    "Radiation_to_Wall":["W","Btu/h"],
    "Working_Fluid_Temp":["\u00B0C","\u00B0F"],
    "Heat_Absorbed_by_Pipe":["W","Btu/h"],
    "Actual_Airflow_NV":["m^3/s","kcfm"], #Next-vis calculated data
    "Train_Number":["#","#"],          #Train Information
    "Route_Number":["#","#"],
    "Train_Type_Number":["#","#"],
    "Location":["m","ft"],
    "Speed":["kph","mph"],
    "Accel":["m/s^2","mph/s"],
    "Air_Drag":["kN","lbs"],
    "Air_Drag_Coeff":["#","#"],
    "Tractive_Effort":["N/motor","lbs/mo"],
    "Motor_Current":["amps","amps"],
    "Line_Current":["amps","amps"],
    "Fly_Wheel":["rpm","rpm"],
    "Motor_Eff":["%","%"],
    "Grid_Temp_Accel":["\u00B0C","\u00B0F"],
    "Grid_Temp_Decel":["\u00B0C","\u00B0F"],
    "Heat_Gen":["W/m","Btu/s-ft"],
    "Heat_Reject":["W/m","Btu/s-ft"],
    "Max_Airflow":["m^3/s","kcfm"], #SA Values
    "Max_Airflow_Time":["seconds","second"],
    "Min_Airflow":["m^3/s","kcfm"],
    "Min_Airflow_Time":["seconds","second"],
    "Average_Positive_Airflow":["m^3/s","kcfm"],
    "Average_Negative_Airflow":["m^3/s","kcfm"],
    "Max_Velocity":["m/s","fpm"],
    "Max_Velocity_Time":["seconds","second"],
    "Min_Velocity":["m/s","fpm"],
    "Min_Velocity_Time":["seconds","second"],
    "Average_Velocity_Positive":["m/s","fpm"],
    "Average_Velocity_Negative":["m/s","fpm"],
    "Airflow_Direction_Positive":["%","%"],
    "Airflow_Direction_Negative":["%","%"],
    "Train_Propulsion_and_Braking_Heat":["W","Btu/h"],
    "Train_Aux_and_Passenger_Sensible":["W","Btu/h"],
    "Train_Aux_and_Passenger_Latent":["W","Btu/h"],
    "Steady_State_Heat_Sensible":["W","Btu/h"],
    "Steady_State_Heat_Latent":["W","Btu/h"],
    "Unsteady_State_Heat_Sensible":["W","Btu/h"],
    "Unsteady_State_Heat_Latent":["W","Btu/h"],
    "Environental_Control_System_Sensible":["W","Btu/h"],
    "Environental_Control_System_Latent":["W","Btu/h"],
    "Cooling_Pipes_Sensible":["W","Btu/h"],
    "Cooling_Pipes_Latent":["W","Btu/h"],
    "Heat_Sink":["W","Btu/h"],
    "Outflow_Velocity_Exceedance":["m/s","fpm"],
    "Percentage_of_Velocity_Exceedance":["%","%"],
    "Max_Dry_Bulb":["\u00B0C","\u00B0F"],  #Start of ST values
    "Max_Dry_Bulb_Time":["seconds","second"],
    "Min_Dry_Bulb":["\u00B0C","\u00B0F"],
    "Min_Dry_Bulb_Time":["seconds","second"],
    "Average_Positive_Dry_Bulb":["\u00B0C","\u00B0F"],
    "Average_Negative_Dry_Bulb":["\u00B0C","\u00B0F"],
    "Max_Humidity":["kg/kg","lb/lb"],
    "Max_Humidity_Time":["seconds","second"],
    "Min_Humidity":["kg/kg","lb/lb"],
    "Min_Humidity_Time":["seconds","second"],
    "Average_Humidity":["kg/kg","lb/lb"],
    "Average_Dry_Bulb_NV":["\u00B0C","\u00B0F"],
    "Percentage_Above_T1":["%","%"], #Start of PER values	
    "Percentage_Above_T2":["%","%"],	
    "Percentage_Above_T3":["%","%"],	
    "Percentage_Above_T4":["%","%"],	
    "Percentage_Above_T5":["%","%"],	
    "Percentage_Above_T6":["%","%"],
    "T1":["\u00B0C","\u00B0F"],
    "T2":["\u00B0C","\u00B0F"],
    "T3":["\u00B0C","\u00B0F"],
    "T4":["\u00B0C","\u00B0F"],
    "T5":["\u00B0C","\u00B0F"],
    "T6":["\u00B0C","\u00B0F"],
    "Percentage_Above_TA_1":["%","%"],
    "Percentage_Above_TA_2":["%","%"],
    "Percentage_Above_TA_3":["%","%"],
    "Percentage_Above_TA_4":["%","%"],
    "Percentage_Above_TA_5":["%","%"],
    "Percentage_Above_TA_6":["%","%"],
    "Energy_Sector":["#","#"],
    "From_Third_Rail":["KWh","KWh"], #TES Values
    "From_Flywheel":["KWh","KWh"],
    "Auxiliary_Energy":["KWh","KWh"],
    "Regenerated_Energy_to_Third_Rail":["KWh","KWh"],
    "ZN":["#","#"],
    "Morning_Wall_Temp":["\u00B0C","\u00B0F"], #HSA Values
    "Evening_Wall_Temp":["\u00B0C","\u00B0F"],
    "Morning_Air_Temp":["\u00B0C","\u00B0F"],
    "Evening_Air_Temp":["\u00B0C","\u00B0F"],
    "Morning_Humidity":["kg/kg","lb/lb"],
    "Evening_Humidity":["kg/kg","lb/lb"],
    "Trains_and_Misc_Sensible":["W","Btu/h"], #ECS Values
    "Trains_and_Misc_Latent":["W","Btu/h"],
    "Steady_State_Sensible":["W","Btu/h"],
    "Steady_State_Latent":["W","Btu/h"],
    "Heat_Sink_Sensible":["W","Btu/h"],
    "Airflow_Sensible":["W","Btu/h"],
    "Airflow_Latent":["W","Btu/h"],
    "EC_Sensible":["W","Btu/h"],
    "EC_Latent":["W","Btu/h"],
    "EC_Requirement_Sensible":["W","Btu/h"],
    "EC_Requirement_Latent":["W","Btu/h"],
    "EC_Requirement_Total":["W","Btu/h"]
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