from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class Config:
    root: Path
    output: Optional[Path] = None
    stdout: bool = False
    include_hidden: bool = False
    respect_gitignore: bool = False
    ignore_dirs: List[str] = field(default_factory=list)
    max_file_bytes: int = 4_000_000
    max_output_chars: int = 0
    follow_symlinks: bool = False
    to_clipboard: bool = False
    clipboard_max_chars: int = 700_000
