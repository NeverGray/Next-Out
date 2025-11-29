# Project Name: Next-Out
# Description: Summarize data from many files into a single Dataframe or Excel file.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

from pathlib import Path
import pandas as pd

import NO_constants
from NO_file_tools import read_h5_file, can_write_file

def summarize_segment_data(settings, gui=""):
    """
    Process multiple H5 files and extract data from multiple dataframe types.
    """
    from NO_visio import valid_simtime  # Import here to avoid circular import
    
    #Get summary options from settings
    run_msg(gui, "Creating Summary file")
    segment_numbers_2_lookup = settings.get('segments_2_lookup', [])
    fire_summary = settings.get('lookup_fire_data', False)
    #Initialize lists to hold data from all files
    segment_summary_data = []
    fire_summary_data = []
    sub_segment_summary_data = []
    train_summary_data = []
    summary_dfs = []
    file_info_data = []  # Store file metadata for Files_info sheet
    for no_file_path_str in settings['ses_output_str']:
        try:
            no_file_path = Path(no_file_path_str)
            data, output_meta_data = read_h5_file(no_file_path)
            
            # Collect file metadata for Files_info sheet
            file_info = {
                'File_Name': no_file_path.stem,
                'File_Time': output_meta_data.get('file_time', ''),
                'File_Path': str(output_meta_data.get('file_path', no_file_path)),
                'Conversion': output_meta_data.get('SES_version', '')
            }
            file_info_data.append(file_info)
            
            requested_time = settings.get('sim_time', -1)
            segment_slices = []
            train_slices = []
            sub_segment_slices = []
            fire_slices = []
            for df_name in ["SSA","SA","TRA"]:
                if df_name in data:          
                    try:
                        valid_time = valid_simtime(requested_time, data[df_name])
                        
                        # Get the time slice first
                        time_slice = data[df_name].xs(valid_time, level='Time')
                        
                        # Find which segments actually exist in the index
                        valid_segments = time_slice.index.intersection(segment_numbers_2_lookup)
                        
                        # Only slice if we have segments available
                        if df_name != "TRA" and len(valid_segments) > 0:
                            df_slice = time_slice.loc[valid_segments]
                            segment_slices.append(df_slice)
                        elif df_name=="TRA" and not time_slice.empty:
                            train_slices.append(time_slice)
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
            
            # Collect segments for this file
            if segment_slices:
                segment_df = pd.concat(segment_slices, axis=1)
                segment_df = pd.concat([segment_df], keys=[no_file_path.stem])
                segment_summary_data.append(segment_df)
            
            # Collect train data for this file (added last)
            if train_slices:
                train_df = pd.concat(train_slices, axis=1)
                train_df = pd.concat([train_df], keys=[no_file_path.stem])
                train_summary_data.append(train_df)

            # Collect fire data for this file
            if fire_slices:
                fire_df = pd.concat(fire_slices, axis=1)
                fire_df = pd.concat([fire_df], keys=[no_file_path.stem])
                fire_summary_data.append(fire_df)

            for df_name in ["SST","ST","HSA"]:
                if df_name in data:          
                    try:
                        valid_time = valid_simtime(requested_time, data[df_name])
                        # Get the time slice first
                        if df_name == "HSA":
                            # HSA has 3 index levels: (Time, ZN, Segment, Sub_Segment)
                            # Remove ZN level by taking xs on Time, then droplevel('ZN')
                            time_slice = data[df_name].xs(valid_time, level='Time').droplevel('ZN')
                        else:
                            time_slice = data[df_name].xs(valid_time, level='Time')
                        
                        # Find which segments actually exist in the index
                        valid_segments = time_slice.index.get_level_values(0).intersection(segment_numbers_2_lookup).tolist()
                        
                        # Only slice if we have segments available
                        if len(valid_segments) > 0:
                            df_slice = time_slice.loc[valid_segments]
                            sub_segment_slices.append(df_slice)
                        else:
                            run_msg(gui, f"No requested segments found in {df_name}")
                        
                    except Exception as e:
                        run_msg(gui, f"  Error processing data from {df_name}: {str(e)}")
            
            # Collect segments for this file
            if sub_segment_slices:
                sub_segment_df = pd.concat(sub_segment_slices, axis=1)
                sub_segment_df = pd.concat([sub_segment_df], keys=[no_file_path.stem])
                sub_segment_summary_data.append(sub_segment_df)
            
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

    # Combine all fire data if we have any
    if sub_segment_summary_data:
        df = pd.concat(sub_segment_summary_data)
        df.name = "Sub_Segments"
        summary_dfs.append(df)

    # Combine all train data if we have any
    if train_summary_data:
        df = pd.concat(train_summary_data)
        df.name = "Train"
        summary_dfs.append(df)
    
    return summary_dfs, file_info_data

def valid_summary_option(settings):
    valid = False
    segment_numbers = settings.get('segments_2_lookup', "Empty")
    lookup_fire_data= settings.get('lookup_fire_data', False)
    if segment_numbers != "Empty" or lookup_fire_data:
        valid = True
    return valid

