from pathlib import Path

import pandas as pd

import NV_CONSTANTS
import NV_excel_R01 as NV_excel

def create_route_data(data, output_meta_data):
    # Get number of sub-segments per segement, from SST last timestep
    form8f_df = output_meta_data['form_8f']
    time = data['SST'].index.get_level_values("Time").max()
    data['SST'].loc[(time)].index #Give index on last timestep
    sst_at_time = data['SST'].loc[(time)] #get last timestep
    sub_count = sst_at_time.groupby(level=0).size() #Count of sub-segements
    # Create number of sub-segements per segement positive and negative
    sub_count_df_pos = sub_count.to_frame("Sub_Count")
    sub_count_df_neg = sub_count_df_pos.copy()
    sub_count_df_neg.index = -sub_count_df_neg.index
    sub_count = pd.concat([sub_count_df_neg,sub_count_df_pos,])
    sub_count.reindex
    # Merge number of sub-segments with route data
    routes_df = sub_count.join(form8f_df, how="outer")
    routes_df['Segement_Length'] = routes_df['Forward'] - routes_df['Backward']
    routes_df['Sub_Length'] = routes_df['Segement_Length']/routes_df['Sub_Count']
    #Create datafame with mid-points, segment, and sub-segments
    route_numbers = routes_df.index.unique(level=0).to_list()
    route_list = []
    for route_num in route_numbers:
        route_stationing = routes_df.loc[route_num]
        for index, row in route_stationing.iterrows():
            #print(index, row['Sub_Length'], row['Sub_Count'] )
            sub_length = row['Sub_Length']
            half_sub_length = 0.5 * sub_length
            sub_count = int(row['Sub_Count'])
            for i in range(1, sub_count + 1):
                if index > 0:
                    sub_number = i
                    segment = index
                else:
                    sub_number = sub_count + 1 - i
                    segment = -index
                mid_point = int(row['Backward'] + sub_length * i - half_sub_length)
                route_dict = {
                    'Route_Number': route_num,
                    'Segment': segment,
                    'Sub' : sub_number,
                    'Mid_Point': mid_point
                }
                route_list.append(route_dict)
    route_mid_points = pd.DataFrame(route_list)
    
    # Covert IP Mid_Points to SI Mid_Points if ip_to_si is selected.
    if output_meta_data['ses_version'] == 'SI from IP':
        route_mid_points['Mid_Point'] = route_mid_points['Mid_Point']*NV_CONSTANTS.IP_TO_SI['ft']
    route_mid_points['Mid_Point'] = route_mid_points['Mid_Point'].round(1)
    # Index the dataframes on route number and mid_point of route
    route_mid_points.set_index(['Route_Number','Segment','Sub'], inplace=True)
    route_num_mid_points={}
    #Create a dictionary of individual routes by numbers for each mid-points
    for route_num in route_numbers:
        route_num_mid_points[route_num] = route_mid_points.loc[route_num]
    df_key_2_route = ['SST','ST','SA','HSA'] #List of DFs to create for routes
    route_data = {} #Empty dictionary to collect data
    for key in df_key_2_route: #For every df type, perform the following
        if key in data.keys(): 
            if len(data[key]) > 0:
                #For each DF type, export data for each route
                for route_num in route_numbers: 
                    if key == 'SA': #SA is a special case
                        df = pd.merge(data[key],route_num_mid_points[route_num],left_index=True,right_index=True,how="inner")
                    else: #All other DFs can be joined as follows.
                        df = data[key].join(route_num_mid_points[route_num],on=['Segment','Sub'],how="inner")
                    format_df(route_num, df,key) #Format and sort the DF
                    route_data.update({df.name: df}) #Add it to the dictionary
    return route_data

def format_df(route_num, df,df_key):
    df.reset_index(inplace=True)
    df.set_index(['Time','Mid_Point'], inplace=True)
    df.sort_index(inplace=True)
    df_name = ''.join([df_key,"-RT", str(route_num)])
    df.name = df_name

def create_route_excel(settings, data, output_meta_data, gui=""):
    if not data['TRA'].empty: #Only perform analysis if train data is present.
        route_data = create_route_data(settings, data, output_meta_data, gui)
        #Create Excel Files
        file_path = output_meta_data['file_path']
        new_file_name = file_path.name[:-4] + "-Routes.out"
        new_file_path = file_path.parent/new_file_name
        output_meta_data['file_path'] = new_file_path
        NV_excel.create_excel(settings, route_data, output_meta_data, gui)
        #Revert back to original output_meta_data name (incase needed elsewhere)
        output_meta_data['file_path'] = file_path
    else: #Create an info message if trains are not simulated.
        msg = "INFO: Route Data is skipped because trains are not operating in the output file."
        run_msg(gui, msg)

def run_msg(gui, text):
    if gui != "":
        gui.gui_text(text)
    else:
        print("Run msg: " + text)

if __name__ == "__main__":
    import NV_parser
    directory_str = "C:\\Simulations\\2023-03-21\\SI Samples\\" #Include \\ at end of directory
    file_name = "coolpipe.out"
    ses_output_list = [directory_str + file_name]
    file_path = Path(directory_str)/ses_output_list[0]
    settings = {
        'ses_output_str': one_output_file, 
        'visio_template': 'C:/Simulations/Demonstration/Next Vis Samples1p21.vsdx', 
        'results_folder_str': 'C:/Simulations/1p30 Testing', 
        'simtime': -1, 
        'version': '', 
        'control': 'First', 
        'output': ['Excel', 'Visio', '', '', 'Route', '', '', '', ''], 
        'file_type':'', #'input_file', 
        'path_exe': 'C:/Simulations/_Exe/SVSV6_32.exe'}
    file_path = Path(settings['ses_output_str'][0])
    data, output_meta_data = NV_parser.parse_file(file_path, gui="", convert_df=settings['version'])
    create_route_excel(settings, data, output_meta_data)
    print('Finished')
