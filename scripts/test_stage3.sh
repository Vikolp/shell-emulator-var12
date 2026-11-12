#!/usr/bin/env bash
# Тесты Этапа 3: разные варианты VFS

set -e
cd "$(dirname "$0")/.."

echo "=== Test Stage 3: VFS ==="

echo "--- 1. Default VFS (без --vfs) ---"
python3 src/emulator.py --script scripts/commands_stage3.txt || true

echo ""
echo "--- 2. Minimal VFS ---"
python3 src/emulator.py --vfs vfs/minimal --script scripts/commands_stage3_minimal.txt || true

echo ""
echo "--- 3. Multi-file VFS ---"
python3 src/emulator.py --vfs vfs/multi --script scripts/commands_stage3_multi.txt || true

echo ""
echo "--- 4. Deep VFS (≥3 levels) ---"
python3 src/emulator.py --vfs vfs/deep --script scripts/commands_stage3_deep.txt || true

echo ""
echo "--- 5. Ошибка загрузки (несуществующий путь) ---"
python3 src/emulator.py --vfs /nonexistent/path --script scripts/commands_stage3.txt || true

echo ""
echo "=== Stage 3 tests finished ==="
