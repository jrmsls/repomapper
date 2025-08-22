from pathlib import Path

BINARY_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".gz",
    ".tgz",
    ".xz",
    ".7z",
    ".rar",
    ".jar",
    ".war",
    ".class",
    ".o",
    ".so",
    ".dll",
    ".dylib",
    ".exe",
    ".bin",
    ".dat",
    ".lock",
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
    ".mp3",
    ".flac",
    ".wav",
    ".mp4",
    ".mkv",
    ".mov",
    ".avi",
    ".heic",
}

LANG_BY_EXT = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".jsx": "jsx",
    ".json": "json",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    ".env": "",
    ".md": "markdown",
    ".rst": "rst",
    ".sql": "sql",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".less": "less",
    ".go": "go",
    ".java": "java",
    ".kt": "kotlin",
    ".rs": "rust",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".hh": "cpp",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".m": "objectivec",
    ".mm": "objectivec",
    ".swift": "swift",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "zsh",
    ".ps1": "powershell",
    ".dockerfile": "dockerfile",
    "Dockerfile": "dockerfile",
    ".makefile": "make",
    "Makefile": "make",
}


def is_binary_path(p: Path) -> bool:
    return p.suffix.lower() in BINARY_EXTS


def is_probably_binary(chunk: bytes) -> bool:
    if b"\x00" in chunk:
        return True
    text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(32, 127)))
    nontext = sum(b not in text_chars for b in chunk)
    return nontext / max(1, len(chunk)) > 0.30


def detect_lang(file: Path) -> str:
    if file.name in LANG_BY_EXT:
        return LANG_BY_EXT[file.name]
    return LANG_BY_EXT.get(file.suffix.lower(), "")
