# Project Name: Next-Out
# Description: Compile the Python code into an executable
# Copyright (c) 2025 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT


Set-Location "c:\bin\code"
..\python313\Scripts\Activate.ps1
Remove-Item "C:\Bin\code\*.*" -Force

Copy-Item "$PSScriptRoot\*.py" "C:\bin\code\"
Copy-Item "$PSScriptRoot\NO_Icon.ico" "C:\bin\code\"
# Exclude large unused libraries: matplotlib, scipy, PIL, test frameworks, pandas I/O modules not used
pyinstaller -F main.py --noconsole --onefile --icon NO_Icon.ico --add-data "NO_Icon.ico;." `
    --exclude matplotlib --exclude scipy --exclude PIL --exclude unittest --exclude test --exclude tests `
    --hidden-import=h5py --hidden-import=tables --hidden-import=pandas.io.pytables --collect-all tables --copy-metadata tables
Rename-Item -Path "C:\Bin\code\dist\main.exe" -NewName "Next-Out.exe"