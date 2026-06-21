#!/usr/bin/env bash
# Launch the Space Weather Dashboard locally (macOS / Linux).
#
# Behaviour:
#   * If a conda env or virtualenv is already active, install into it and run.
#     (Use this with the Python 3.12 'swdash' conda env for full HUXt support:
#        conda env create -f environment.yml && conda activate swdash && ./run.sh)
#   * Otherwise create a local .venv, install requirements there, and run.
set -euo pipefail

cd "$(dirname "$0")"

if [ -n "${CONDA_PREFIX:-}" ] || [ -n "${VIRTUAL_ENV:-}" ]; then
  echo "Using active environment: ${CONDA_PREFIX:-$VIRTUAL_ENV}"
  PY=python
  "$PY" -m pip install -q -r requirements.txt
else
  if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in .venv ..."
    python3 -m venv .venv
    ./.venv/bin/python -m pip install --upgrade pip
    ./.venv/bin/python -m pip install -r requirements.txt
  fi
  PY=./.venv/bin/python
fi

# Use the project's Streamlit config (dark space theme).
export STREAMLIT_CONFIG_DIR="$(pwd)/swdash/.streamlit"

echo "Starting dashboard at http://localhost:8501 ..."
# Invoke Streamlit as a module to avoid stale `streamlit` console-script shims.
exec "$PY" -m streamlit run swdash/app.py "$@"
