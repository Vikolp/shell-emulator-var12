"""
Реализация команд эмулятора оболочки.
"""

from __future__ import annotations

import calendar
import datetime
from typing import List, Optional

from vfs import VirtualFileSystem


class CommandError(Exception):
    """Ошибка выполнения команды."""

    pass


class CommandHandler:
    """Обработчик команд эмулятора."""

    def __init__(self, vfs: VirtualFileSystem) -> None:
        self.vfs = vfs
        self.history: List[str] = []

    def execute(self, command: str, args: List[str]) -> Optional[str]:
        """
        Выполнить команду.
        Возвращает строку результата или None.
        Бросает CommandError при ошибках.
        """
        self.history.append(command + (" " + " ".join(args) if args else ""))

        handlers = {
            "ls": self._cmd_ls,
            "cd": self._cmd_cd,
            "exit": self._cmd_exit,
            "pwd": self._cmd_pwd,
            "date": self._cmd_date,
            "cal": self._cmd_cal,
            "vfs-info": self._cmd_vfs_info,
            "cp": self._cmd_cp,
            "mkdir": self._cmd_mkdir,
        }

        handler = handlers.get(command)
        if handler is None:
            raise CommandError(f"Unknown command: {command}")

        return handler(args)

    def _cmd_ls(self, args: List[str]) -> str:
        """Команда ls — список файлов."""
        # Игнорируем флаги (начинающиеся с -) — упрощённая реализация
        paths = [a for a in args if not a.startswith("-")]
        path = paths[0] if paths else "."
        try:
            names = self.vfs.list_dir(path)
        except FileNotFoundError as exc:
            raise CommandError(str(exc)) from exc
        except NotADirectoryError as exc:
            raise CommandError(str(exc)) from exc

        if not names:
            return ""
        return "\n".join(names)

    def _cmd_cd(self, args: List[str]) -> None:
        """Команда cd — смена директории."""
        if len(args) > 1:
            raise CommandError("cd: too many arguments")
        path = args[0] if args else "/"
        try:
            self.vfs.change_dir(path)
        except FileNotFoundError as exc:
            raise CommandError(str(exc)) from exc
        except NotADirectoryError as exc:
            raise CommandError(str(exc)) from exc
        return None

    def _cmd_exit(self, args: List[str]) -> str:
        """Команда exit — выход из эмулятора."""
        if args:
            raise CommandError("exit: too many arguments")
        raise SystemExit(0)

    def _cmd_pwd(self, args: List[str]) -> str:
        """Команда pwd — текущий путь."""
        if args:
            raise CommandError("pwd: too many arguments")
        return self.vfs.cwd.path()

    def _cmd_date(self, args: List[str]) -> str:
        """Команда date — текущая дата и время."""
        if args:
            raise CommandError("date: too many arguments")
        now = datetime.datetime.now()
        return now.strftime("%a %b %d %H:%M:%S %Y")

    def _cmd_cal(self, args: List[str]) -> str:
        """Команда cal — календарь."""
        now = datetime.datetime.now()
        year = now.year
        month = now.month

        if len(args) == 1:
            try:
                month = int(args[0])
                if not 1 <= month <= 12:
                    raise ValueError
            except ValueError as exc:
                raise CommandError("cal: invalid month") from exc
        elif len(args) == 2:
            try:
                month = int(args[0])
                year = int(args[1])
                if not 1 <= month <= 12:
                    raise ValueError
            except ValueError as exc:
                raise CommandError("cal: invalid arguments") from exc
        elif len(args) > 2:
            raise CommandError("cal: too many arguments")

        return calendar.month(year, month).rstrip()

    def _cmd_vfs_info(self, args: List[str]) -> str:
        """Служебная команда vfs-info."""
        if args:
            raise CommandError("vfs-info: too many arguments")
        return self.vfs.info()

    def _cmd_cp(self, args: List[str]) -> None:
        """Команда cp — копирование (только в памяти)."""
        if len(args) != 2:
            raise CommandError("cp: expected 2 arguments (source destination)")
        src, dst = args
        try:
            self.vfs.copy(src, dst)
        except FileNotFoundError as exc:
            raise CommandError(str(exc)) from exc
        except FileExistsError as exc:
            raise CommandError(str(exc)) from exc
        except NotADirectoryError as exc:
            raise CommandError(str(exc)) from exc
        return None

    def _cmd_mkdir(self, args: List[str]) -> None:
        """Команда mkdir — создание директории (только в памяти)."""
        if not args:
            raise CommandError("mkdir: missing operand")
        if len(args) > 1:
            raise CommandError("mkdir: too many arguments")
        path = args[0]
        try:
            self.vfs.make_dir(path)
        except FileNotFoundError as exc:
            raise CommandError(str(exc)) from exc
        except FileExistsError as exc:
            raise CommandError(str(exc)) from exc
        except NotADirectoryError as exc:
            raise CommandError(str(exc)) from exc
        except ValueError as exc:
            raise CommandError(str(exc)) from exc
        return None
