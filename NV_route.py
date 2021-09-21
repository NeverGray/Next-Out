from pathlib import Path

import pandas as pd

import NV_excel


def create_route_data(settings, data, output_meta_data, gui=""):
    # Get number of sub-segments per segement, from SST last timestep
    form8f_df = output_meta_data['form_8f']
    time = data['SST'].index.get_level_values("Time").max()
    data['SST'].loc[(time)].index #Give index on last timestep
    sst_at_time = data['SST'].loc[(time)] #get last timestep
    sub_count = sst_at_time.groupby(level=0).size() #Count of sub-segements
    # Create number of sub-segements per segement positive and nefative
    sub_count_df_pos = sub_count.to_frame("Sub_Count")
    sub_count_df_neg = sub_count_df_pos.copy()
    sub_count_df_neg.index = -sub_count_df_neg.index
    sub_count = pd.concat([sub_count_df_neg,sub_count_df_pos,])
    sub_count.reindex
    # Merge number of sub-segments with route data
    routes_df = sub_count.join(form8f_df, how="outer")
    routes_df['Segement_Length'] = routes_df['End'] - routes_df['Start']
    routes_df['Sub_Length'] = routes_df['Segement_Length']/routes_df['Sub_Count']
    #Create datafame with mid-points
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
                mid_point = int(row['Start'] + sub_length * i - half_sub_length)
                route_dict = {
                    'Route_Number': route_num,
                    'Segment': segment,
                    'Sub' : sub_number,
                    'Mid_Point': mid_point
                }
                route_list.append(route_dict)
    route_mid_points = pd.DataFrame(route_list)
    route_mid_points.set_index(['Route_Number','Mid_Point'], inplace=True)
    # Merge with Second-by-Second data
    route_data = {}
    dfs = route_mid_points.join(sst_at_time,on=['Segment','Sub'])
    for route_num in route_numbers:
        df_name = ''.join(["SST-RT", str(route_num)])
        df = dfs.loc[route_num]
        df.name = df_name
        route_data.update({df.name: df})
    if 'ST' in data.keys():
        last_time = data['ST'].index.get_level_values("Time").max()
        dfs = route_mid_points.join(data['ST'].loc[last_time], on=['Segment','Sub'])
        for route_num in route_numbers:
            df_name = ''.join(["ST-RT", str(route_num)])
            df = dfs.loc[route_num]
            df.name = df_name
            route_data.update({df.name: df})
    if 'HSA' in data.keys():
        last_time = data['HSA'].index.get_level_values("Time").max()
        dfs = route_mid_points.join(data['HSA'].loc[last_time].reset_index(level=0), on=['Segment','Sub'])
        for route_num in route_numbers:
            df_name = ''.join(["HSA-RT", str(route_num)])
            df = dfs.loc[route_num]
            df.name = df_name
            route_data.update({df.name: df})
    return route_data

def create_route_excel(settings, data, output_meta_data, gui=""):
    route_data = create_route_data(settings, data, output_meta_data, gui)
    #Create Excel Files
    file_path = output_meta_data['file_path']
    new_file_name = file_path.name[:-4] + "-Routes.out"
    new_file_path = file_path.parent/new_file_name
    output_meta_data['file_path'] = new_file_path
    NV_excel.create_excel(settings, route_data, output_meta_data, gui="")
    #Revert back to original output_meta_data name (incase needed elsewhere)
    output_meta_data['file_path'] = file_path

if __name__ == "__main__":
    import NV_parser
    directory_str = "C:\\Users\\msn\\OneDrive - Never Gray\\Software Development\\Next-Vis\\Projects and Issues\\2021-09-14 Tunnel Stencil\\Parsing\\"
    file_name = "Form4.prn"
    ses_output_list = [directory_str + file_name]
    file_path = Path(directory_str)/ses_output_list[0]
    settings = {
        "ses_output_str": ses_output_list,
        "results_folder_str": None,
        "visio_template": None,
        "simtime": 990.0,
        "version": "tbd",
        "control": "First",
        "output": ["Excel","Route"],
    }
    data, output_meta_data = NV_parser.parse_file(file_path)
    create_route_excel(settings, data, output_meta_data)
    print('finished')
    

