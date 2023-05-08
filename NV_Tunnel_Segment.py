import pandas as pd

from NV_CONSTANTS import IP_TO_SI as IP_TO_SI

#From https://stackoverflow.com/questions/20625582/how-to-deal-with-settingwithcopywarning-in-pandas
pd.options.mode.chained_assignment = None  # default='warn'


''' Create truth table of fire in Segments (not sub-segments)'''
def create_form4_truths(output_meta_data, simtime):
    if 'form4_df' in output_meta_data:
        form4_df = output_meta_data['form4_df']
        form4_df['active_fire']= (form4_df['source_active'] <= simtime) & (form4_df['source_inactive'] >= simtime)
        # Create smaller truth table with only True segments and sub-segments
        form4_truth_table_sub = form4_df[form4_df['active_fire']==True]['active_fire']
        # Create smaller truth table using only segments
        grouped = form4_truth_table_sub.groupby(level=0)
        form4_truth_table_segment = grouped.first()
    else:
        form4_truth_table_segment = None
    return form4_truth_table_segment
    
''' Create Truth Table of trains in segments (not sub-segments)'''
def create_train_truths(output_meta_data, data, simtime):
    #Next-In 1p13 Check if trains exist at the simtime
    if ('TRA' in data) and ('form9_df' in output_meta_data) and simtime in data['TRA'].index:
        simtime_tra = data['TRA'].loc[simtime]
        # Create default empty series
        segments_with_trains_series = pd.Series(dtype='int64')
        for index, row in simtime_tra.iterrows():
            train_number = index
            route = row['Route_Number']
            # Change train location from PIT back to IP if the file is converted from IP to SI
            if output_meta_data['ses_version'] == "SI from IP":
                train_front = row['Location']/IP_TO_SI['ft'] #Train front from PIT
            # Change train location from PIT back to SI if the file is converted from SI to IP
            elif output_meta_data['ses_version'] == "IP from SI":
                train_front = row['Location']*IP_TO_SI['ft']
            else:
                train_front = row['Location']
            train_type_number = row['Train_Type_Number']
            length = output_meta_data['form9_df'].loc[train_type_number,'train_length']
            train_back = train_front - length
            df = output_meta_data['form_8f'].loc[route]
            #Logic for presence of train is explained in "Logic for selection Rev1.pdf"
            criteria_train_front = (df['Forward'] >= train_front) & (train_front >= df['Backward'])
            criteria_train_middle = (train_front >= df['Forward']) & (train_back <= df['Backward'])
            criteria_train_back = (df['Forward'] >= train_back) & (train_back >= df['Backward'])
            new_segments_series = df[criteria_train_front | criteria_train_middle | criteria_train_back].index.to_series().abs()
            if new_segments_series is not None:
                # segments_with_trains_series= segments_with_trains_series.append(new_segments_series,ignore_index=True)
                segments_with_trains_series = pd.concat([segments_with_trains_series,new_segments_series])
        segments_with_trains = segments_with_trains_series.unique().tolist()
        if len(segments_with_trains) > 0:
            #train_false_table_segment = pd.Series(index = segments_with_trains, dtype = bool, name="train_present").fillna(value=True)
            #train_truth_table_segment = ~train_false_table_segment
            train_truth_table_segment = pd.Series(index = segments_with_trains, dtype = bool, name="train_present").fillna(value=True)
        else:
            train_truth_table_segment = None
    else:
        train_truth_table_segment = None
    return train_truth_table_segment

def create_segment_info(data, output_meta_data, simtime):
    form4_truth_table_segment = create_form4_truths(output_meta_data, simtime)
    train_truth_table_segment = create_train_truths(output_meta_data, data, simtime)
    segment_time_df = data['SSA'].loc[(simtime)]
    if form4_truth_table_segment is not None:
        segment_time_df = segment_time_df.join(form4_truth_table_segment, how='left')
    else:
        segment_time_df["active_fire"] = False
    if train_truth_table_segment is not None:
        segment_time_df = segment_time_df.join(train_truth_table_segment, how="left")
    else:
        segment_time_df["train_present"] = False
    fillin_values = {"active_fire":False, "train_present":False}
    segment_time_df.fillna(value=fillin_values, inplace=True)
    return segment_time_df

if __name__ == "__main__":
    from pathlib import Path

    import NV_parser
    import NV_visio     
    visio_template = "Next Vis Samples1p21.vsdx"
    file_path_string = "C:/simulations/NV_Tunnel_Fix/siinfern-detailed.out"
    visio_template_folder = "C:/simulations/NV_Tunnel_Fix"
    results_folder_str = visio_template_folder
    settings = {
        "ses_output_str": [file_path_string],
        "visio_template": "/".join([visio_template_folder, visio_template]),
        "results_folder_str": results_folder_str,
        "simtime": 500.0,
        "conversion": "",
        "control": "First",
        "output": ["Visio"],
    }
    file_path = Path(settings['ses_output_str'][0])
    conversion_setting = settings['conversion']
    data, output_meta_data = NV_parser.parse_file(file_path, gui="",conversion_setting=conversion_setting)
    simtime = NV_visio.valid_simtime(settings["simtime"], data["SSA"], gui="")
    segment_time_df = create_segment_info(data, output_meta_data, simtime)
    print('Finished')
