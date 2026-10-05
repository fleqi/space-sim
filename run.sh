#!/usr/bin/env bash
# Crea el entorno virtual (si no existe), instala dependencias y ejecuta el simulador.
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi
exec .venv/bin/python Tarea3.py "$@"
