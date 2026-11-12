#!/usr/bin/env bash
# Тестовые скрипты реальной ОС для Этапа 2 (конфигурация)

set -e
cd "$(dirname "$0")/.."

echo "=== Test Stage 2: Configuration ==="

echo "--- 1. Без параметров ---"
python3 src/emulator.py --script scripts/commands_stage2.txt || true

echo ""
echo "--- 2. С указанием VFS ---"
python3 src/emulator.py --vfs vfs/minimal --script scripts/commands_stage2.txt || true

echo ""
echo "--- 3. С указанием VFS и скрипта ---"
python3 src/emulator.py --vfs vfs/multi --script scripts/commands_stage2.txt || true

echo ""
echo "=== Stage 2 tests finished ==="
