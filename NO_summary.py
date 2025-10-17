# Project Name: Next-Out
# Description: Summarize data from many files into a single Dataframe or Excel file.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

from pathlib import Path
import pandas as pd

from NO_file_tools import read_h5_file
from NO_visio import valid_simtime

def summarize_segment_data(settings, gui=""):
    """
    Process multiple NO files and extract data from multiple dataframe types.
    """
    #Get summary options from settings
    run_msg(gui, "Creating Summary file")
    segment_numbers_2_lookup = settings.get('segments_2_lookup', [])
    fire_summary = settings.get('lookup_fire_data', False)
    #Initialize lists to hold data from all files
    segment_summary_data = []
    fire_summary_data = []
    summary_dfs = []
    for no_file_path_str in settings['ses_output_str']:
        try:
            no_file_path = Path(no_file_path_str)
            data, output_meta_data = read_h5_file(no_file_path)
            requested_time = settings.get('sim_time', -1)
            segment_slices = []
            fire_slices = []
            for df_name in ["SSA","SA"]:
                if df_name in data:          
                    try:
                        valid_time = valid_simtime(requested_time, data[df_name])
                        
                        # Get the time slice first
                        time_slice = data[df_name].xs(valid_time, level='Time')
                        
                        # Find which segments actually exist in the index
                        valid_segments = time_slice.index.intersection(segment_numbers_2_lookup)
                        
                        # Only slice if we have segments available
                        if len(valid_segments) > 0:
                            df_slice = time_slice.loc[valid_segments]
                            segment_slices.append(df_slice)
                        else:
                            run_msg(gui, f"  No requested segments found in {df_name}")
                        
                        # Process fire data (same approach)
                        if df_name=='SSA' and fire_summary and 'form4_df' in output_meta_data and not output_meta_data['form4_df'].empty:
                            fire_segment = int(output_meta_data['form4_df'].index.get_level_values('Segment')[0])
                            if fire_segment in time_slice.index:
                                fire_slice = time_slice.loc[[fire_segment]]
                                fire_slices.append(fire_slice)
                    except Exception as e:
                        run_msg(gui, f"  Error processing data from {df_name}: {str(e)}")
            
            # Combine segments for this file
            if segment_slices:
                segment_df = pd.concat(segment_slices, axis=1)
                segment_summary_data.append(pd.concat([segment_df], keys=[no_file_path.stem]))
                
            # Combine fire data for this file
            if fire_slices:
                fire_df = pd.concat(fire_slices, axis=1)
                fire_summary_data.append(pd.concat([fire_df], keys=[no_file_path.stem]))

        except Exception as e:
            run_msg(gui, f"Error processing file {no_file_path_str}: {str(e)}")
    
    # Combine all segment data if we have any
    if segment_summary_data:
        df = pd.concat(segment_summary_data)
        df.name = "Segments"
        summary_dfs.append(df)
        
    # Combine all fire data if we have any
    if fire_summary_data:
        df = pd.concat(fire_summary_data)
        df.name = "Fire"
        summary_dfs.append(df)
    return summary_dfs

def valid_summary_option(settings):
    valid = False
    segment_numbers = settings.get('segments_2_lookup', "Empty")
    lookup_fire_data= settings.get('lookup_fire_data', False)
    if segment_numbers != "Empty" or lookup_fire_data:
        valid = True
    return valid

def create_excel_summary(settings, gui=""):
    """
    Create an Excel file from NO files based on settings, with each dataframe saved
    to a separate worksheet named according to its type.
    """
    # Get the summary dataframes
    if valid_summary_option(settings):
        summary_dfs = summarize_segment_data(settings, gui)
    else:
        run_msg(gui, "No summary options provided.")
        return None

    if not summary_dfs:
        return None
    # Determine output file name for summary file
    results_folder = Path(settings['ses_output_str'][0]).parent
    result_path = results_folder / "Summary.xlsx"
    # Create Excel writer object
    with pd.ExcelWriter(result_path, engine='openpyxl') as writer:
        # Write each dataframe to its own worksheet
        for df in summary_dfs:
            # Get the name for the worksheet (default to "Sheet1" if no name specified)
            sheet_name = df.name
            
            # Create flat version of this dataframe
            flat_df = (df
                      .reset_index(level=[0,1])
                      .rename(columns={
                          'level_0': 'File_Name',
                          'level_1': 'Segment'
                      }))
            
            # For fire data, rename the Segment column to Fire_Segment
            if sheet_name.lower() == "fire":
                flat_df = flat_df.rename(columns={'Segment': 'Fire_Segment'})
            
            # Save to worksheet
            flat_df.to_excel(writer, sheet_name=sheet_name, index=False)
    run_msg(gui, f"Summary saved to {result_path}")
    return result_path

def run_msg(gui, text):
    if gui != "":
        gui.gui_text(text)
    else:
        print("Run msg: " + text)

if __name__ == "__main__":
    # Example usage
    settings = {
        'ses_output_str': [
            'C:/Simulations/Test/PT09-S1GM-011-R01.out',
            'C:/Simulations/Test/PT09-S1GM-012-F-R01.out',
            'C:/Simulations/Test/PT09-S1GM-012-R01.out'
        ],
        'sim_time': -1,
        'output_filename': 'summary_results.xlsx',
        'segments_2_lookup': [2,4,6],
        'lookup_fire_data': True
    }

    output_file = create_excel_summary(settings)
    if output_file:
        print(f"\nSaved summary to: {output_file}")
    else:
        print("No data to summarize")