#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

echo "=== Test Stage 5: Additional commands ==="
python3 src/emulator.py --script scripts/commands_stage5.txt || true
echo "=== Stage 5 tests finished ==="
