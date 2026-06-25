# Project Name: Next-Out
# Description: Create Dataframes with train supplementary data.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

import NO_parser
import pandas as pd
import re

train_sup = re.compile(
        r"""(
        \s*(?P<Train_Number>\d+)\s+           #Number
        (?P<Route_Number>\d+)\s?               #RTE
        (?P<Train_Type_Number>\d+)\s+          #Train_Type_Number
        (?P<Mode>\d+)\s+                       #Mode
        (?P<Auxilaries>\d+\.)\s+               #Auxilaires
        (?P<Propulsion_3rd_Rail>\d+\.)\s+      #Propulsion_3rd_Rail
        (?P<Regenerated_3rd_Rail>\d+\.)\s+     #Regenerated_3rd_Rail
        (?P<From_Flywheel_TRA>\d+\.)\s+        #Heat Generation from flywheel in train data
        (?P<Accel_Grid>\d+\.\d+)\s+            #Accel Grid
        (?P<Decel_Grid>\d+\.\d+)\s+            #Decel Grid
        (?P<Mech>\d+\.\d+)\s+                  #Mec
        (?P<Propul_Sens>\d+\.\d+)\s+           #Propul_Sens
        (?P<Aux_Sens>\d+\.\d+)\s+              #Aux Sens
        (?P<Aux_Latent>\d+\.\d+)\n            #Aux Latent
        )""",
        re.VERBOSE,
    )

def add_train_sup(df_train, data_train_sup, output_meta_data):
    df_train_sup = NO_parser.to_dataframe2(
        data_train_sup, ["Train_Number", "Route_Number", "Train_Type_Number"],
        ["Time", "Train_Number"]
    )
    df_train_sup = df_train_sup.drop(columns=["Route_Number", "Train_Type_Number"])  # Duplicate columns already in df_train
    # If IP version, convert watts per train to Kilowatts per train
    if output_meta_data["ses_version"] == "IP":
        w_to_kw = ["Auxilaries", "Propulsion_3rd_Rail", "Regenerated_3rd_Rail", "From_Flywheel_TRA"]
        for col in w_to_kw:
            df_train_sup[col] = df_train_sup[col] / 1000.0

    # Merge the supplementary train data with the main train dataframe first
    df_train = df_train.join(df_train_sup, how="outer")

    # Add a column with the train length, named "Train_length_NO"
    form9_df = output_meta_data["form9_df"]
    
    # Ensure form9_df index is Train_Type_Number
    if form9_df.index.name != "train_type":
        form9_df = form9_df.set_index("train_type")
    df_train = df_train.join(form9_df[["train_length"]], on="Train_Type_Number")
    df_train = df_train.rename(columns={"train_length": "Train_Length_NO"})

    # Columns to multiply
    columns_to_multiply = ["Propul_Sens", "Aux_Sens", "Aux_Latent"]

    # Create new columns with the "_per_train_NO" suffix
    for column in columns_to_multiply:
        new_column = f"{column}_per_Train_NO"
        df_train[new_column] = df_train[column] * df_train["Train_Length_NO"]

    new_column = "Calculated_Energy_NO"
    df_train[new_column] = (
        df_train["Propul_Sens_per_Train_NO"]
        - df_train["Accel_Grid"]
        - df_train["Mech"]
    )

    return df_train

if __name__ == "__main__":
    from NO_parser import parse_file
    from NO_Excel_R01 import create_excel
    from pathlib import Path

    file_path_string = "C:\\simulations\\test\\test.PRN"
    settings = {
        "ses_output_str": [file_path_string],
        "output_conversion": "IP_TO_SI",
        "output": ["Excel"]
    }
    conversion_setting = settings["output_conversion"]
    file_path = Path(settings["ses_output_str"][0])
    d, output_meta_data = NO_parser.parse_file(file_path, gui="", conversion_setting=conversion_setting)
    create_excel(settings, d, output_meta_data)
