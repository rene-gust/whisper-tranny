#!/bin/bash

BASE="$(cd "$(dirname "$0")" && pwd)"

source "$BASE/venv/bin/activate"
python3 "$BASE/whisper-tranny.py"
