' ACE Free Zone Daemon - Windows Background Launcher
' Double-click to start 24h continuous learning silently in background
'
' 自由区副本启动器：
' - 24h 持续运行
' - 零成本（只用免费 API）
' - 输出到 02_MEMORY/free_zone/
' - 每 8 小时 TG 心跳

Option Explicit

Dim WShell, FSO, ScriptDir, Workspace, PythonExe, Cmd

Set WShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

ScriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
Workspace = FSO.GetParentFolderName(FSO.GetParentFolderName(ScriptDir))

' Find python.exe
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

' ── 免费 API Keys ──
' GLM (智谱)
Dim GLMKey
GLMKey = "c4c766faaf974bfaba30f381ccc7b066.E7VUlQfxnMXnvVRx"

' NIM (NVIDIA) - 3 keys 轮询
Dim NIMKey1, NIMKey2, NIMKey3
NIMKey1 = "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"
NIMKey2 = "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"
NIMKey3 = "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"

' GitHub Models
Dim GHKey
GHKey = "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"

' Telegram Bot (for heartbeat)
Dim TGBotToken, TGChatId
TGBotToken = "8446702999:AAHw51HYX_EwZhnzmJpQFUy734SnaZpzsCI"
TGChatId = "5016609451"

' Build command
Cmd = "cmd /c cd /d """ & Workspace & """"
Cmd = Cmd & "&& set GLM_KEY=" & GLMKey
Cmd = Cmd & "&& set NIM_KEY_1=" & NIMKey1
Cmd = Cmd & "&& set NIM_KEY_2=" & NIMKey2
Cmd = Cmd & "&& set NIM_KEY_3=" & NIMKey3
Cmd = Cmd & "&& set GH_MODELS_KEY=" & GHKey
Cmd = Cmd & "&& set TG_BOT_TOKEN_2=" & TGBotToken
Cmd = Cmd & "&& set TG_CHAT_ID=" & TGChatId
Cmd = Cmd & "&& """ & PythonExe & """ 06_RUNTIME\free_zone\daemon.py --daemon >nul 2>&1"

' Start silently (hidden window, 0 = hidden)
WShell.Run Cmd, 0, False

Set WShell = Nothing
Set FSO = Nothing