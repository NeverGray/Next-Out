# Project Name: Next-Out
# Description: Compile the Python code into an executable
# Copyright (c) 2025 Justin Edenbaum, Never Gray
#
# This file is licensed under the MIT License.
# You may obtain a copy of the license at https://opensource.org/licenses/MIT

param(
    [string]$VenvRoot = "C:\venv",
    [string]$EnvName = "next-out-py3.13"
)

Set-Location "c:\bin\code"
$VenvPath = Join-Path $VenvRoot $EnvName
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    throw "Virtual environment python executable not found: $PythonExe"
}
Remove-Item "C:\Bin\code\*.*" -Force

# Record the exact dependency set used for this executable build.
$requirementsExePath = Join-Path $PSScriptRoot "requirements_in_exe.txt"
& $PythonExe -m pip freeze | Sort-Object | Set-Content -Path $requirementsExePath

Copy-Item "$PSScriptRoot\*.py" "C:\bin\code\"
Copy-Item "$PSScriptRoot\NO_Icon.ico" "C:\bin\code\"
# Exclude large unused libraries: matplotlib, scipy, PIL, test frameworks
# Use h5py for HDF5 support (more reliable with PyInstaller than PyTables)
& $PythonExe -m PyInstaller -F main.py --noconsole --onefile --icon NO_Icon.ico --add-data "NO_Icon.ico;." `
    #   --exclude matplotlib --exclude scipy --exclude PIL --exclude unittest --exclude test --exclude tests `
    #   --hidden-import=h5py --copy-metadata h5py
$constantsPath = Join-Path $PSScriptRoot "NO_constants.py"
$versionMatch = Select-String -Path $constantsPath -Pattern '^\s*VERSION_NUMBER\s*=\s*"([^"]+)"' | Select-Object -First 1
$version = if ($versionMatch -and $versionMatch.Matches.Count -gt 0) { $versionMatch.Matches[0].Groups[1].Value } else { "Unknown" }
$newExeName = "Next-Out $version.exe"
Rename-Item -Path "C:\Bin\code\dist\main.exe" -NewName $newExeName