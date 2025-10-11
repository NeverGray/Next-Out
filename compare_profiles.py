import pstats
from pathlib import Path
import pandas as pd

def compare_prof_files(directory_str, top_n=10):
    """
    Compare multiple .prof files and create a summary DataFrame
    
    Args:
        directory_str (str): Directory containing .prof files
        top_n (int): Number of top functions to include in comparison
        
    Returns:
        DataFrame with function statistics across all profile files
    """
    directory = Path(directory_str)
    prof_files = list(directory.glob("*.prof"))
    
    # Dictionary to store results
    results = {}
    
    for prof_file in prof_files:
        # Load the profile
        stats = pstats.Stats(str(prof_file))
        
        # Get the function statistics
        function_stats = {}
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            # cc: cumulative calls
            # nc: number of calls
            # tt: total time
            # ct: cumulative time
            function_name = f"{func[2]}:{func[1]}"  # function:line_number
            function_stats[function_name] = {
                'calls': nc,
                'total_time': tt,
                'cumulative_time': ct,
                'time_per_call': tt/nc if nc > 0 else 0
            }
        
        # Sort by total time and get top N functions
        sorted_funcs = sorted(function_stats.items(), 
                            key=lambda x: x[1]['total_time'], 
                            reverse=True)[:top_n]
        
        results[prof_file.stem] = {
            func_name: stats['total_time'] 
            for func_name, stats in sorted_funcs
        }
    
    # Create DataFrame
    df = pd.DataFrame.from_dict(results, orient='index')
    
    return df

if __name__ == "__main__":
    # Example usage
    directory_str = "C:\\Simulations\\Test"  # Update this to your directory
    df = compare_prof_files(directory_str)
    
    # Save to Excel with formatting
    with pd.ExcelWriter('profile_comparison.xlsx', engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Profile Comparison')
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Profile Comparison']
        
        # Add some formatting
        format_float = workbook.add_format({'num_format': '0.000'})
        
        # Apply formatting to all numeric columns
        for col_num, _ in enumerate(df.columns, 1):
            worksheet.set_column(col_num, col_num, 15, format_float)
            
        worksheet.set_column(0, 0, 30)  # Make first column wider for function names
    
    print(f"Comparison saved to profile_comparison.xlsx")
    
    # Print summary to console
    print("\nSummary of profile comparisons:")
    print(df)