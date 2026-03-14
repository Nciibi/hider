# Option D: C2 Framework, Plugin System, Payload Staging & Memory Injection

## Background
Hider currently generates evasion payloads, stagers, and steganographic carriers — but has no way to **receive callbacks**, **control implants**, or **dynamically extend itself**. Option D bridges that gap by turning Hider from a payload generator into a full operator framework.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│                   OPERATOR (Attacker)                 │
│                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐ │
│  │  hider CLI   │  │  Flask GUI  │  │  C2 Listener │ │
│  │  (hider.py)  │  │  (app.py)   │  │  (c2_server) │ │
│  └──────┬───────┘  └──────┬──────┘  └──────┬───────┘ │
│         │                 │                │          │
│         └────────┬────────┘                │          │
│                  │                         │          │
│          ┌───────▼────────┐       ┌────────▼───────┐ │
│          │  Plugin Loader │       │ Session Manager │ │
│          │  (modules/)    │       │  (sessions DB)  │ │
│          └───────┬────────┘       └────────┬───────┘ │
│                  │                         │          │
│          ┌───────▼─────────────────────────▼───────┐ │
│          │          Staging Engine                   │ │
│          │  (poly + front + loader + patch)          │ │
│          └──────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
                         │ HTTP/HTTPS/DNS
                         ▼
              ┌──────────────────┐
              │  IMPLANT (Beacon)│
              │  beacon.py /     │
              │  beacon.ps1      │
              └──────────────────┘
