Set-Location c:\bin
python3.13\scripts\activate
pip install pandas
pip install xlsxwriter
pip install pyinstaller
pip install openpyxl
pip install pywin32
pip install tomli-w
pip install tables # For HDF5 reading/writing
pip freeze > requirements.txt