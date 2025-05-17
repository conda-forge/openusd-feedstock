#!/usr/bin/env python
"""
openusd_plugins_sanity_check.py
----------------------------------------------------------
Exit 0  – when all registered USD plug‑ins load successfully **and**
          their count is strictly greater than the threshold supplied
          on the command line.

Exit 1  – when the plug‑in count is not greater than the threshold
          OR at least one plug‑in fails to load.

Exit 2  – bad invocation (missing or non‑integer argument).

Usage:
    python openusd_plugins_sanity_check.py 40
"""

import sys
from pxr import Plug

def main() -> int:
    # ------------------------- argument parsing -------------------------
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <min_plugin_count>", file=sys.stderr)
        return 2

    try:
        threshold = int(sys.argv[1])
    except ValueError:
        print("Error: threshold must be an integer.", file=sys.stderr)
        return 2

    # ------------------------ enumerate plug‑ins ------------------------
    registry       = Plug.Registry()
    all_plugins    = registry.GetAllPlugins()
    plugin_count   = len(all_plugins)
    load_failures  = []

    for plugin in all_plugins:
        # PlugPlugin.Load() returns True on success, False on failure.
        # It is a no‑op if the plug‑in is already loaded.
        try:
            if not plugin.Load():
                load_failures.append(plugin.GetName())
        except Exception as exc:             # defensive: catch unexpected errors
            load_failures.append(plugin.GetName())
            print(f"Exception while loading '{plugin.GetName()}': {exc}",
                  file=sys.stderr)

    # --------------------------- decide exit ----------------------------
    if load_failures:
        print("Plug‑in(s) failed to load:", ", ".join(load_failures),
              file=sys.stderr)

    if plugin_count > threshold and not load_failures:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
