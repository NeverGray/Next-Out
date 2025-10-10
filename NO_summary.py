# Project Name: Next-Out
# Description: Summarize data from many files into a single Dataframe or Excel file.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

from pathlib import Path
import pandas as pd

from NO_file_tools import read_no_file
from NO_visio import valid_simtime
from NO_run import run_msg

def summarize_segment_data(settings, gui=""):
    """
    Process multiple NO files and extract data from multiple dataframe types.
    
    Args:
        settings: Dictionary containing settings including:
            - 'ses_output_str': list of NO files to process
            - 'segment_numbers_2_lookup': list of segment numbers to extract
            - 'segment_data_2_lookup': list of dataframe types (default: ["SSA"])
            - 'sim_time': simulation time point (default: -1)
    
    Returns:
        DataFrame with multi-index (File_Name, Segment) containing data from all dataframes
    """
    segment_summary_data = []
    fire_summary_data = []
    summary_dfs = []
    summary_options = settings.get('summary_options', {}) #Get summary options from settings
    segment_numbers_2_lookup = summary_options.get('segment_numbers_2_lookup', [])
    df_names = summary_options.get('segment_data_2_lookup', ["SSA","SA"])
    fire_summary = summary_options.get('lookup_fire_data', False)
    for no_file_path_str in settings['ses_output_str']:
        try:
            no_file_path = Path(no_file_path_str)
            data, output_meta_data = read_no_file(no_file_path)
            requested_time = settings.get('sim_time', -1)
            segment_slices = []
            fire_slices = []

            for df_name in df_names:
                if df_name not in data:
                    run_msg(gui, f"  Warning: {df_name} not found in {no_file_path.name}")
                    continue              
                try:
                    valid_time = valid_simtime(requested_time, data[df_name])
                    # Process segment data
                    # TODO Fails if one segment doesn't exist. Check list in index and then elimiante items that doen't exist
                    df_slice = (data[df_name]
                              .xs(valid_time, level='Time')
                              .loc[segment_numbers_2_lookup])
                    segment_slices.append(df_slice)
                    
                    # Process fire data
                    if df_name=='SSA' and fire_summary and not output_meta_data['form4_df'].empty:
                        fire_segment = int(output_meta_data['form4_df'].index.get_level_values('Segment')[0])
                        fire_slice = (data[df_name]
                                .xs(valid_time, level='Time')
                                .loc[[fire_segment]])  # Wrap in list to keep DataFrame structure
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

def create_excel_summary(settings, gui=""):
    """
    Create an Excel file from NO files based on settings, with each dataframe saved
    to a separate worksheet named according to its type.
    
    Args:
        settings: Dictionary containing:
            - All settings required by summarize_segment_data
            - 'results_folder_str': folder to save Excel file (default: working directory)
            - 'output_filename': name of Excel file (default: "summary_results.xlsx")
    
    Returns:
        Path object to the created Excel file
    """
    # Get the summary dataframes
    summary_dfs = summarize_segment_data(settings, gui)
    
    if not summary_dfs:
        return None
        
    # Determine output path
    # TODO Select output folder from settings results_folder_str
    output_folder = Path("c:/simulations/test")
    output_filename = 'summary_results.xlsx'
    output_path = output_folder / output_filename
    
    # Create Excel writer object
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
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
    
    return output_path

if __name__ == "__main__":
    # Example usage
    summary = {
        'segment_numbers_2_lookup': [2, 4],
        'segment_data_2_lookup': ["SSA"],
        'lookup_fire_data': True,
    }
    settings = {
        'ses_output_str': [
            'C:/Simulations/Test/PT09-S1GM-011-R01.no',
            'C:/Simulations/Test/PT09-S1GM-012-F-R01.no',
            'C:/Simulations/Test/PT09-S1GM-012-R01.no'
        ],
        'sim_time': -1,
        'results_folder_str': 'C:/Simulations/Test',
        'output_filename': 'summary_results.xlsx',
        'summary_options': summary
    }

    output_file = create_excel_summary(settings)
    if output_file:
        print(f"\nSaved summary to: {output_file}")
    else:
        print("No data to summarize")