# repomapper

[![builds.sr.ht status](https://builds.sr.ht/~jcdenton/repomapper.svg)](https://builds.sr.ht/~jcdenton/repomapper?)
[![License: CC0-1.0](https://img.shields.io/badge/license-CC0%201.0-blue.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

repomapper exports a source repository into a single Markdown text:  
- a tree-like view of the repository structure  
- followed by the concatenated contents of text files.  

A systematic prompt engineered introduction is added to guide LLMs (full context, answers in French).

---

## Installation

```bash
pip install repomapper
```

For development:

```bash
git clone https://git.sr.ht/~jrmsls/repomapper
cd repomapper
pip install -e .[gitignore,clipboard]
```

---

## Example usage

```bash
# Basic usage
repomapper .

# Respect .gitignore and include hidden files
repomapper . --respect-gitignore --include-hidden

# With output size limits and clipboard copy
repomapper . --max-output-chars 900000 --to-clipboard --clipboard-max-chars 700000

# Redirect output to a file
repomapper . --stdout > dump.txt
```

---

## Key features

- Systematic contextual intro.  
- Tree + file contents export.  
- Skips binary and oversized files.  
- `.gitignore` support (via pathspec).  
- Clipboard copy support (via pyperclip).  
- Configurable output limits.