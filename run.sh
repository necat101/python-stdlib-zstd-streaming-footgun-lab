#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON_BIN:-}"
if [ -z "$PY" ]; then
  for c in python3.14 python3 python; do
    if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
  done
fi
if [ -z "$PY" ]; then echo "No python found (set PYTHON_BIN)" >&2; exit 1; fi
echo "Using: $("$PY" -c 'import sys; print(sys.executable, sys.version.split()[0])')"
"$PY" -m py_compile run_lab.py test_lab.py
"$PY" run_lab.py
"$PY" -m unittest -v
