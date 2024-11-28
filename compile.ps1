Set-Location c:\bin
.\python311\Scripts\Activate
Remove-Item "C:\Bin\code\*.py" -Force
Remove-Item "C:\Bin\code\*.ini" -Force
Copy-Item "C:\Users\msn\OneDrive - Never Gray\Software Development\Next-Vis\Python2021\*.py" "C:\bin\code\"
Copy-Item "C:\Users\msn\OneDrive - Never Gray\Software Development\Next-Vis\Python2021\Icon4.ico" "C:\bin\code\"
Remove-Item "C:\Bin\code\speed_test.py" -Force
Remove-Item "C:\Bin\code\NV_CONSTANTS.py" -Force
#Use pyminify to obscurte and compress the code to smaller files. 
pyminify code/ --in-place
#The files below cannot be 'minified' because of UTF-8 charactor for degree. Therefore, copy them back over
Copy-Item "C:\Users\msn\OneDrive - Never Gray\Software Development\Next-Vis\Python2021\NV_CONSTANTS.py" "C:\bin\code\"
Set-Location c:\bin\code
#Below is code before update from 7 to 8 of pyarmor
#pyarmor pack -e "--clean --onefile  --icon Icon4.ico --exclude matplotlib --exclude scipy --exclude unittest" main.py
#pyarmor-7 pack -e "--noconsole --onefile  --icon Icon4.ico --exclude matplotlib --exclude scipy --exclude unittest" main.py
#Below is the newer code to try packing the install
pyinstaller -F main.py --noconsole --onefile  --icon Icon4.ico --exclude matplotlib --exclude scipy --exclude unittest
# based on code on https://pyarmor.readthedocs.io/en/latest/tutorial/obfuscation.html
pyarmor gen -O obfdist --enable-jit --mix-str --assert-call --private --pack dist/main.exe main.py
Copy-Item "C:\bin\code\dist\main.exe" "C:\Simulations\_Exe"
Remove-Item -Path "C:\simulations\_exe\Next-Sim Beta11.exe"
Rename-Item -Path "C:\simulations\_exe\main.exe" -NewName "Next-Sim Beta11.exe"