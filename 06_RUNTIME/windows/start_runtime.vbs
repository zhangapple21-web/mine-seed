' ACE Runtime - Windows Background Launcher
' Double-click to start Runtime silently in background
' Logs: 02_MEMORY/logs/runtime_YYYYMMDD.log

Option Explicit

Dim WShell, FSO, ScriptDir, Workspace, PythonExe, ChatId, Cmd

Set WShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

ScriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
Workspace = FSO.GetParentFolderName(ScriptDir)

' Try to find python.exe
PythonExe = "python"
On Error Resume Next
PythonExe = WShell.RegRead("HKLM\SOFTWARE\Python\PythonCore\3.11\InstallPath\ExecutablePath")
If Err.Number <> 0 Then
    Err.Clear
    PythonExe = WShell.RegRead("HKLM\SOFTWARE\Python\PythonCore\3.10\InstallPath\ExecutablePath")
End If
If Err.Number <> 0 Then
    Err.Clear
    PythonExe = WShell.RegRead("HKLM\SOFTWARE\Python\PythonCore\3.9\InstallPath\ExecutablePath")
End If
On Error GoTo 0

If PythonExe = "" Then PythonExe = "python"

' Read chat_id from environment or config
ChatId = WShell.ExpandEnvironmentStrings("%TG_CHAT_ID%")
If ChatId = "%TG_CHAT_ID%" Then ChatId = ""

' Build command - daemon mode, silent
Cmd = "cmd /c cd /d """ & Workspace & """ && """ & PythonExe & """ 06_RUNTIME\core\runtime_main.py --daemon"
If ChatId <> "" Then
    Cmd = Cmd & " --chat-id " & ChatId
End If
Cmd = Cmd & " >nul 2>&1"

' Start silently (hidden window, 0 = hidden)
WShell.Run Cmd, 0, False

' Show brief notification (optional, comment out for fully silent)
' WShell.Popup "ACE Runtime started in background" & vbCrLf & "Logs: 02_MEMORY/logs/", 3, "ACE Runtime", 64

Set WShell = Nothing
Set FSO = Nothing