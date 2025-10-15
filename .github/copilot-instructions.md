# Next-Out AI Coding Guidelines

## Project Overview
Next-Out is a Windows desktop application for managing and post-processing SES (Subway Environment Simulation) output files. It parses complex text-based simulation outputs, converts data to Excel/Visio formats, and performs comparative analysis of tunnel ventilation simulations.

**Core Architecture**: Tkinter GUI → SES simulation orchestration → Regex-based parsing → Pandas DataFrames → Multi-format output generation (Excel, Visio, H5)

## Critical Domain Knowledge

### SES File Types & Processing Pipeline
- **Input files** (`.INP`, `.SES`): Require SES executable to run simulation first
- **Output files** (`.OUT`, `.PRN`): Direct parsing via `NO_parser.py`
- **H5 files** (`.h5`): Compressed cached format for faster re-processing

**Processing flow**: Input → Simulation (via subprocess) → Output parsing → H5 caching → Post-processing (Excel/Visio/Route/Summary)

### Parser Architecture (`NO_parser.py`)
The parser uses regex patterns in the `PIT` dictionary to extract structured data:
- **Second-by-second data** (SSA/SST): Time-series airflow, temperature, velocity by segment
- **Summary data** (SA/ST): Aggregated min/max/average statistics
- **Train data** (TRA): Position, speed, heat generation along route
- **Forms 3-9**: Metadata about fans, dampers, pressure systems, jet fans

All data is converted to multi-index Pandas DataFrames with keys like `("Time", "Segment")`.

### Units & Conversions (`NO_constants.py`)
- `COLUMN_UNITS` dict maps column names to `[SI_unit, IP_unit, data_type]`
- Data type codes: `SSA`, `SST`, `TRA`, `SA`, `ST`, `PER`, etc.
- Conversions via `NO_conversion.py` using `IP_TO_SI` factors (e.g., `"kcfm": 0.471947`)
- Suffix added to output filenames: `_SI` or `_IP` based on conversion

### Settings Management
- GUI settings saved to `NO_settings.toml` using `tomllib`/`tomli_w`
- Settings dict structure: `{'ses_output_str': [paths], 'file_type': str, 'output': [list], 'conversion': str, ...}`
- `gui_settings`: All tkinter StringVar values
- `summary_settings`: Lookup segments and fire data flags
- `directory_cache`: Last-used folder paths per file type

## Key Development Patterns

### GUI Communication Pattern
Most processing functions accept optional `gui=""` parameter:
```python
def process_function(settings, gui=""):
    NO_run.run_msg(gui, "Status message")  # Updates GUI or prints if CLI
```
Never use `print()` directly; always use `run_msg()` for status updates.

### Multi-Processing Architecture (`NO_process_multiple_files.py`)
- Uses `multiprocessing` for parallel file processing (required for PyInstaller)
- Shared state via `Manager().dict()` and `Manager().list()`
- Monitor GUI (`Monitor_GUI` class) polls process status every `UPDATE_FREQUENCY` ms
- **Always** include `multiprocessing.freeze_support()` in main blocks

### File Path Conventions
- Use `pathlib.Path` throughout, not `os.path`
- Results folder logic: `settings['results_folder_str']` if set, else same as source file
- Filename suffixes: `get_results_path2()` handles `_SI`/`_IP` naming automatically
- Output file from input: `NO_file_tools.output_from_input()` determines `.OUT` vs `.PRN`

### Visio XML Manipulation (`NO_visio.py`)
Visio files are ZIP archives containing XML. Pattern:
1. Extract with `get_visXML()` → dict of `{page_path: xml_bytes}`
2. Parse with `xml.etree.ElementTree`, namespace `ns = {"Visio": "http://..."}`
3. Update shapes by finding `Shape[@Name='NV01_...']` or `Row[@N='Fan_Segment']`
4. Write back with `write_visio()` (ZIP compression)

**Critical**: Always register namespace before modifications to preserve XML structure.

### Validation & Error Handling
- `Start_Screen.validation()` checks file extensions, folder existence, SES exe path
- File type validation: `valid_extensions` dict enforces `.INP`/`.SES`, `.OUT`/`.PRN`, or `.H5`
- For Visio: Verify template path and numeric `simtime` if `user_time` selected
- Always wrap I/O operations in try/except with `run_msg(gui, error_message)`

## Build & Distribution

### Compilation to EXE (`compile.ps1`)
```powershell
# Activates venv, copies files to c:\bin\code, runs PyInstaller
pyinstaller -F main.py --noconsole --onefile --icon NO_Icon.ico --exclude matplotlib --exclude scipy
```
- Excludes unused heavy dependencies (matplotlib, scipy, unittest)
- Must call `multiprocessing.freeze_support()` in `main.py` and `__name__ == "__main__"` blocks
- Output: `Next-Out.exe` in `c:\Bin\code\dist\`

### Dependencies (`requirements.txt`)
Core: `pandas`, `openpyxl`, `XlsxWriter`, `tables` (HDF5), `pywin32` (COM for Visio/Excel)
Build: `pyinstaller`, `pefile`

## Common Tasks

### Adding New Parser Data Type
1. Add regex pattern to `PIT` dict in `NO_parser.py`
2. Add column definitions to `COLUMN_UNITS` in `NO_constants.py`
3. Update `create_ss_dfs()` or add new parser function
4. Add conversion factors to `IP_TO_SI` if needed

### Adding GUI Option
1. Define `tk.StringVar` in `Start_Screen.screen_settings` dict
2. Create widget (checkbox/radiobutton) with `variable=self.cbo_name`
3. Add to `settings` dict in `run()` method
4. Include in `validation()` checks
5. Save/load via `NO_settings.toml` in `load_settings()`/`on_closing()`

### Extending Output Formats
Check `settings['output']` list for flags: `'Excel'`, `'Visio'`, `'Route'`, `'Summary'`, `'H5_file'`
Add processing in `NO_run.single_sim()` after parsing step.

## Testing & Debugging
- Command-line testing: `python main.py --settings "{...}"` (see `main.py` docstring)
- Enable logging: Uncomment `logging.basicConfig()` in files
- Test data location: `C:/simulations/test/` (per `NO_run.py` main block)
- Jupyter notebooks: `summary_output R0*.ipynb` for data exploration

## Project-Specific Conventions
- Prefix all module files with `NO_` (Next-Out namespace)
- Version stored in `NO_constants.VERSION_NUMBER`
- Status text widgets are always disabled except during updates
- Use `tk.StringVar(value="")` pattern for all GUI settings
- DataFrame storage: Multi-index with `(Time, Segment)` for time-series data
- Regex patterns use `re.VERBOSE` with inline comments for maintainability
