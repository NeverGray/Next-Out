"""
Compare H5 files between two Next-Out version directories
This script finds matching H5 files in two directories and uses NO_compare.py to compare them.
"""
import time
from pathlib import Path

import NO_compare

def get_h5_files(directory_str, extension=".h5"):
    """
    Get all H5 files in the specified directory (no subdirectories)
    
    Args:
        directory_str (str): Path to the directory to search
        extension (str): File extension to search for (e.g., ".h5" or ".no")
        
    Returns:
        dict: Dictionary with base filename (without extension) as key and full Path as value
    """
    directory = Path(directory_str)
    h5_files = {}
    
    # Get files with specified extension (case-insensitive)
    for file in directory.glob(f"*{extension}"):
        # Use stem (filename without extension) as key
        base_name = file.stem
        h5_files[base_name] = file
    
    return h5_files

def compare_h5_versions(old_dir, new_dir, old_ext=".no", new_ext=".h5"):
    """
    Compare H5 files between two Next-Out version directories
    
    Args:
        old_dir (str): Path to older version results directory
        new_dir (str): Path to newer version results directory  
        old_ext (str): Extension used in old version (default ".no")
        new_ext (str): Extension used in new version (default ".h5")
        
    Returns:
        list: List of comparison settings for each matching file pair
    """
    old_files = get_h5_files(old_dir, old_ext)
    new_files = get_h5_files(new_dir, new_ext)
    
    # Find matching files (same base name in both directories)
    matching_files = set(old_files.keys()) & set(new_files.keys())
    
    print(f"Found {len(old_files)} files in {old_dir}")
    print(f"Found {len(new_files)} files in {new_dir}")
    print(f"Found {len(matching_files)} matching files to compare")
    print()
    
    comparison_list = []
    for base_name in sorted(matching_files):
        old_file = old_files[base_name]
        new_file = new_files[base_name]
        
        settings = {
            "ses_output_str": [str(old_file), str(new_file)],
            "visio_template": None,
            "simtime": 9999.0,
            "conversion": "",
            "output": ["Compare"],
            "file_type": "H5_file",
            "path_exe": ""
        }
        comparison_list.append((base_name, settings))
    
    return comparison_list

if __name__ == "__main__":
    # Compare H5 files between Next-Out versions
    old_version_dir = "C:\\Simulations\\Next-Out 1.3.1 Results"
    new_version_dir = "C:\\Simulations\\Next-out 1.4.I Results"
    
    print("="*80)
    print("Next-Out Version Comparison Tool")
    print("="*80)
    print(f"Comparing: {old_version_dir}")
    print(f"Against:   {new_version_dir}")
    print()
    
    # Get list of comparisons to perform
    comparisons = compare_h5_versions(old_version_dir, new_version_dir, old_ext=".no", new_ext=".h5")
    
    if not comparisons:
        print("No matching files found to compare!")
    else:
        print(f"Starting comparison of {len(comparisons)} file pairs...")
        print("="*80)
        print()
        
        # Perform each comparison
        for i, (base_name, settings) in enumerate(comparisons, 1):
            print(f"[{i}/{len(comparisons)}] Comparing: {base_name}")
            start_time = time.perf_counter()
            
            try:
                NO_compare.compare_outputs(settings)
                end_time = time.perf_counter()
                print(f"    ✓ Completed in {end_time - start_time:.2f} seconds")
            except Exception as e:
                print(f"    ✗ ERROR: {str(e)}")
            
            print()
        
        print("="*80)
        print("All comparisons complete!")
        print("="*80)
