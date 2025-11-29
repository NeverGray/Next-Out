# Next Out

Next-Out manages SES simulations and post-processes the text output.

## Features

- **Automated SES Simulation Management**: Run multiple simulations in parallel
- **Multi-Format Output**: Generate Excel spreadsheets, Visio diagrams, and summary reports
- **Data Caching**: H5 file format for faster reprocessing
- **Unit Conversion**: Conversion of output data between SI and Imperial units
- **Route Analysis**: Compare multiple simulation runs side-by-side
- **Staggered Headway Analysis**: Min, max, and average of multiple simulations

## Getting Started

### For Users

Download the latest executable from [Never Gray's website](https://www.nevergray.biz/next-out) or from the [Releases](https://github.com/NeverGray/Next-Out/releases) page.

### For Developers

#### Prerequisites

- Python 3.13 or higher
- Windows OS (required for Visio integration via COM)

#### Installation

```powershell
# Clone the repository
git clone https://github.com/NeverGray/Next-Out.git
cd Next-Out

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Running from Source

```powershell
# GUI mode
python main.py

# Command-line mode (see main.py docstring for settings format)
python main.py --settings "{...}"
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch from `development`
3. Make your changes following our [coding guidelines](.github/copilot-instructions.md)
4. Submit a pull request to `development`

## Project Structure

```
Next-Out/
├── NO_*.py           # Core modules (parser, GUI, file tools, etc.)
├── main.py           # Application entry point
├── compile.ps1       # Build script for executable
├── .github/
│   └── copilot-instructions.md  # Detailed coding guidelines
└── test_output_files.py  # Test suite
```

## Built With

* [Python](https://www.python.org/) - Core language
* [Pandas](https://pandas.pydata.org/) - Data processing
* [Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI framework
* [PyTables](https://www.pytables.org/) - HDF5 file handling
* [XlsxWriter](https://xlsxwriter.readthedocs.io/) - Excel generation

## Versioning

We use [semantic versioning](https://semver.org/). See the [tags on this repository](https://github.com/NeverGray/Next-Out/tags) for available versions.

## Authors

* **Justin Edenbaum** - *Initial work* - [NeverGray](https://github.com/NeverGray)

See also the list of [contributors](https://github.com/NeverGray/Next-Out/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details

## Acknowledgments

