@echo off
:: Register ACE Daily Self Loop Windows Task
:: Run as Administrator

echo Registering ACE_DailySelfLoop task...

schtasks /create /tn "ACE_DailySelfLoop" /tr "\"C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe\" \"C:\Users\User\ace_workspace\mine-seed\04_PROTOCOLS\daily_self_loop.py\"" /sc daily /st 03:00 /f /ru SYSTEM

if %errorlevel% == 0 (
    echo Task registered successfully.
) else (
    echo Failed to register task. Error code: %errorlevel%
)

pause