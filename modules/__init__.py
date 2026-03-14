"""
modules/__init__.py — Hot-Loadable Plugin System

Automatically discovers and registers Python module files placed in the
modules/ directory. Each module must define:
  MODULE_INFO = {"name": "...", "description": "...", "author": "...", "platform": "windows|linux|all"}
  def run(session, args): ...  # Returns string output
"""
import os
import importlib
import importlib.util
import sys

MODULES = {}

_MODULES_DIR = os.path.dirname(os.path.abspath(__file__))


def _validate_module(mod):
    """Check a module has the required interface."""
    if not hasattr(mod, 'MODULE_INFO'):
        return False
    info = mod.MODULE_INFO
    for key in ('name', 'description', 'platform'):
        if key not in info:
            return False
    if not hasattr(mod, 'run') or not callable(mod.run):
        return False
    return True


def discover():
    """
    Scan the modules/ directory for .py files containing valid
    MODULE_INFO + run() definitions. Returns the MODULES dict.
    """
    global MODULES
    MODULES.clear()

    for filename in sorted(os.listdir(_MODULES_DIR)):
        if filename.startswith('_') or not filename.endswith('.py'):
            continue

        mod_name = filename[:-3]
        filepath = os.path.join(_MODULES_DIR, filename)

        try:
            spec = importlib.util.spec_from_file_location(f"modules.{mod_name}", filepath)
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            if _validate_module(mod):
                MODULES[mod.MODULE_INFO['name']] = {
                    'info': mod.MODULE_INFO,
                    'run': mod.run,
                    'file': filename,
                }
        except Exception as e:
            print(f"[!] Failed to load module {filename}: {e}")

    return MODULES


def list_modules():
    """Pretty-print all loaded modules."""
    if not MODULES:
        discover()
    lines = []
    lines.append(f"{'Name':<20} {'Platform':<10} {'Description'}")
    lines.append("-" * 60)
    for name, entry in MODULES.items():
        info = entry['info']
        lines.append(f"{name:<20} {info['platform']:<10} {info['description']}")
    return "\n".join(lines)


def run_module(name, session=None, args=None):
    """Execute a module by name."""
    if not MODULES:
        discover()
    if name not in MODULES:
        return f"[!] Module '{name}' not found. Use 'list' to see available modules."
    try:
        return MODULES[name]['run'](session, args or [])
    except Exception as e:
        return f"[!] Module '{name}' failed: {e}"


# Auto-discover on import
discover()
