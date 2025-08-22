import argparse
import re
import sys
from pathlib import Path
from .config import Config
from .dump import dump_repository

try:
    import pyperclip
except ImportError:
    pyperclip = None


def parse_args():
    p = argparse.ArgumentParser(
        description="Map a repository to text (tree + files)"
    )
    p.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repository root path (default: .)",
    )
    p.add_argument(
        "-o", "--output", help="Output file path (default: ./repo_dump.md)"
    )
    p.add_argument(
        "--stdout", action="store_true", help="Print to stdout instead of file"
    )
    p.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and directories",
    )
    p.add_argument(
        "--respect-gitignore",
        action="store_true",
        help="Respect .gitignore (requires pathspec)",
    )
    p.add_argument(
        "--ignore-dir",
        action="append",
        help="Directory name to ignore (repeatable)",
    )
    p.add_argument(
        "--max-file-bytes",
        type=int,
        default=4_000_000,
        help="Max individual file size in bytes",
    )
    p.add_argument(
        "--max-output-chars",
        type=int,
        default=0,
        help="Max output length in characters (0 = unlimited)",
    )
    p.add_argument(
        "--follow-symlinks", action="store_true", help="Follow symlinks"
    )
    p.add_argument(
        "--to-clipboard",
        action="store_true",
        help="Copy output to clipboard (requires pyperclip)",
    )
    p.add_argument(
        "--clipboard-max-chars",
        type=int,
        default=700_000,
        help="Max characters allowed for clipboard copy",
    )
    p.add_argument(
        "--eol",
        choices=["lf", "crlf", "platform"],
        default="lf",
        help="Line endings for output: lf (\\n), crlf (\\r\\n), or platform",
    )
    return p.parse_args()


def _normalize_eol(text: str, mode: str) -> str:
    """
    Normalize all EOLs deterministically to the target mode, preserving
    single newlines. Does NOT collapse legitimate blank lines.
    """
    # Split on ANY EOL, then re-join with the chosen one.
    lines = re.split(r"\r\n|\n\r|\r|\n", text)
    if mode == "lf":
        eol = "\n"
    elif mode == "crlf":
        eol = "\r\n"
    else:
        eol = "\r\n" if sys.platform.startswith("win") else "\n"
    return eol.join(lines)


def main(argv=None):
    args = parse_args()

    cfg = Config(
        root=Path(args.path).resolve(),
        output=Path(args.output) if args.output else None,
        stdout=args.stdout,
        include_hidden=args.include_hidden,
        respect_gitignore=args.respect_gitignore,
        ignore_dirs=args.ignore_dir or [],
        max_file_bytes=args.max_file_bytes,
        max_output_chars=args.max_output_chars,
        follow_symlinks=args.follow_symlinks,
        to_clipboard=args.to_clipboard,
        clipboard_max_chars=args.clipboard_max_chars,
    )

    text = dump_repository(cfg)

    # Normalize EOLs for the whole document to the requested style.
    out_text = _normalize_eol(text, args.eol)
    out_bytes = out_text.encode("utf-8")

    if not cfg.stdout:
        out_path = cfg.output if cfg.output else (cfg.root / "repo_dump.md")
        out_path.write_bytes(out_bytes)
        print(f"Export written to: {out_path}")

    if cfg.to_clipboard:
        if pyperclip:
            # Windows clipboard prefers CRLF
            clip_text = _normalize_eol(text, "crlf")
            if len(clip_text) <= cfg.clipboard_max_chars:
                pyperclip.copy(clip_text)
                print("Copied to clipboard.")
            else:
                print("Output too large for clipboard, not copied.")
        else:
            print("pyperclip is not installed; clipboard copy is unavailable.")

    if cfg.stdout:
        sys.stdout.buffer.write(out_bytes)

    return 0
