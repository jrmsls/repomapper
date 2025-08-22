import os
import sys
from pathlib import Path

import pytest

from repomapper.config import Config
from repomapper.dump import dump_repository


def _section_two(text: str) -> str:
    """
    Return only the 'Section 2 - Files and contents' slice of the dump.
    """
    marker = "# Section 2 - Files and contents"
    i = text.find(marker)
    return text[i:] if i != -1 else ""


def test_smoke_basic(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "b.py").write_text("print('x')", encoding="utf-8")

    cfg = Config(root=tmp_path, stdout=True)
    text = dump_repository(cfg)

    assert "Section 1" in text
    assert "Section 2" in text
    assert "a.txt" in text
    assert "b.py" in text
    # Fence and file contents present
    assert "```" in text
    assert "hello" in text
    assert "print('x')" in text


def test_tree_output(tmp_path: Path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "f.py").write_text("print(123)", encoding="utf-8")

    cfg = Config(root=tmp_path, stdout=True)
    text = dump_repository(cfg)

    # Directory and file should appear in the tree section
    assert "pkg/" in text
    assert "f.py" in text


def test_binary_skipped(tmp_path: Path):
    # Contains NUL byte -> treated as probably binary (content skipped)
    (tmp_path / "file.bin").write_bytes(b"\x00\x01\x02\x03")

    cfg = Config(root=tmp_path, stdout=True)
    text = dump_repository(cfg)

    # It may appear in the tree (Section 1) but must not be exported in Section 2
    section2 = _section_two(text)
    assert "file.bin" not in section2


def test_max_file_bytes(tmp_path: Path):
    big = tmp_path / "big.txt"
    big.write_text("x" * 5000, encoding="utf-8")

    cfg = Config(root=tmp_path, stdout=True, max_file_bytes=1000)
    text = dump_repository(cfg)

    # It may appear in the tree (Section 1) but must not be exported in Section 2
    section2 = _section_two(text)
    assert "big.txt" not in section2


def test_max_output_chars_truncates(tmp_path: Path):
    (tmp_path / "a.txt").write_text("y" * 5000, encoding="utf-8")

    cfg = Config(root=tmp_path, stdout=True, max_output_chars=1000)
    text = dump_repository(cfg)

    assert "> Output truncated:" in text


def test_hidden_files_excluded_by_default(tmp_path: Path):
    (tmp_path / ".hidden.txt").write_text("secret", encoding="utf-8")
    (tmp_path / ".hidden_dir").mkdir()
    (tmp_path / ".hidden_dir" / "x.txt").write_text("xx", encoding="utf-8")

    cfg = Config(root=tmp_path, stdout=True)
    text = dump_repository(cfg)

    section2 = _section_two(text)
    assert ".hidden.txt" not in text  # not in tree
    assert ".hidden_dir" not in text  # not in tree
    assert "x.txt" not in text
    assert ".hidden.txt" not in section2
    assert "x.txt" not in section2


def test_hidden_files_included_when_flag(tmp_path: Path):
    (tmp_path / ".hidden.txt").write_text("secret", encoding="utf-8")

    cfg = Config(root=tmp_path, stdout=True, include_hidden=True)
    text = dump_repository(cfg)

    assert ".hidden.txt" in text
    section2 = _section_two(text)
    assert ".hidden.txt" in section2
    assert "secret" in section2


def test_gitignore_respected(tmp_path: Path):
    pytest.importorskip("pathspec")

    (tmp_path / ".gitignore").write_text(
        "ignored.txt\nsubdir/\n", encoding="utf-8"
    )
    (tmp_path / "ignored.txt").write_text("secret", encoding="utf-8")
    (tmp_path / "kept.txt").write_text("keep", encoding="utf-8")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "a.txt").write_text(
        "should be ignored", encoding="utf-8"
    )

    cfg = Config(root=tmp_path, stdout=True, respect_gitignore=True)
    text = dump_repository(cfg)

    assert "ignored.txt" not in text
    assert "subdir/" not in text
    assert "a.txt" not in text
    assert "kept.txt" in text
    section2 = _section_two(text)
    assert "kept.txt" in section2
    assert "keep" in section2


@pytest.mark.skipif(
    sys.platform.startswith("win"), reason="symlink permissions"
)
def test_symlink_not_followed_by_default(tmp_path: Path):
    target = tmp_path / "real.txt"
    target.write_text("real", encoding="utf-8")
    link = tmp_path / "link.txt"
    os.symlink(target, link)

    cfg = Config(root=tmp_path, stdout=True, follow_symlinks=False)
    text = dump_repository(cfg)

    # real file included, symlink skipped (in tree and section 2)
    assert "real.txt" in text
    assert "link.txt" not in text
    section2 = _section_two(text)
    assert "real.txt" in section2
    assert "link.txt" not in section2


@pytest.mark.skipif(
    sys.platform.startswith("win"), reason="symlink permissions"
)
def test_symlink_followed_when_enabled(tmp_path: Path):
    target = tmp_path / "real.txt"
    target.write_text("real", encoding="utf-8")
    link = tmp_path / "link.txt"
    os.symlink(target, link)

    cfg = Config(root=tmp_path, stdout=True, follow_symlinks=True)
    text = dump_repository(cfg)

    assert "real.txt" in text
    assert "link.txt" in text
    section2 = _section_two(text)
    assert "link.txt" in section2
    assert "real" in section2
