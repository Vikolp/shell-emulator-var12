"""
Базовые тесты эмулятора.
Запуск: python -m pytest tests/ -v
или просто python tests/test_basic.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from vfs import VirtualFileSystem
from commands import CommandHandler, CommandError


def test_default_vfs():
    vfs = VirtualFileSystem()
    assert vfs.name == "default"
    assert vfs.cwd.name == "/"
    names = vfs.list_dir("/")
    assert "home" in names


def test_pwd():
    vfs = VirtualFileSystem()
    handler = CommandHandler(vfs)
    result = handler.execute("pwd", [])
    assert result == "/"


def test_cd_and_pwd():
    vfs = VirtualFileSystem()
    handler = CommandHandler(vfs)
    handler.execute("cd", ["home"])
    result = handler.execute("pwd", [])
    assert result == "/home"


def test_ls():
    vfs = VirtualFileSystem()
    handler = CommandHandler(vfs)
    result = handler.execute("ls", [])
    assert "home" in result


def test_mkdir_and_ls():
    vfs = VirtualFileSystem()
    handler = CommandHandler(vfs)
    handler.execute("mkdir", ["newdir"])
    result = handler.execute("ls", [])
    assert "newdir" in result


def test_unknown_command():
    vfs = VirtualFileSystem()
    handler = CommandHandler(vfs)
    try:
        handler.execute("foobar", [])
        assert False, "Should raise CommandError"
    except CommandError as exc:
        assert "Unknown command" in str(exc)


def test_vfs_info():
    vfs = VirtualFileSystem()
    handler = CommandHandler(vfs)
    result = handler.execute("vfs-info", [])
    assert "VFS name: default" in result
    assert "SHA-256:" in result


if __name__ == "__main__":
    tests = [
        test_default_vfs,
        test_pwd,
        test_cd_and_pwd,
        test_ls,
        test_mkdir_and_ls,
        test_unknown_command,
        test_vfs_info,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"FAIL: {t.__name__} — {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
    sys.exit(0 if passed == len(tests) else 1)
