<<<<<<< HEAD
VERSION_NUMBER = '1.2'
=======
VERSION_NUMBER = '1.14'
>>>>>>> parent of 8646856 (1.15 Gets machine fingerprint to clipboard)

#Column name : [SI Unit, IP Unit]
COLUMN_UNITS={
    "Airflow":	["m^3/s","kcfm"],
    "Air_Velocity":["m/s","fpm"],
    "Segment":["#","#"],
    "Sub":["#","#"],
    "Sensible":["W","Btu/s"],
    "Latent":["W","Btu/s"],
    "Air_Temp":["°C","°F"],
    "Humidity":["kg/kg","lb/lb"],
    "Wall_Temp":["°C","°F"],
    "Convection_to_Wall":["W","Btu/h"],
    "Radiation_to_Wall":["W","Btu/h"],
    "Working_Fluid_Temp":["°C",""],
    "Heat_Absorbed_by_Pipe":["W",""],
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
    "Grid_Temp_Accel":["°C","°F"],
    "Grid_Temp_Decel":["°C","°F"],
    "Heat_Gen":["W/m","Btu/s-ft"],
    "Heat_Reject":["W/m","Btu/s-ft"],
    "Max_Airflow":["m^3/s","kcfm"],
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
    "Train_Propulsion__and_Braking_Heat":["W","Btu/h"],
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
    "Max_Dry_Bulb":["°C","°F"],
    "Max_Dry_Bulb_Time":["seconds","second"],
    "Min_Dry_Bulb":["°C","°F"],
    "Min_Dry_Bulb_Time":["seconds","second"],
    "Average_Positive_Dry_Bulb":["°C","°F"],
    "Average_Negative_Dry_Bulb":["°C","°F"],
    "Max_Humidity":["kg/kg","lb/lb"],
    "Max_Humidity_Time":["seconds","second"],
    "Min_Humidity":["kg/kg","lb/lb"],
    "Min_Humidity_Time":["seconds","second"],
    "Average_Humidity":["kg/kg","lb/lb"],
    "Percentage_Above_T1":["%","%"],	
    "Percentage_Above_T2":["%","%"],	
    "Percentage_Above_T3":["%","%"],	
    "Percentage_Above_T4":["%","%"],	
    "Percentage_Above_T5":["%","%"],	
    "Percentage_Above_T6":["%","%"],
    "T1":["°C","°F"],
    "T2":["°C","°F"],
    "T3":["°C","°F"],
    "T4":["°C","°F"],
    "T5":["°C","°F"],
    "T6":["°C","°F"],
    "Percentage_Above_TA_1":["%","%"],
    "Percentage_Above_TA_2":["%","%"],
    "Percentage_Above_TA_3":["%","%"],
    "Percentage_Above_TA_4":["%","%"],
    "Percentage_Above_TA_5":["%","%"],
    "Percentage_Above_TA_6":["%","%"],
    "Energy_Sector":["#","#"],
    "From_Third_Rail":["KWh","KWh"],
    "From_Flywheel":["KWh","KWh"],
    "Auxiliary_Energy":["KWh","KWh"],
    "Regenerated_Energy_to_Third_Rail":["KWh","KWh"],
    "Morning_Wall_Temp":["°C","°F"],
    "Evening_Wall_Temp":["°C","°F"],
    "Morning_Air_Temp":["°C","°F"],
    "Evening_Air_Temp":["°C","°F"],
    "Morning_Humidity":["kg/kg","lb/lb"],
    "Evening_Humidity":["kg/kg","lb/lb"],
    "Trains_and_Misc_Sensible":["W","Btu/h"],
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