def auto_adjust_column_widths(worksheet, df):
    """
    Auto-adjust column widths in an Excel worksheet to fit content.
    
    Args:
        worksheet: xlsxwriter worksheet object
        df: pandas DataFrame that was written to the worksheet
    """
    # Auto-size data columns
    for idx, col in enumerate(df.columns):
        # Calculate max length for column
        max_length = max(
            df[col].astype(str).apply(len).max(),
            len(str(col))
        )
        # Set column width (add padding)
        worksheet.set_column(idx, idx, max_length + 2)

def create_excel_summary(settings, gui=""):
    """
    Create an Excel file from NO files based on settings, with each dataframe saved
    to a separate worksheet named according to its type.
    """
    # Determine output file name for summary file
    results_folder = Path(settings['ses_output_str'][0]).parent
    result_path = results_folder / "Summary.xlsx"
    
    # Check if file can be written (e.g., not already open)
    if not can_write_file(result_path, gui):
        run_msg(gui, f"The file {result_path} cannot be written. Try closing the file.")
        return None
    
    # Get the summary dataframes and file info
    if valid_summary_option(settings):
        summary_dfs, file_info_data = summarize_segment_data(settings, gui)
    else:
        run_msg(gui, "No summary options provided.")
        return None

    if not summary_dfs:
        return None
    
    # Create Excel writer object with xlsxwriter engine
    with pd.ExcelWriter(result_path, engine='xlsxwriter') as writer:
        # Set workbook properties
        writer.book.set_properties({
            'title': "Summary",
            'subject': "Summary of SES Outputs",
            'author': f"Next-Out {NO_constants.VERSION_NUMBER}",
            'comments': f"Created by Next-Out {NO_constants.VERSION_NUMBER}"
        })
        
        # Create format for header row (orange background, bold)
        format_header = writer.book.add_format({
            'bold': True,
            'bg_color': '#F07F09',
        })
        
        # Write each dataframe to its own worksheet
        for df in summary_dfs:
            # Get the name for the worksheet
            sheet_name = df.name
            
            # Reset index to move multi-index to columns
            df_reset = df.reset_index()
            
            # Get the original index level names (or provide defaults if unnamed)
            level_0_name = df.index.names[0] or 'File_Name'
            level_1_name = df.index.names[1] or ('Fire_Segment' if sheet_name.lower() == "fire" else 'Segment')
            if df.name.lower() == "sub_segments":
                level_2_name = df.index.names[2] or 'Sub_Segment'
                #Rname first three columns to match the level names
                df_reset.rename(columns={df_reset.columns[0]: level_0_name, df_reset.columns[1]: level_1_name, df_reset.columns[2]: level_2_name}, inplace=True)
                # Create combined column and insert at position 3 (after File_Name, Segment, and Sub_Segment)
                combined_index = df_reset.iloc[:, 0].astype(str) + '_' + df_reset.iloc[:, 1].astype(str) + '_' + df_reset.iloc[:, 2].astype(str)
                df_reset.insert(3, f'{level_0_name}_{level_1_name}_{level_2_name}', combined_index)
            else:
                level_2_name = None
                # Rename the first two columns to match the level names
                df_reset.rename(columns={df_reset.columns[0]: level_0_name, df_reset.columns[1]: level_1_name}, inplace=True)            
                # Create combined column and insert at position 2 (after File_Name and Segment)
                combined_index = df_reset.iloc[:, 0].astype(str) + '_' + df_reset.iloc[:, 1].astype(str)
                df_reset.insert(2, f'{level_0_name}_{level_1_name}', combined_index)
            
            # Save to worksheet (index=False since we've moved everything to columns)
            df_reset.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Get worksheet object
            worksheet = writer.sheets[sheet_name]
            
            # Auto-adjust column widths for this sheet
            auto_adjust_column_widths(worksheet, df_reset)
            
            # Add AutoFilter to the header row
            max_col = len(df_reset.columns) - 1
            worksheet.autofilter(0, 0, 0, max_col)
            
            # Format header row with orange background
            for col_num, value in enumerate(df_reset.columns):
                worksheet.write(0, col_num, value, format_header)
        
        # Write Files_info sheet
        if file_info_data:
            files_info_df = pd.DataFrame(file_info_data)
            
            # Check if Conversion column exists and all values are None
            if 'Conversion' in files_info_df.columns:
                if files_info_df['Conversion'].isna().all():
                    files_info_df = files_info_df.drop(columns=['Conversion'])
            
            files_info_df.to_excel(writer, sheet_name='Files_info', index=False)
            
            # Get worksheet object
            worksheet = writer.sheets['Files_info']
            
            # Auto-adjust column widths for Files_info sheet
            auto_adjust_column_widths(worksheet, files_info_df)
            
            # Add AutoFilter to the header row
            max_col = len(files_info_df.columns) - 1
            worksheet.autofilter(0, 0, 0, max_col)
            
            # Format header row with orange background
            for col_num, value in enumerate(files_info_df.columns):
                worksheet.write(0, col_num, value, format_header)
                
    run_msg(gui, f"Summary saved to {result_path}")
    return result_path

def run_msg(gui, text):
    if gui != "":
        gui.gui_text(text)
    else:
        print("Run msg: " + text)

if __name__ == "__main__":
    # Select all files with suffix .OUT or .PRN in the directory
    directory = Path("C:/Simulations/Test/")
    ses_output_str = [str(f) for ext in ["*.H5", "*.NO"] for f in directory.glob(ext)]
    
    settings = {
        'ses_output_str': ses_output_str,   
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