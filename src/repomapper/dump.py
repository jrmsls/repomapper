import io
import re
from pathlib import Path
from typing import Optional
from .config import Config
from .ignore import COMMON_IGNORED_DIRS, load_gitignore
from .tree import build_tree
from .collect import iter_files
from .utils import detect_lang, is_probably_binary

FENCE = "```"

# Recognize ANY EOL variant so we can recompose clean text deterministically.
_EOL_SPLIT = re.compile(r"\r\n|\n\r|\r|\n")


def _pick_fence_for(text: str) -> str:
    max_run = 0
    run = 0
    for ch in text:
        if ch == "`":
            run += 1
            if run > max_run:
                max_run = run
        else:
            run = 0
    fence_len = max(3, max_run + 1)
    return "`" * fence_len


def read_text_safely(
    p: Path,
    encodings=("utf-8", "utf-16", "latin-1"),
    probe_bytes: int = 8192,
) -> Optional[str]:
    try:
        with open(p, "rb") as fh:
            head = fh.read(probe_bytes)
            if is_probably_binary(head):
                return None
    except OSError:
        return None

    for enc in encodings:
        try:
            with open(
                p, "r", encoding=enc, errors="strict", newline=None
            ) as fh:
                return fh.read()
        except (UnicodeDecodeError, OSError):
            continue

    try:
        with open(
            p, "r", encoding="utf-8", errors="replace", newline=None
        ) as fh:
            return fh.read()
    except OSError:
        return None


def _intro_prompt(project_name: str) -> str:
    return (
        "Voici mon projet **%s**. Lis attentivement **tout ce qui suit** "
        "— arborescence et contenus de fichiers — et prends cela en compte "
        "pour répondre.\n\n- Réponds toujours en français.\n" % project_name
    )


def dump_repository(cfg: Config) -> str:
    gi_spec = load_gitignore(cfg.root) if cfg.respect_gitignore else None
    ignore_dirs = set(COMMON_IGNORED_DIRS).union(cfg.ignore_dirs)

    tree_text, _nb_dirs, _nb_files = build_tree(
        cfg.root, cfg.include_hidden, ignore_dirs, gi_spec
    )

    out = io.StringIO()

    project_name = cfg.root.resolve().name
    out.write(_intro_prompt(project_name))

    out.write("# Section 1 - Tree\n\n")
    out.write(FENCE + " text\n")
    out.write(tree_text)
    out.write("\n" + FENCE + "\n\n")

    out.write("# Section 2 - Files and contents\n\n")

    total_chars = out.tell()
    file_count = 0

    for p in iter_files(
        cfg.root,
        cfg.include_hidden,
        ignore_dirs,
        gi_spec,
        cfg.max_file_bytes,
        cfg.follow_symlinks,
    ):
        rel = p.relative_to(cfg.root).as_posix()
        text = read_text_safely(p)
        if text is None:
            continue

        lang = detect_lang(p) or ""
        fence = _pick_fence_for(text)

        canonical = "\n".join(_EOL_SPLIT.split(text))

        out.write("## File: %s\n" % rel)
        out.write("%s %s\n" % (fence, lang) if lang else "%s\n" % fence)
        out.write(canonical.rstrip("\n"))
        out.write("\n%s\n\n" % fence)

        file_count += 1
        total_chars = out.tell()
        if cfg.max_output_chars and total_chars > cfg.max_output_chars:
            out.write(
                "> Output truncated: --max-output-chars=%s exceeded.\n\n"
                % cfg.max_output_chars
            )
            break

    out.write("---\n\n")
    out.write(
        "Statistics: %s files exported; total length ~= %s characters.\n"
        % (file_count, total_chars)
    )
    return out.getvalue()
