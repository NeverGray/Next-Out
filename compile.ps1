Set-Location c:\bin
.\NextVis006-env\Scripts\Activate
Remove-Item "C:\Bin\code\*.py" -Force
Remove-Item "C:\Bin\code\*.ini" -Force
Copy-Item "C:\Users\msn\OneDrive - Never Gray\Software Development\Next-Vis\Python2021\*.py" "C:\bin\code\"
Remove-Item "C:\Bin\code\speed_test.py" -Force
Remove-Item "C:\Bin\code\NV_CONSTANTS.py" -Force
Copy-Item "C:\Users\msn\OneDrive - Never Gray\Software Development\Next-Vis\Python2021\Icon4.ico" "C:\bin\code\"
pyminify code/ --in-place
#The files below cannot be 'minified! Therefore, copy them back over
Copy-Item "C:\Users\msn\OneDrive - Never Gray\Software Development\Next-Vis\Python2021\NV_CONSTANTS.py" "C:\bin\code\"
Set-Location c:\bin\code
pyarmor pack -e "--onefile  --icon Icon4.ico --exclude matplotlib --exclude scipy --exclude unittest" main.py
Copy-Item "C:\bin\code\dist\main.exe" "C:\Simulations\_Exe"