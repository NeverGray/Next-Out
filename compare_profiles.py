"""
Compare profiling results between original and optimized Excel creation
"""
import pstats
from pstats import SortKey

if __name__ == "__main__":
    print("=" * 80)
    print("ORIGINAL VERSION PROFILE")
    print("=" * 80)
    p_original = pstats.Stats('C:/Simulations/Test/xlsxwriter_original.prof')
    p_original.strip_dirs()
    p_original.sort_stats(SortKey.CUMULATIVE)
    print("\nTop 20 functions by cumulative time:")
    p_original.print_stats(20)

    print("\n" + "=" * 80)
    print("OPTIMIZED VERSION PROFILE")
    print("=" * 80)
    p_optimized = pstats.Stats('C:/Simulations/Test/xlsxwriter_optimized.prof')
    p_optimized.strip_dirs()
    p_optimized.sort_stats(SortKey.CUMULATIVE)
    print("\nTop 20 functions by cumulative time:")
    p_optimized.print_stats(20)

    print("\n" + "=" * 80)
    print("FUNCTIONS WITH MOST TIME SPENT (sorted by own time)")
    print("=" * 80)
    print("\nOriginal - Top 15 by own time:")
    p_original.sort_stats(SortKey.TIME)
    p_original.print_stats(15)

    print("\nOptimized - Top 15 by own time:")
    p_optimized.sort_stats(SortKey.TIME)
    p_optimized.print_stats(15)
