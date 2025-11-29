# Project Name: Next-Out
# Description: Progress tracking calculations for multi-file processing
# Copyright (c) 2025 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

class ProgressTracker:
    """
    Tracks progress for multi-file processing operations.
    Calculates total work units and provides progress percentage.
    """
    
    def __init__(self, num_files, process_settings):
        """
        Initialize progress tracker.
        
        Args:
            num_files (int): Number of files to process
            process_settings (dict): Dictionary of processing steps with boolean values
                Example: {'Simulation': True, 'Read Output': True, 'Visio': False, ...}
        """
        self.num_files = num_files
        self.process_settings = process_settings
        
        # Count how many processing steps are enabled
        self.steps_per_file = sum(1 for value in process_settings.values() 
                                   if isinstance(value, bool) and value)
        
        # Total work units = files × enabled steps
        self.total_work_units = num_files * self.steps_per_file
        
        # Track completed work
        self.completed_work_units = 0
    
    def get_total_work_units(self):
        """Returns the total number of work units to complete."""
        return self.total_work_units
    
    def get_completed_work_units(self):
        """Returns the number of completed work units."""
        return self.completed_work_units
    
    def increment_progress(self, amount=1):
        """
        Increment the progress by a number of work units.
        
        Args:
            amount (int): Number of work units to add (default 1)
        """
        self.completed_work_units = min(
            self.completed_work_units + amount,
            self.total_work_units
        )
    
    def get_progress_percentage(self):
        """
        Calculate current progress as a percentage.
        
        Returns:
            float: Progress percentage (0-100)
        """
        if self.total_work_units == 0:
            return 100.0
        return (self.completed_work_units / self.total_work_units) * 100.0
    
    def is_complete(self):
        """Check if all work is complete."""
        return self.completed_work_units >= self.total_work_units
    
    def get_progress_text(self):
        """
        Get a formatted progress string.
        
        Returns:
            str: Progress text like "15/45 tasks (33%)"
        """
        percentage = self.get_progress_percentage()
        return f"{self.completed_work_units}/{self.total_work_units} tasks ({percentage:.1f}%)"
    
    def reset(self):
        """Reset progress to zero."""
        self.completed_work_units = 0


def calculate_progress_from_status(processing_dictionary, process_settings,number_of_done_files):
    """
    Calculate completed work units from the current processing status dictionary.
    
    Args:
        processing_dictionary (dict): Shared dictionary with PID -> status list mapping
        process_status_value_index (dict): Index mapping for status values
            Example: {'name': 0, 'Simulation': 1, 'Read Output': 2, ...}
    
    Returns:
        int: Number of completed work units
    """
    process_status_value_index = process_settings["process_status_value_index"]
    steps_per_file = sum(1 for value in process_settings.values() 
                                   if isinstance(value, bool) and value)
    completed = number_of_done_files * steps_per_file
    
    # Define which statuses count as "done"
    done_statuses = {"Done"}
    
    for pid, status_list in processing_dictionary.items():
        # Skip the name field (index 0)
        for key, index in process_status_value_index.items():
            if key == 'name':
                continue
            
            # Check if this step is marked as "Done"
            if index < len(status_list) and status_list[index] in done_statuses:
                completed += 1
    
    return completed


def get_step_weight(step_name):
    """
    Get the relative weight/importance of a processing step.
    Some steps take longer than others.
    
    Args:
        step_name (str): Name of the processing step
    
    Returns:
        float: Weight multiplier (default 1.0)
    """
    # You can adjust these weights based on actual processing time
    weights = {
        'Simulation': 3.0,      # SES simulation takes longest
        'Read Output': 2.0,     # Parsing is moderately slow
        'Visio': 1.0,           # Visio creation is fast
        'Excel': 2.0,           # Excel is moderately slow
        'Route': 2.0,           # Route is moderately slow
    }
    return weights.get(step_name, 1.0)


class WeightedProgressTracker(ProgressTracker):
    """
    Enhanced progress tracker that weights steps by their expected duration.
    """
    
    def __init__(self, num_files, process_settings):
        """
        Initialize weighted progress tracker.
        
        Args:
            num_files (int): Number of files to process
            process_settings (dict): Dictionary of processing steps with boolean values
        """
        self.num_files = num_files
        self.process_settings = process_settings
        
        # Calculate weighted total work units
        self.total_work_units = 0.0
        self.step_weights = {}
        
        for step_name, is_enabled in process_settings.items():
            if isinstance(is_enabled, bool) and is_enabled:
                weight = get_step_weight(step_name)
                self.step_weights[step_name] = weight
                self.total_work_units += num_files * weight
        
        self.completed_work_units = 0.0
    
    def increment_progress_for_step(self, step_name, amount=1):
        """
        Increment progress by a weighted amount for a specific step.
        
        Args:
            step_name (str): Name of the processing step
            amount (int): Number of times this step was completed
        """
        weight = self.step_weights.get(step_name, 1.0)
        self.completed_work_units = min(
            self.completed_work_units + (amount * weight),
            self.total_work_units
        )


if __name__ == "__main__":
    # Test the progress tracker
    print("Testing ProgressTracker...")
    
    # Simulate processing 5 files with 3 steps each
    test_settings = {
        'Simulation': True,
        'Read Output': True,
        'Excel': True,
        'Visio': False,
        'Route': False
    }
    
    tracker = ProgressTracker(num_files=5, process_settings=test_settings)
    
    print(f"Total work units: {tracker.get_total_work_units()}")
    print(f"Steps per file: {tracker.steps_per_file}")
    print(f"Initial progress: {tracker.get_progress_text()}")
    
    # Simulate completing some work
    for i in range(15):
        tracker.increment_progress()
        if (i + 1) % 3 == 0:  # Every file completion
            print(f"After file {(i+1)//3}: {tracker.get_progress_text()}")
    
    print(f"Final: {tracker.get_progress_text()}")
    print(f"Is complete: {tracker.is_complete()}")
    
    print("\n" + "="*50)
    print("Testing calculate_progress_from_status...")
    
    # Simulate a processing dictionary
    test_processing_dict = {
        12345: ['file1.out', 'Done', 'Processing', 'Queued'],
        12346: ['file2.out', 'Done', 'Done', 'Queued'],
        12347: ['file3.out', 'Done', 'Done', 'Done']
    }
    
    test_index = {
        'name': 0,
        'Simulation': 1,
        'Read Output': 2,
        'Excel': 3
    }
    
    completed = calculate_progress_from_status(test_processing_dict, test_index)
    print(f"Completed work units: {completed}")
    print(f"Expected: 6 (3 Simulation + 2 Read Output + 1 Excel)")
    
    print("\nAll tests completed!")
