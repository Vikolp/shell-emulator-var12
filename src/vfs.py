"""
Виртуальная файловая система (VFS).
Все операции выполняются только в памяти.
Источник данных — директория на диске.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union


@dataclass
class VFSNode:
    """Узел виртуальной файловой системы."""

    name: str
    is_dir: bool
    content: bytes = b""
    children: Dict[str, "VFSNode"] = field(default_factory=dict)
    parent: Optional["VFSNode"] = None

    def add_child(self, node: "VFSNode") -> None:
        """Добавить дочерний узел."""
        node.parent = self
        self.children[node.name] = node

    def get_child(self, name: str) -> Optional["VFSNode"]:
        """Получить дочерний узел по имени."""
        return self.children.get(name)

    def path(self) -> str:
        """Вернуть полный путь узла."""
        parts: List[str] = []
        current: Optional[VFSNode] = self
        while current is not None and current.name != "/":
            parts.append(current.name)
            current = current.parent
        if not parts:
            return "/"
        return "/" + "/".join(reversed(parts))


class VirtualFileSystem:
    """
    Виртуальная файловая система, работающая полностью в памяти.

    Источник: директория на диске (копируется при загрузке).
    Если путь не указан — создаётся минимальная VFS по умолчанию.
    """

    def __init__(self, source_path: Optional[str] = None) -> None:
        self.name: str = "default"
        self.root: VFSNode = VFSNode(name="/", is_dir=True)
        self.cwd: VFSNode = self.root
        self._source_path: Optional[str] = source_path
        self._hash: Optional[str] = None

        if source_path:
            self._load_from_directory(source_path)
        else:
            self._create_default()

    def _create_default(self) -> None:
        """Создать минимальную VFS по умолчанию."""
        self.name = "default"
        home = VFSNode(name="home", is_dir=True)
        user = VFSNode(name="user", is_dir=True)
        docs = VFSNode(name="documents", is_dir=True)
        readme = VFSNode(
            name="readme.txt",
            is_dir=False,
            content=b"Welcome to default VFS\n",
        )
        docs.add_child(readme)
        user.add_child(docs)
        home.add_child(user)
        self.root.add_child(home)
        self.cwd = self.root
        self._recalculate_hash()

    def _load_from_directory(self, path: str) -> None:
        """Загрузить VFS из директории на диске."""
        src = Path(path)
        if not src.exists():
            raise FileNotFoundError(f"VFS path not found: {path}")
        if not src.is_dir():
            raise ValueError(f"VFS path is not a directory: {path}")

        self.name = src.name
        self._source_path = str(src.resolve())
        self.root = VFSNode(name="/", is_dir=True)

        def walk(current_dir: Path, parent_node: VFSNode) -> None:
            try:
                entries = sorted(current_dir.iterdir(), key=lambda p: p.name)
            except PermissionError as exc:
                msg = f"Cannot read directory: {current_dir}"
                raise PermissionError(msg) from exc

            for entry in entries:
                if entry.name.startswith("."):
                    continue
                if entry.is_dir():
                    node = VFSNode(name=entry.name, is_dir=True)
                    parent_node.add_child(node)
                    walk(entry, node)
                elif entry.is_file():
                    try:
                        content = entry.read_bytes()
                    except (OSError, PermissionError):
                        content = b""
                    node = VFSNode(
                        name=entry.name,
                        is_dir=False,
                        content=content,
                    )
                    parent_node.add_child(node)

        walk(src, self.root)
        self.cwd = self.root
        self._recalculate_hash()

    def _recalculate_hash(self) -> None:
        """Пересчитать SHA-256 хеш всего содержимого VFS."""
        hasher = hashlib.sha256()

        def visit(node: VFSNode, prefix: str) -> None:
            path = f"{prefix}/{node.name}" if prefix else node.name
            if node.is_dir:
                hasher.update(f"DIR:{path}\n".encode())
                for child_name in sorted(node.children.keys()):
                    visit(node.children[child_name], path)
            else:
                hasher.update(f"FILE:{path}\n".encode())
                hasher.update(node.content)

        visit(self.root, "")
        self._hash = hasher.hexdigest()

    @property
    def sha256(self) -> str:
        """Вернуть SHA-256 хеш текущего состояния VFS."""
        if self._hash is None:
            self._recalculate_hash()
        return self._hash or ""

    def resolve(self, path: str) -> Optional[VFSNode]:
        """
        Разрешить путь относительно текущей директории.
        Поддерживает абсолютные и относительные пути, а также '..' и '.'.
        """
        if not path or path == ".":
            return self.cwd

        if path.startswith("/"):
            current: Optional[VFSNode] = self.root
            parts = [p for p in path.split("/") if p]
        else:
            current = self.cwd
            parts = [p for p in path.split("/") if p]

        for part in parts:
            if current is None or not current.is_dir:
                return None
            if part == ".":
                continue
            if part == "..":
                if current.parent is not None:
                    current = current.parent
                continue
            current = current.get_child(part)
            if current is None:
                return None
        return current

    def change_dir(self, path: str) -> None:
        """Сменить текущую директорию."""
        target = self.resolve(path)
        if target is None:
            raise FileNotFoundError(f"No such file or directory: {path}")
        if not target.is_dir:
            raise NotADirectoryError(f"Not a directory: {path}")
        self.cwd = target

    def list_dir(self, path: str = ".") -> List[str]:
        """Вернуть список имён в директории."""
        target = self.resolve(path)
        if target is None:
            raise FileNotFoundError(f"No such file or directory: {path}")
        if not target.is_dir:
            raise NotADirectoryError(f"Not a directory: {path}")
        names = sorted(target.children.keys())
        return names

    def get_content(self, path: str) -> bytes:
        """Получить содержимое файла."""
        target = self.resolve(path)
        if target is None:
            raise FileNotFoundError(f"No such file or directory: {path}")
        if target.is_dir:
            raise IsADirectoryError(f"Is a directory: {path}")
        return target.content

    def make_dir(self, path: str) -> None:
        """Создать директорию (только в памяти)."""
        path = path.rstrip("/")
        if not path or path == "/":
            raise ValueError("Cannot create root directory")

        parent_path = str(Path(path).parent)
        name = Path(path).name

        if parent_path == ".":
            parent = self.cwd
        else:
            parent = self.resolve(parent_path)

        if parent is None:
            raise FileNotFoundError(f"No such file or directory: {parent_path}")
        if not parent.is_dir:
            raise NotADirectoryError(f"Not a directory: {parent_path}")
        if name in parent.children:
            raise FileExistsError(f"File exists: {path}")

        new_dir = VFSNode(name=name, is_dir=True)
        parent.add_child(new_dir)
        self._recalculate_hash()

    def copy(self, src: str, dst: str) -> None:
        """
        Копировать файл или директорию (только в памяти).
        Рекурсивное копирование директорий.
        """
        source = self.resolve(src)
        if source is None:
            raise FileNotFoundError(f"No such file or directory: {src}")

        dst_path = Path(dst)
        dst_name = dst_path.name
        dst_parent_path = str(dst_path.parent)

        if dst_parent_path == ".":
            parent = self.cwd
        else:
            parent = self.resolve(dst_parent_path)

        if parent is None:
            msg = f"No such file or directory: {dst_parent_path}"
            raise FileNotFoundError(msg)
        if not parent.is_dir:
            msg = f"Not a directory: {dst_parent_path}"
            raise NotADirectoryError(msg)

        # Если целевой путь существует и это директория — копируем внутрь
        existing = parent.get_child(dst_name)
        if existing is not None and existing.is_dir and not source.is_dir:
            parent = existing
            dst_name = source.name

        if parent.get_child(dst_name) is not None:
            raise FileExistsError(f"File exists: {dst}")

        def clone(node: VFSNode) -> VFSNode:
            new_node = VFSNode(
                name=node.name,
                is_dir=node.is_dir,
                content=node.content,
            )
            if node.is_dir:
                for child in node.children.values():
                    cloned = clone(child)
                    new_node.add_child(cloned)
            return new_node

        cloned = clone(source)
        cloned.name = dst_name
        parent.add_child(cloned)
        self._recalculate_hash()

    def info(self) -> str:
        """Информация о VFS для команды vfs-info."""
        return f"VFS name: {self.name}\nSHA-256: {self.sha256}"
