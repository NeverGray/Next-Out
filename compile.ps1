# Project Name: Next-Out
# Description: Compile the Python code into an executable
# Copyright (c) 2025 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT


Set-Location "c:\bin\code"
..\python3p13\Scripts\Activate.ps1
Remove-Item "C:\Bin\code\*.*" -Force

# Prompt the user for confirmation
$response = Read-Host "Do you want to delete the Build and Dist folders? (Yes/No)"

# Check if the response is "Yes"
if ($response -eq "Yes" -or $response -eq "") {
    Remove-Item "C:\Bin\code\dist" -Recurse -Force
    Remove-Item "C:\Bin\code\build" -Recurse -Force
    Write-Host "File deleted."
}
else {
    Write-Host "Build and Dist Folders kept."
}
Copy-Item "C:\Users\msn\OneDrive\Never Gray\Software Development\Next-Vis\Python2021\*.py" "C:\bin\code\"
Copy-Item "C:\Users\msn\OneDrive\Never Gray\Software Development\Next-Vis\Python2021\NO_Icon.ico" "C:\bin\code\"
pyinstaller -F main.py --noconsole --onefile  --icon NO_Icon.ico --exclude matplotlib --exclude scipy --exclude unittest