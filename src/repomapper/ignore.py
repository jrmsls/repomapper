from pathlib import Path

try:
    import pathspec
except Exception:
    pathspec = None

COMMON_IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".mypy_cache",
    "dist",
    "build",
    "target",
    ".gradle",
    ".next",
    ".turbo",
    ".cache",
}


def load_gitignore(root: Path):
    if pathspec is None:
        return None
    gi = root / ".gitignore"
    if gi.exists():
        patterns = gi.read_text(encoding="utf-8", errors="ignore").splitlines()
        return pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    return None


def is_ignored(rel_path: str, spec) -> bool:
    return spec.match_file(rel_path) if spec else False
