# Contributing to Next-Out

Thank you for your interest in contributing to Next-Out! This document provides guidelines and information for contributors.

I'm happy to help contributors along the way. If anything here is confusing, try your best and we'll work together.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

Be respectful, constructive, and professional in all interactions. We're here to improve tunnel ventilation analysis together.

## Getting Started

### Development Setup

1. **Fork and Clone**
   ```powershell
   git clone https://github.com/YOUR-USERNAME/Next-Out.git
   cd Next-Out
   git remote add upstream https://github.com/NeverGray/Next-Out.git
   ```

2. **Create Virtual Environment**
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Verify Setup**
   ```powershell
   python main.py  # Should launch GUI
   ```

### Understanding the Codebase

- **Read [.github/copilot-instructions.md](.github/copilot-instructions.md)** - Comprehensive coding guidelines
- **Key modules**:
  - `NO_GUI_main.py` - Main GUI window
  - `NO_run.py` - Core processing of a single file
  - `NO_GUI_multiefile_monitor` - Core processing of multiple files, with parallel processing
  - `NO_parser.py` - Regex-based SES file parsing to python dataframes and output meta-data
  - `NO_Excel_R01.py` - Excel output generation from python dataframes and output meta-data
  - `NO_visio.py` - Populate visio diagrams with SES data from python dataframes and output meta-data

## Development Workflow

### Branch Structure

- `Released-Versions` - Stable releases only (protected)
- `development` - Active development (default branch, protected)
- `feature/*` - Your feature branches

### Creating a Feature Branch

```powershell
# Start from development
git checkout development
git pull upstream development

# Create feature branch
git checkout -b feature/your-feature-name
```

### Keeping Your Branch Updated

```powershell
git checkout development
git pull upstream development
git checkout feature/your-feature-name
git merge development
```

## Coding Standards

### Critical Conventions (from copilot-instructions.md)

1. **Module Naming**: All modules prefixed with `NO_`
   ```python
   # Good
   NO_my_feature.py
   
   # Bad
   my_feature.py
   ```

2. **Status Messages**: Always use `NO_run.run_msg(gui, message)`, never `print()`
   ```python
   # Good
   NO_run.run_msg(gui, "Processing file...")
   
   # Bad
   print("Processing file...")
   ```

3. **File Paths**: Use `pathlib.Path`, not `os.path`
   ```python
   # Good
   from pathlib import Path
   file_path = Path(settings["ses_output_str"][0])
   parent_dir = file_path.parent
   
   # Bad
   import os
   parent_dir = os.path.dirname(file_path)
   ```

4. **GUI Integration**: Functions that may run from GUI or CLI should accept `gui=""` parameter
   ```python
   def my_function(settings, data, gui=""):
       NO_run.run_msg(gui, "Starting process")
       # ... processing ...
       NO_run.run_msg(gui, "Complete")
   ```

5. **Multiprocessing**: Always include `multiprocessing.freeze_support()` in `__main__` blocks
   ```python
   if __name__ == "__main__":
       multiprocessing.freeze_support()
       # ... rest of code
   ```

### Code Style

- Follow PEP 8 with 4-space indentation
- Use descriptive variable names with snake_case (`segment_data`, not `sd`). Justin hates acronyms.
- Add docstrings to public functions
- Comment complex regex patterns using `re.VERBOSE`

### Common Patterns

**DataFrame Creation**:
```python
df = pd.DataFrame(data, columns=['Time', 'Segment', 'Airflow'])
df = df.set_index(['Time', 'Segment'])
```

**Error Handling**:
```python
try:
    # operation
except Exception as e:
    NO_run.run_msg(gui, f"Error: {str(e)}")
    return None
```

**Settings Validation**:
```python
if not Path(settings['file_path']).exists():
    NO_run.run_msg(gui, "File not found")
    return False
```

## Testing

### Running Tests

```powershell
python test_output_files.py
```

### Adding Tests

When adding features that process SES files:

1. Place test files in appropriate test directory
2. Add test case to `test_output_files.py`
3. Verify both GUI and command-line modes work

### Manual Testing Checklist

- [ ] GUI launches without errors
- [ ] Feature works with .INP files
- [ ] Feature works with .OUT files
- [ ] Excel output generates correctly
- [ ] H5 caching works
- [ ] Error messages are clear and helpful

## Submitting Changes

### Pull Request Process

1. **Ensure all tests pass**
   ```powershell
   python test_output_files.py
   ```

2. **Commit with clear messages**
   ```powershell
   git add .
   git commit -m "Add feature: Brief description
   
   - Detailed change 1
   - Detailed change 2
   - Fixes #123"
   ```

3. **Push to your fork**
   ```powershell
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request**
   - Go to GitHub and create PR from your branch to `development`
   - Fill out the PR template with:
     - What changed
     - Why it changed
     - How to test it
     - Related issues

### PR Requirements

- [ ] Targets `development` branch
- [ ] Follows coding standards
- [ ] Includes tests if applicable
- [ ] Documentation updated if needed
- [ ] No merge conflicts
- [ ] Clear description of changes

### Review Process

- Maintainer will review within 1 week
- Address feedback by pushing new commits to your branch
- Once approved, maintainer will merge

## Types of Contributions

### Bug Fixes
Found a bug? Please:
1. Check if issue already exists
2. Create detailed issue with reproduction steps
3. Submit PR with fix referencing issue number

### New Features
Want to add a feature? Please:
1. Open an issue to discuss before coding
2. Ensure it fits project scope
3. Follow existing patterns (see copilot-instructions.md)

### Documentation
Improvements to docs are always welcome:
- Clarify existing documentation
- Add examples
- Fix typos
- Add code comments

### Performance Improvements
When optimizing:
1. Profile first (using cProfile)
2. Document performance gains
3. Ensure no functionality breaks

## Need Help?

- **Questions about code**: Open a [Discussion](https://github.com/NeverGray/Next-Out/discussions)
- **Bug reports**: Open an [Issue](https://github.com/NeverGray/Next-Out/issues)
- **Feature ideas**: Open an Issue with "Feature Request" tag

## Recognition

Contributors will be acknowledged in:
- GitHub contributors page
- Release notes for their contributions

Thank you for contributing to Next-Out!