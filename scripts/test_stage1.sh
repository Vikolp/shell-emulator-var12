#!/usr/bin/env bash
# Тестовый скрипт для Этапа 1 (REPL)
# Запускается из реальной ОС

set -e
cd "$(dirname "$0")/.."

echo "=== Test Stage 1: REPL ==="

# Запуск без параметров (должен стартовать с default VFS)
echo "--- Run without arguments ---"
python3 src/emulator.py --script scripts/commands_stage1.txt

echo ""
echo "=== Stage 1 tests finished ==="
