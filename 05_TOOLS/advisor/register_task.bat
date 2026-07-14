@echo off
echo ===============================================
echo ACE Stock Advisor - Register Windows Task
echo ===============================================
echo.
echo Task Name: ACE_StockAdvisor_Daily
echo Time: Mon-Fri 09:20
echo User: SYSTEM
echo.

schtasks /create /tn "ACE_StockAdvisor_Daily" /tr "\"C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe\" \"c:\Users\User\ace_workspace\mine-seed\05_TOOLS\advisor\daily_runner.py\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 09:20 /f /ru SYSTEM

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: Task registered!
    echo.
    echo Verify command:
    echo   schtasks /query /tn "ACE_StockAdvisor_Daily" /fo list
) else (
    echo.
    echo FAILED: Registration failed!
    echo Error code: %errorlevel%
    echo.
    echo Ensure you run this as ADMINISTRATOR!
)

echo.
pause
