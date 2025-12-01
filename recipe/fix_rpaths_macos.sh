#!/bin/sh
set -eu

: "${PREFIX:?PREFIX must be set}"

MANIFEST="install_manifest.txt"

if [ ! -f "$MANIFEST" ]; then
    echo "install_manifest.txt not found at $MANIFEST" >&2
    exit 1
fi

# Find .dylib / .so files from the manifest
grep -E '\.(dylib|so)(\.[0-9]+)*$' "$MANIFEST" | while IFS= read -r lib; do
    [ -f "$lib" ] || continue

    echo "Processing $lib"

    # Extract all LC_RPATH paths via otool + awk
    otool -l "$lib" 2>/dev/null \
    | awk '
        $1 == "cmd" && $2 == "LC_RPATH" {in_rpath=1}
        in_rpath && $1 == "path" {print $2; in_rpath=0}
      ' \
    | while IFS= read -r rp; do
        [ -n "$rp" ] || continue
        echo "  Deleting rpath: $rp"
        # Do not fail if delete_rpath fails for some reason
        install_name_tool -delete_rpath "$rp" "$lib" 2>/dev/null || :
      done

    echo "  Adding rpath: $PREFIX/lib"
    install_name_tool -add_rpath "$PREFIX/lib" "$lib"
done
