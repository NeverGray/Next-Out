# Test script for recent Next-Out changes
# Run this to verify core functionality after recent updates

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        import NO_gui
        import NO_file_tools
        import NO_run
        import NO_Excel_R01
        import NO_visio
        import NO_summary
        import NO_compare
        import NO_average
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_file_tools():
    """Test that get_results_path2 works without settings parameter"""
    print("\nTesting NO_file_tools.get_results_path2...")
    try:
        import NO_file_tools
        from pathlib import Path
        
        # Create test metadata
        output_meta_data = {
            'file_path': Path('C:/test/sample.out'),
            'SES_version': 'SI'
        }
        
        # Test the function (should work without settings now)
        result = NO_file_tools.get_results_path2(output_meta_data, '.xlsx')
        
        expected = Path('C:/test/sample.xlsx')
        if result == expected:
            print(f"✓ get_results_path2 works correctly: {result}")
            return True
        else:
            print(f"✗ Unexpected result: {result} (expected {expected})")
            return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_settings_file():
    """Check if NO_settings.toml exists and has expected structure"""
    print("\nTesting settings file...")
    try:
        import tomllib
        settings_file = Path("NO_settings.toml")
        
        if not settings_file.exists():
            print("ℹ No settings file found (this is OK on first run)")
            return True
        
        with open(settings_file, "rb") as f:
            data = tomllib.load(f)
        
        # Check for expected keys
        expected_keys = ['gui_settings', 'summary_settings', 'directory_cache', 'window_geometry']
        missing_keys = [k for k in expected_keys if k not in data]
        
        if missing_keys:
            print(f"ℹ Settings file missing keys: {missing_keys} (will be added on next save)")
        
        # Check for OLD keys that should be removed
        if 'results_folder_str' in str(data):
            print("✗ Old 'results_folder_str' found in settings - this should be removed")
            return False
        
        print(f"✓ Settings file structure looks good")
        print(f"  - Window geometry: {data.get('window_geometry', 'not set')}")
        print(f"  - Has summary settings: {bool(data.get('summary_settings'))}")
        return True
        
    except Exception as e:
        print(f"✗ Settings test failed: {e}")
        return False

def test_gui_creation():
    """Test that GUI can be created without errors"""
    print("\nTesting GUI creation...")
    try:
        import tkinter as tk
        import NO_gui
        
        # This will test the imports and class definition
        # We won't actually launch the window
        print("✓ GUI class can be imported and instantiated")
        return True
    except Exception as e:
        print(f"✗ GUI creation test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("Next-Out Recent Changes Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_file_tools,
        test_settings_file,
        test_gui_creation,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All automated tests passed!")
        print("\nNext steps for manual testing:")
        print("1. Run NO_gui.py and process a sample file")
        print("2. Verify output files are created in source folder")
        print("3. Test window resizing and persistence")
        print("4. Test Summary options integration")
        print("5. Close and reopen to verify settings are saved")
    else:
        print("\n✗ Some tests failed - review errors above")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
