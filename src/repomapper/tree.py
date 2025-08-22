from pathlib import Path
from typing import List, Tuple
from .ignore import is_ignored


def build_tree(
    root: Path, include_hidden: bool, ignore_dirs: set[str], gi_spec
) -> Tuple[str, int, int]:
    lines: List[str] = []
    nb_dirs = 0
    nb_files = 0

    def _walk(dir_path: Path, prefix: str = ""):
        nonlocal nb_dirs, nb_files
        try:
            entries = sorted(
                dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())
            )
        except PermissionError:
            lines.append(f"{prefix}[permission denied] {dir_path.name}")
            return

        entries = [
            e
            for e in entries
            if (include_hidden or not e.name.startswith("."))
            and not e.is_symlink()
        ]

        filtered = []
        for e in entries:
            rel = e.relative_to(root).as_posix()
            if e.is_dir():
                if e.name in ignore_dirs:
                    continue
                if is_ignored(rel + "/", gi_spec):
                    continue
            else:
                if is_ignored(rel, gi_spec):
                    continue
            filtered.append(e)

        for idx, e in enumerate(filtered):
            connector = "└── " if idx == len(filtered) - 1 else "├── "
            next_prefix = "    " if idx == len(filtered) - 1 else "│   "
            if e.is_dir():
                lines.append(f"{prefix}{connector}{e.name}/")
                nb_dirs += 1
                _walk(e, prefix + next_prefix)
            else:
                lines.append(f"{prefix}{connector}{e.name}")
                nb_files += 1

    lines.append(f"{root.resolve().name}/")
    _walk(root)
    return "\n".join(lines), nb_dirs, nb_files
