import os
from pathlib import Path
from typing import Iterable
from .ignore import is_ignored
from .utils import is_binary_path


def iter_files(
    root: Path,
    include_hidden: bool,
    ignore_dirs: set[str],
    gi_spec,
    max_file_bytes: int,
    follow_symlinks: bool,
) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(
        root, followlinks=follow_symlinks
    ):
        dir_path = Path(dirpath)

        # prune directories in-place
        pruned = []
        for d in list(dirnames):
            if d in ignore_dirs or (not include_hidden and d.startswith(".")):
                pruned.append(d)
                continue
            rel = (dir_path / d).relative_to(root).as_posix()
            if gi_spec and is_ignored(rel + "/", gi_spec):
                pruned.append(d)
        for d in pruned:
            dirnames.remove(d)

        for f in filenames:
            if not include_hidden and f.startswith("."):
                continue
            p = dir_path / f
            rel = p.relative_to(root).as_posix()
            if gi_spec and is_ignored(rel, gi_spec):
                continue
            try:
                if p.is_symlink() and not follow_symlinks:
                    continue
                if p.is_file():
                    if is_binary_path(p):
                        continue
                    size = p.stat().st_size
                    if size > max_file_bytes:
                        continue
                    yield p
            except OSError:
                continue
