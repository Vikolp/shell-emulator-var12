#!/usr/bin/env python3
"""
Эмулятор командной оболочки UNIX-подобной ОС.
Вариант №12.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# Добавляем src в путь, чтобы импорты работали при запуске
sys.path.insert(0, str(Path(__file__).resolve().parent))

from commands import CommandError, CommandHandler
from vfs import VirtualFileSystem


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Разбор аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Shell Emulator (Вариант 12)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--vfs",
        type=str,
        default=None,
        help="Путь к директории VFS",
    )
    parser.add_argument(
        "--script",
        type=str,
        default=None,
        help="Путь к стартовому скрипту",
    )
    return parser.parse_args(argv)


def print_debug_config(args: argparse.Namespace) -> None:
    """Отладочный вывод параметров при запуске (Этап 2)."""
    print("=== Emulator configuration ===", flush=True)
    print(f"vfs:    {args.vfs if args.vfs else '(default)'}", flush=True)
    print(f"script: {args.script if args.script else '(none)'}", flush=True)
    print("==============================", flush=True)


def simple_parse(line: str) -> Tuple[str, List[str]]:
    """
    Простой парсер: разбивает строку по пробелам.
    Возвращает (команда, список аргументов).
    """
    parts = line.strip().split()
    if not parts:
        return "", []
    return parts[0], parts[1:]


def get_prompt(vfs: VirtualFileSystem) -> str:
    """Сформировать приглашение к вводу (содержит имя VFS)."""
    cwd_path = vfs.cwd.path()
    return f"{vfs.name}:{cwd_path}$ "


def run_script(handler: CommandHandler, script_path: str) -> None:
    """
    Выполнить стартовый скрипт.
    Останавливается при первой ошибке (требование варианта 12).
    На экране отображается и ввод, и вывод.
    """
    path = Path(script_path)
    if not path.exists():
        print(f"Error: script not found: {script_path}", file=sys.stderr)
        sys.exit(1)

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        print(f"Error: cannot read script: {exc}", file=sys.stderr)
        sys.exit(1)

    for raw_line in lines:
        line = raw_line.strip()

        # Пропускаем пустые строки и комментарии
        if not line or line.startswith("#"):
            continue

        # Показываем ввод (имитация диалога)
        prompt = get_prompt(handler.vfs)
        print(f"{prompt}{line}", flush=True)

        command, args = simple_parse(line)
        if not command:
            continue

        try:
            result = handler.execute(command, args)
            if result is not None:
                print(result)
        except CommandError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            # Останавливаемся при первой ошибке
            print("Script stopped due to error.", file=sys.stderr)
            sys.exit(1)
        except SystemExit:
            raise


def repl(handler: CommandHandler) -> None:
    """Интерактивный режим (REPL)."""
    while True:
        try:
            prompt = get_prompt(handler.vfs)
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            break

        command, args = simple_parse(line)
        if not command:
            continue

        try:
            result = handler.execute(command, args)
            if result is not None:
                print(result)
        except CommandError as exc:
            print(f"Error: {exc}", file=sys.stderr)
        except SystemExit:
            break


def main(argv: Optional[List[str]] = None) -> int:
    """Точка входа."""
    args = parse_args(argv)

    # Отладочный вывод параметров
    print_debug_config(args)

    # Загрузка VFS
    try:
        vfs = VirtualFileSystem(source_path=args.vfs)
    except (FileNotFoundError, ValueError, PermissionError) as exc:
        print(f"Error loading VFS: {exc}", file=sys.stderr)
        return 1

    handler = CommandHandler(vfs)

    # Выполнение стартового скрипта (если указан)
    if args.script:
        try:
            run_script(handler, args.script)
        except SystemExit as exc:
            return int(exc.code) if isinstance(exc.code, int) else 0
        return 0

    # Интерактивный режим
    try:
        repl(handler)
    except SystemExit:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