```

---

## 1️⃣ C2 Framework (Beaconing + Command Control)

### What
A lightweight HTTP(S)-based C2 server that receives check-ins ("beacons") from implants, queues operator commands, and collects results.

### New Files

#### [NEW] `c2/server.py` — C2 Listener
- Flask-based HTTPS listener on a configurable port (default `:8443`).
- Routes:
  - `GET /beacon` — Implant check-in. Returns queued command (or `NOP`).
  - `POST /result` — Implant posts command output.
  - `GET /stage/<id>` — Serves staged payloads on-demand.
- Session tracking: each implant gets a UUID on first check-in (stored in `sessions.json`).
- Jitter-aware: expects beacons within `sleep ± jitter` intervals.

#### [NEW] `c2/session.py` — Session Manager
- Tracks active sessions: `{uuid, hostname, os, user, ip, last_seen, status}`.
- Methods: `register()`, `heartbeat()`, `queue_command()`, `get_pending()`, `store_result()`.
- Persistence: SQLite file `c2/hider_c2.db`.

#### [NEW] `c2/beacon_gen.py` — Implant Generator
- Generates a Python or PowerShell beacon script customized for the operator's listener.
- Configurable: callback URL, sleep interval, jitter %, kill date, user-agent.
- The beacon:
  1. Sleeps for `interval ± jitter`.
  2. Sends `GET /beacon?id=<uuid>` with system info headers.
  3. If command received → executes via `subprocess` / `IEX` → `POST /result`.
- Output wrapped through [poly_engine.py](file:///home/tyrel/hider/poly_engine.py) for uniqueness.

#### [NEW] `c2/console.py` — Operator Console (interactive CLI)
- `interact <session_id>` — Select an active session.
- `shell <cmd>` — Queue a shell command.
- `upload <local> <remote>` — Stage a file for download.
- `download <remote>` — Request file exfil from implant.
- `sessions` — List all active/dead sessions.
- `kill <session_id>` — Send self-destruct to implant.

---

## 2️⃣ Module / Plugin System

### What
A hot-loadable module system allowing operators to drop Python files into a `modules/` directory and have them auto-register as available post-exploitation commands.

### New Files

#### [NEW] `modules/__init__.py` — Plugin Loader
- On startup, scans `modules/` for [.py](file:///home/tyrel/hider/app.py) files.
- Each module must define:
  ```python
  MODULE_INFO = {"name": "...", "description": "...", "author": "...", "platform": "windows|linux|all"}
  def run(session, args): ...  # Returns string output
  ```
- Loader validates structure, registers into a global `MODULES` dict.
- Accessible via `use <module_name>` in the C2 console and via `POST /api/module` in the GUI.

#### [NEW] `modules/whoami.py` — Example Module
- Runs `whoami /all` (Windows) or [id](file:///home/tyrel/hider/video_handler.py#51-55) (Linux) on the target.

#### [NEW] `modules/screenshot.py` — Example Module
- Generates a PowerShell/Python one-liner to capture a screenshot and base64-encode it back.

#### [NEW] `modules/persist_registry.py` — Example Module
- Adds a `HKCU\...\Run` registry key for persistence (Windows).

#### [NEW] `modules/persist_cron.py` — Example Module  
- Adds a crontab entry for persistence (Linux).

---

## 3️⃣ Payload Staging

### What
A centralized staging engine that combines Hider's existing generators (poly, front, loader, patch) into automated "recipes" for one-click payload delivery.

### New Files

#### [NEW] `c2/stager.py` — Staging Engine
- Recipes combine multiple engines:
  - **`windows_full`**: `patch_engine(amsi+etw)` + `poly_engine(beacon, layers=2)` + `loader_engine(shellcode_stager)` → single `.ps1`
  - **`lnk_dropper`**: `lolbin_engine(certutil)` + `lnk_handler` → `.lnk` that stages the beacon
  - **`office_macro`**: `macro_engine(beacon_url)` + `evasion_engine(sandbox)` → [.vba](file:///home/tyrel/hider/test_macro.vba) ready to embed
  - **`linux_memfd`**: `loader_engine(bash_memfd)` wrapped with `front_engine` headers
- Each recipe outputs a ready-to-deploy file served via `GET /stage/<id>`.

#### [MODIFY] `c2/server.py`
- Add `/stage/<recipe_id>` route to serve generated stager files.

---

## 4️⃣ Memory Injection Modules

### What
Pre-built PowerShell and Python templates for in-memory code execution on compromised targets. These are _templates generated by Hider_ — not compiled binaries.

### New Files

#### [NEW] `modules/inject_shellcode.py`
- Generates a PowerShell script using `VirtualAlloc` + `CreateThread` (extends `loader_engine`).
- Delivered as a C2 module: operator provides shellcode URL → module generates + queues the injection command.

#### [NEW] `modules/inject_dotnet.py`
- Generates `[Reflection.Assembly]::Load()` stager for in-memory .NET assembly execution.
- Operator provides assembly URL → module wraps in AMSI patch + poly layer.

#### [NEW] `modules/inject_python.py`
- For Linux targets: generates `ctypes` + `mmap` based shellcode loader.
- Uses `ctypes.CDLL(None).memfd_create()` for anonymous execution.

#### [NEW] `modules/hollow.py`
- Generates a PowerShell template for basic process hollowing:
  - Spawns `svchost.exe` in suspended state.
  - Overwrites image base with shellcode.
  - Resumes thread.
- Template only — actual execution requires target-side PowerShell with Win32 API access.

---

## Implementation Priority

| Phase | Component | Depends On | Effort |
|---|---|---|---|
| **Phase 1** | Module/Plugin System | Nothing | Small |
| **Phase 2** | C2 Server + Session Manager | Phase 1 | Medium |
| **Phase 3** | Beacon Generator | Phase 2 | Medium |
| **Phase 4** | Operator Console | Phase 2+3 | Medium |
| **Phase 5** | Staging Engine (recipes) | Phase 2 | Small |
| **Phase 6** | Memory Injection Modules | Phase 1 | Small |
| **Phase 7** | GUI Integration | Phase 2-5 | Medium |

---

## Verification Plan

### Automated (CLI)
- Start C2 listener → generate beacon → run beacon locally → verify session appears
- `sessions` command shows the local implant
- `shell whoami` returns current user
- `use whoami` module returns output
- Stage a `windows_full` recipe → verify file is served at `/stage/<id>`

### Manual
- Test beacon across network (two machines on same LAN)
- Verify jitter timing randomization
- Confirm AMSI patch + poly wrapping produces unique stagers
