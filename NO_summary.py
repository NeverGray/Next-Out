# Project Name: Next-Out
# Description: Summarize data from many files into a single Dataframe or Excel file.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

from pathlib import Path
import pandas as pd

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
            
            # Collect segments for this file
            if segment_slices:
                segment_df = pd.concat(segment_slices, axis=1)
                segment_df = pd.concat([segment_df], keys=[no_file_path.stem])
                segment_summary_data.append(segment_df)
                
            # Collect fire data for this file
            if fire_slices:
                fire_df = pd.concat(fire_slices, axis=1)
                fire_df = pd.concat([fire_df], keys=[no_file_path.stem])
                fire_summary_data.append(fire_df)

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
    
    return summary_dfs, file_info_data

def valid_summary_option(settings):
    valid = False
    segment_numbers = settings.get('segments_2_lookup', "Empty")
    lookup_fire_data= settings.get('lookup_fire_data', False)
    if segment_numbers != "Empty" or lookup_fire_data:
        valid = True
    return valid

def auto_adjust_column_widths(worksheet, df, has_index=True):
    """
    Auto-adjust column widths in an Excel worksheet to fit content.
    
    Args:
        worksheet: openpyxl worksheet object
        df: pandas DataFrame that was written to the worksheet
        has_index: Whether the DataFrame was written with index=True
    """
    # Start column offset (1 if index is written, 0 if not)
    col_offset = 1 if has_index else 0
    
    # Auto-size index column if present
    if has_index:
        index_name = df.index.name or 'Index'
        # Convert index to list and calculate max string length
        max_length = max(
            max(len(str(val)) for val in df.index),
            len(str(index_name))
        )
        worksheet.column_dimensions['A'].width = max_length + 2
    
    # Auto-size data columns
    for idx, col in enumerate(df.columns):
        max_length = max(
            df[col].astype(str).apply(len).max(),
            len(str(col))
        )
        col_letter = worksheet.cell(1, idx + col_offset + 1).column_letter
        worksheet.column_dimensions[col_letter].width = max_length + 2

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
    
    # Create Excel writer object
    with pd.ExcelWriter(result_path, engine='openpyxl') as writer:
        
        # Write each dataframe to its own worksheet
        for df in summary_dfs:
            # Get the name for the worksheet
            sheet_name = df.name
            
            # Reset index to move multi-index to columns
            df_reset = df.reset_index()
            
            # Get the original index level names (or provide defaults if unnamed)
            level_0_name = df.index.names[0] or 'File_Name'
            level_1_name = df.index.names[1] or ('Fire_Segment' if sheet_name.lower() == "fire" else 'Segment')
            
            # Rename the first two columns to match the level names
            df_reset.rename(columns={df_reset.columns[0]: level_0_name, df_reset.columns[1]: level_1_name}, inplace=True)
            
            # Create combined column and insert at position 2 (after File_Name and Segment)
            combined_index = df_reset.iloc[:, 0].astype(str) + '_' + df_reset.iloc[:, 1].astype(str)
            df_reset.insert(2, f'{level_0_name}_{level_1_name}', combined_index)
            
            # Save to worksheet (index=False since we've moved everything to columns)
            df_reset.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Auto-adjust column widths for this sheet
            worksheet = writer.sheets[sheet_name]
            auto_adjust_column_widths(worksheet, df_reset, has_index=False)
        
        # Write Files_info sheet
        if file_info_data:
            files_info_df = pd.DataFrame(file_info_data)
            
            # Check if Conversion column exists and all values are None
            if 'Conversion' in files_info_df.columns:
                if files_info_df['Conversion'].isna().all():
                    files_info_df = files_info_df.drop(columns=['Conversion'])
            
            files_info_df.to_excel(writer, sheet_name='Files_info', index=False)
            
            # Auto-adjust column widths for Files_info sheet
            worksheet = writer.sheets['Files_info']
            auto_adjust_column_widths(worksheet, files_info_df, has_index=False)
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