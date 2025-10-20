# Project Name: Next-Out
# Description: Compile the Python code into an executable
# Copyright (c) 2025 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT


Set-Location "c:\bin\code"
..\python313\Scripts\Activate.ps1
Remove-Item "C:\Bin\code\*.*" -Force

# Prompt the user for confirmation
Copy-Item "$PSScriptRoot\*.py" "C:\bin\code\"
Copy-Item "$PSScriptRoot\NO_Icon.ico" "C:\bin\code\"
pyinstaller -F main.py --noconsole --onefile  --icon NO_Icon.ico --exclude matplotlib --exclude scipy --exclude unittest
Rename-Item -Path "C:\Bin\code\dist\main.exe" -NewName "Next-Out.exe"