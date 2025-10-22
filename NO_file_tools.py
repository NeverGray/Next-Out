# Project Name: Next-Out
# Description: Tools for working with files in Next Out.
# Copyright (c) 2024 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

import json
import logging
import pandas as pd
from pathlib import Path, PosixPath

# Explicitly import tables to ensure PyInstaller bundles it
try:
    import tables
except ImportError:
    tables = None

def can_write_file(file_path, gui=""):
    """
    Check if a file can be written to (not locked/open in another program).
    
    Args:
        file_path: Path object or string to the file to check
        gui: Optional GUI object for displaying messages
        
    Returns:
        True if file can be written, False otherwise
    """
    from NO_run import run_msg  # Import here to avoid circular import
    
    try:
        # Try to open file in write mode to check if it's accessible
        with open(file_path, 'a') as test_file:
            pass  # Just testing if we can access it
        return True
    except PermissionError:
        run_msg(gui, f"Error: Cannot write to {file_path}. File may be open in another program. Please close it and try again.")
        return False
    except Exception as e:
        run_msg(gui, f"Error: Cannot access {file_path}. {str(e)}")
        return False

def output_from_input(file_path_string, path_exe):
    file_path = Path(file_path_string)
    # TODO Select suffix based on SES type
    try:
        if "SES41.exe".lower() in path_exe.lower():
            extension = ".PRN"
        else:
            extension = ".OUT"
        new_file_path = file_path.with_suffix(extension)
        return new_file_path
    except:
        logging.debug("Error in 'output_from_input' when converting file strings")
        return file_path

def get_results_path2(output_meta_data, suffix):
    output_file_path = Path(output_meta_data['file_path'])
    output_stem = output_file_path.stem
    ses_version = output_meta_data.get('SES_version', '')
    if ses_version == "SI from IP":
        results_name_str = output_stem + '_SI' + suffix
    elif ses_version == "IP from SI":
        results_name_str = output_stem + '_IP' + suffix
    else:
        results_name_str = output_stem + suffix
    # Always use the same folder as the output file
    results_parent = output_file_path.parent
    results_path = results_parent/Path(results_name_str)
    return results_path

#Get variable from parsed file. Save information as HDF5 file
def save_h5_file(data, output_meta_data, settings=None):
    # Define the output file path with the HDF5 suffix
    if settings is None:
        no_file_path = output_meta_data['file_path'].with_suffix('.h5')
    else:
        no_file_path = get_results_path2(output_meta_data, '.h5')
    
    # Use PyTables for writing
    if tables is not None:
        try:
            _save_h5_with_pytables(data, output_meta_data, no_file_path)
            logging.info(f"{no_file_path} created with PyTables.")
            return
        except Exception as e:
            raise Exception(f"Failed to save H5 file to {no_file_path} with PyTables: {str(e)}") from e
    
    # PyTables not available
    raise ImportError(
        "PyTables is not available. H5 file creation requires PyTables package."
    )

def _save_h5_with_pytables(data, output_meta_data, no_file_path):
    """Save using PyTables (pd.HDFStore) - for development/script mode only"""
    try:
        complib = 'blosc'
    except:
        complib = 'zlib'
    
    with pd.HDFStore(no_file_path, mode='w', complevel=9, complib=complib) as store:
        # Save all DataFrames from data dictionary
        for key, value in data.items():
            if isinstance(value, pd.DataFrame):
                store.put(f'data/{key}', value, format='table')
            else:
                # For non-DataFrame data, store as a separate DataFrame or in metadata
                logging.warning(f"Non-DataFrame data '{key}' will be stored in metadata")
        
        # Prepare metadata for JSON serialization
        metadata = {}
        for key, value in output_meta_data.items():
            if isinstance(value, pd.DataFrame):
                # Store DataFrame in HDF5 under metadata group
                store.put(f'metadata/{key}', value, format='table')
            elif isinstance(value, (dict, list)):
                # Store complex types as JSON strings
                metadata[key] = json.dumps(value)
            elif isinstance(value, Path):
                # Convert Path to string
                metadata[key] = str(value)
            else:
                # Store simple types directly
                metadata[key] = value
        
        # Save metadata as attributes on the SSA DataFrame
        if metadata:
            store.get_storer('data/SSA').attrs.metadata = metadata

# Read the data and output_meta_data from the HDF5 file
def read_h5_file(file_path):
    # Support both legacy .no files and new .h5 files
    no_file_path_h5 = get_file_path_with_suffix(file_path, '.h5')
    no_file_path_legacy = get_file_path_with_suffix(file_path, '.no')
    
    # Try HDF5 first, fall back to legacy format
    if no_file_path_h5.exists():
        no_file_path = no_file_path_h5
        use_hdf5 = True
    elif no_file_path_legacy.exists():
        no_file_path = no_file_path_legacy
        use_hdf5 = False
        logging.warning(f"Reading legacy .no file format. Consider converting to .h5")
    else:
        raise FileNotFoundError(f"Neither {no_file_path_h5} nor {no_file_path_legacy} found")
    
    if use_hdf5:
        # Read with PyTables
        data = {}
        output_meta_data = {}
        
        if tables is not None:
            try:
                with pd.HDFStore(no_file_path, mode='r') as store:
                    # Read all data DataFrames
                    for key in store.keys():
                        if key.startswith('/data/'):
                            df_key = key.replace('/data/', '')
                            data[df_key] = store[key]
                            data[df_key].name = df_key
                        elif key.startswith('/metadata/'):
                            # Read DataFrame metadata
                            meta_key = key.replace('/metadata/', '')
                            output_meta_data[meta_key] = store[key]
                    
                    # Read metadata attributes from the SSA DataFrame if it exists
                    if 'data/SSA' in store:
                        try:
                            metadata = store.get_storer('data/SSA').attrs.metadata
                            for key, value in metadata.items():
                                if key not in output_meta_data:
                                    if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                                        try:
                                            output_meta_data[key] = json.loads(value)
                                        except json.JSONDecodeError:
                                            output_meta_data[key] = value
                                    else:
                                        output_meta_data[key] = value
                        except Exception as e:
                            logging.warning(f"Could not read metadata from 'data/SSA': {e}")
                
                if 'file_path' in output_meta_data and isinstance(output_meta_data['file_path'], str):
                    output_meta_data['file_path'] = Path(output_meta_data['file_path'])
                return data, output_meta_data
            except Exception as e:
                raise Exception(f"Failed to read H5 file with PyTables: {e}") from e
        
        # PyTables not available
        raise ImportError("PyTables is not available for reading H5 files.")
    else:
        # Legacy pickle format - keep for backward compatibility
        import gzip
        import pickle
        with gzip.open(no_file_path, 'rb') as file:
            no_file = pickle.load(file)
        data = no_file['data']
        output_meta_data = no_file['output_meta_data']
        # Add names to the DataFrames
        for key, df in data.items():
            if isinstance(df, pd.DataFrame):
                df.name = key
    
    return data, output_meta_data

def get_file_path_with_suffix(file_path, suffix='.h5'):
    # Convert any file path to use the specified suffix/extension.
    # Ensure suffix starts with a period
    if not suffix.startswith('.'):
        suffix = '.' + suffix
    
    path = Path(file_path)
    return path.with_suffix(suffix)

if __name__ == "__main__":
    import NO_parser
    directory_str = "C:\\simulations\\test\\"
    output_file_name = "test.out"
    file_path = Path(directory_str + output_file_name)
    data, output_meta_data = NO_parser.parse_file(file_path)
    save_h5_file(data, output_meta_data)