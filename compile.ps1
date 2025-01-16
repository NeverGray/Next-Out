#Disable Windows Defender (or Other Antivirus Software) to properly create EXE File. 
#Disconnect Wifi or internet connection because your computer is vunerable
#Disable Real-time protection. Under Virus & Threat Protection>Virus & Threat protection settings>Manage Settings

Set-Location "c:\bin\code"
..\python313p1\Scripts\Activate.ps1
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