from __future__ import annotations
import subprocess
from pathlib import Path, PurePosixPath
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.standard import blacklist_subset
from llobot.knowledge.subsets.universal import UniversalSubset
from llobot.projects import Project
from llobot.projects.items import ProjectDirectory, ProjectFile, ProjectItem, ProjectLink
from llobot.utils.fs import create_parents, read_document, write_text
from llobot.utils.values import ValueTypeMixin
from llobot.utils.zones import validate_zone
from llobot.formats.paths import coerce_path

class DirectoryProject(Project, ValueTypeMixin):
    """
    A project that sources its content from a filesystem directory.
    Can be configured to be mutable.
    """
    _directory: Path
    _prefix: PurePosixPath
    _whitelist: KnowledgeSubset
    _blacklist: KnowledgeSubset
    _mutable: bool
    _executable: bool

    def __init__(
        self,
        directory: Path | str,
        *,
        prefix: PurePosixPath | str | None = None,
        whitelist: KnowledgeSubset | None = None,
        blacklist: KnowledgeSubset | None = None,
        mutable: bool = False,
        executable: bool = False,
    ):
        """
        Initializes a new DirectoryProject.

        Args:
            directory: The path to the project's root directory. It can contain `~`.
            prefix: The path prefix for all items in the project. If `None`, it
                    defaults to the path relative to the user's home directory
                    for directories under home, or the last component otherwise.
            whitelist: A custom whitelist subset for this project.
            blacklist: A custom blacklist subset for this project.
            mutable: If `True`, the project allows write operations. Defaults to `False`.
            executable: If `True`, the project allows script execution. Defaults to `False`.
        """
        self._directory = Path(directory).expanduser().absolute()

        # Compute default prefix: home-relative path for directories under home,
        # otherwise fall back to directory name
        if prefix is not None:
            self._prefix = coerce_path(prefix)
        else:
            home = Path.home()
            relative = self._directory.relative_to(home) if self._directory.is_relative_to(home) else None
            # Use home-relative path if under home and not the home directory itself
            if relative is not None and relative.parts:
                self._prefix = coerce_path(relative)
            else:
                self._prefix = coerce_path(self._directory.name)
        validate_zone(self._prefix)

        self._whitelist = whitelist or UniversalSubset()
        self._blacklist = blacklist or blacklist_subset()
        self._mutable = mutable
        self._executable = executable

    @property
    def directory(self) -> Path:
        """The underlying filesystem directory path."""
        return self._directory

    @property
    def prefixes(self) -> set[PurePosixPath]:
        return {self._prefix}

    @property
    def summary(self) -> list[str]:
        parts = [f"Directory `~/{self._prefix}`"]
        if self._mutable:
            parts.append("mutable")
        else:
            parts.append("read-only")
        if self._executable:
            parts.append("executable")

        expected_path = Path.home() / self._prefix
        if self._directory != expected_path:
            parts.append(f"real location `{self._directory}`")

        return [", ".join(parts)]

    def _to_local_path(self, path: PurePosixPath) -> PurePosixPath | None:
        """Strips the project prefix from a path. Returns None if path is not under the prefix."""
        try:
            return path.relative_to(self._prefix)
        except ValueError:
            return None

    def items(self, path: PurePosixPath) -> list[ProjectItem]:
        local_path = self._to_local_path(path)
        if local_path is None:
            return []
        real_path = self._directory / local_path
        if not real_path.is_dir():
            return []

        result = []
        for p in real_path.iterdir():
            item_path = path / p.name
            if p.is_file():
                result.append(ProjectFile(item_path))
            elif p.is_dir():
                result.append(ProjectDirectory(item_path))
            elif p.is_symlink():
                result.append(ProjectLink(item_path, PurePosixPath(p.readlink())))
        return result

    def read(self, path: PurePosixPath) -> str | None:
        local_path = self._to_local_path(path)
        if local_path is None:
            return None
        real_path = self._directory / local_path
        if not real_path.is_file():
            return None
        try:
            return read_document(real_path)
        except (ValueError, UnicodeDecodeError):
            return None # e.g. binary file

    def tracked(self, item: ProjectItem) -> bool:
        if isinstance(item, ProjectFile):
            return item.path in self._whitelist and item.path not in self._blacklist
        if isinstance(item, ProjectDirectory):
            return item.path not in self._blacklist
        return False

    def mutable(self, path: PurePosixPath) -> bool:
        """
        Checks if the path is mutable.

        A path is mutable if the project is configured as mutable and the
        path is within the project's prefix.
        """
        return self._mutable and self._to_local_path(path) is not None

    def write(self, path: PurePosixPath, content: str) -> None:
        """
        Writes content to a file in the project directory.

        Args:
            path: The project path of the file to write.
            content: The content to write.

        Raises:
            PermissionError: If the project is not mutable or the path is
                             outside the project prefix.
        """
        if not self.mutable(path):
            raise PermissionError(f"Path is not mutable in this project: ~/{path}")
        local_path = self._to_local_path(path)
        # This should not happen if mutable() check passed
        assert local_path, f"Path {path} is not under project prefix despite mutable() check passing"
        real_path = self._directory / local_path
        write_text(real_path, content)

    def remove(self, path: PurePosixPath) -> None:
        """
        Removes a file from the project directory.

        Args:
            path: The project path of the file to remove.

        Raises:
            PermissionError: If the project is not mutable or the path is
                             outside the project prefix.
            FileNotFoundError: If the path does not exist.
            IsADirectoryError: If the path is a directory.
        """
        if not self.mutable(path):
            raise PermissionError(f"Path is not mutable in this project: ~/{path}")
        local_path = self._to_local_path(path)
        # This should not happen if mutable() check passed
        assert local_path, f"Path {path} is not under project prefix despite mutable() check passing"
        real_path = self._directory / local_path
        real_path.unlink()

    def move(self, source: PurePosixPath, destination: PurePosixPath) -> None:
        """
        Moves a file within the project directory using a filesystem move.

        Args:
            source: The project path of the file to move.
            destination: The new project path for the file.

        Raises:
            PermissionError: If the project is not mutable or if either path
                             is outside the project prefix.
            FileNotFoundError: If the source file does not exist.
        """
        if not self.mutable(source):
            raise PermissionError(f"Source path is not mutable in this project: ~/{source}")
        if not self.mutable(destination):
            raise PermissionError(f"Destination path is not mutable in this project: ~/{destination}")

        source_local = self._to_local_path(source)
        dest_local = self._to_local_path(destination)
        # This should not happen if mutable() check passed
        assert source_local, f"Path {source} is not under project prefix despite mutable() check passing"
        assert dest_local, f"Path {destination} is not under project prefix despite mutable() check passing"

        real_source = self._directory / source_local
        real_dest = self._directory / dest_local

        create_parents(real_dest)
        real_source.rename(real_dest)

    def executable(self, path: PurePosixPath) -> bool:
        """
        Checks if the path is executable.

        A path is executable if the project is configured as executable and the
        path is within the project's prefix.
        """
        return self._executable and self._to_local_path(path) is not None

    def execute(self, path: PurePosixPath, script: str) -> str:
        """
        Executes a shell script in the project directory.

        The script is executed with `set -euxo pipefail` enabled by default.

        Args:
            path: The project path to use as working directory.
            script: The shell script to execute.

        Returns:
            The combined stdout and stderr of the script, followed by the exit code.

        Raises:
            PermissionError: If the project is not executable or the path is
                             outside the project prefix.
            FileNotFoundError: If the working directory does not exist.
        """
        if not self.executable(path):
            raise PermissionError(f"Path is not executable in this project: ~/{path}")

        local_path = self._to_local_path(path)
        # This should not happen if executable() check passed
        assert local_path, f"Path {path} is not under project prefix despite executable() check passing"
        real_path = self._directory / local_path

        if not real_path.is_dir():
            raise FileNotFoundError(f"Working directory not found: ~/{path}")

        result = subprocess.run(
            f"set -euxo pipefail\n{script}",
            shell=True,
            executable='/bin/bash',
            cwd=real_path,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        output = result.stdout
        if output and not output.endswith('\n'):
            output += '\n'
        output += f"Exit code: {result.returncode}\n"
        return output

__all__ = [
    'DirectoryProject',
]
