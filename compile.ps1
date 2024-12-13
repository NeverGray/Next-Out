Set-Location "c:\bin\code"
..\python313p1\Scripts\Activate.ps1
Remove-Item "C:\Bin\code\*.py" -Force
Remove-Item "C:\Bin\code\*.ini" -Force

# Prompt the user for confirmation
$response = Read-Host "Do you want to delete the Build and Dist folderss? (Yes/No)"

# Check if the response is "Yes"
if ($response -eq "Yes") {
    Remove-Tiem "C:\Bin\code\dist" -Recurse -Force
    Remove-Tiem "C:\Bin\code\build" -Recurse -Force
    Write-Host "File deleted."
}
else {
    Write-Host "Operation canceled."
}
Copy-Item "C:\Users\msn\OneDrive\Never Gray\Software Development\Next-Vis\Python2021\*.py" "C:\bin\code\"
Copy-Item "C:\Users\msn\OneDrive\Never Gray\Software Development\Next-Vis\Python2021\NO_Icon.ico" "C:\bin\code\"
pyinstaller -F main.py --noconsole --onefile  --icon NO_Icon.ico --exclude matplotlib --exclude scipy --exclude unittest

# Rename main
# Path to the Python file
$filePath = "C:\bin\code\NO_constants.py"

# Read the file content
$fileContent = Get-Content -Path $filePath

# Use a regex to find the VERSION_NUMBER line and extract the value
if ($fileContent -match 'VERSION_NUMBER\s*=\s*"(.*?)"') {
    $versionNumber = $($matches[1])  # Extract the first capture group
    $versionNumber = $versionNumber.Replace('.', 'p')
    Write-Host "Version Number: $versionNumber"
}
else {
    Write-Host "VERSION_NUMBER not found in the file."
    $versionNumber = "Test"
}
$newname = "Next-Out$versionNumber.exe"
Rename-Item -Path "C:\bin\code\dist\main.exe" -NewName "$newname.exe"