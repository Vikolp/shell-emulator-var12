#!/usr/bin/env bash
# Скрипт запуска эмулятора оболочки

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python3 src/emulator.py "$@"
