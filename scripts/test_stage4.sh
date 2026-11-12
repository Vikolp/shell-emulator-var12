#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

echo "=== Test Stage 4: Main commands ==="
python3 src/emulator.py --script scripts/commands_stage4.txt || true
echo "=== Stage 4 tests finished ==="
