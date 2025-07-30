# Multi-Line Replacer (`mlr`)

*Copyright 2025 Caleb Evans*  
*Released under the MIT license*

[![tests](https://github.com/caleb531/multi-line-replacer/actions/workflows/tests.yml/badge.svg)](https://github.com/caleb531/multi-line-replacer/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/caleb531/multi-line-replacer/badge.svg?branch=main)](https://coveralls.io/r/caleb531/multi-line-replacer?branch=main)

Multi-Line Replacer is a CLI utility for replacing multi-line hunks of strings
across one or more files. Matching is mostly textual, but wildcard matching is
supported, and replacements are indentation-aware.

## Usage

The workflow takes one or more files on which to run replacements, and then a
series of "replacement rule" files with the `-r` flag:

```sh
mlr .github/workflows/*.yml -r example-rules/uv-gha.md
```

Each replacement rule must be a Markdown file with one or more pairs of GFM
fenced code blocks ([see documentation][gfm-docs]). Every odd code block
represents the target text to replace, and every even code block represents the
textual replacement. All other Markdown formatting is ignored, so feel free to
add headings, explainer text, or anything else!

````md
This rule replaces flake8 with ruff in a Github Actions linting workflow.

## flake8

```yml
- name: Run flake8
  run: flake8 MATCH_UNTIL_END_OF_LINE
```

## ruff

```yml
- name: Run ruff
  run: |
    uv run ruff check .
    uv run ruff format --check .
```
````

> [!NOTE]
The language specifier at the start of each code fence is ignored by the
utility. Still, it is highly recommended to specify so that syntax highlighting
is enabled in your editor (i.e. it's for you, not the tool).

### Wildcard Matching

There are two special wildcard variables:

- `MATCH_UNTIL_END_OF_LINE` (`[^\n]*`)
- `MATCH_ALL_BETWEEN` (`[^\n]*?`)

These variables can be used anywhere in any code block representing the target
text to match. Because these names are unique enough, word boundaries are not
required around them (e.g. `vMATCH_UNTIL_END_OF_LINE` is allowed).

### More Examples

To better understand the expected rules format and what's allowed, please see
the `example-rules` directory.

[gfm-docs]: https://github.github.com/gfm/#fenced-code-blocks

## About

Multi-Line Replacer was built as my solution to an intermediate need I had while
writing a large migration script. I had 17 Python projects using old tooling,
and the script was written to migrate these projects to [uv][uv] and
[ruff][ruff].

Part of this migration process necessitated performing textual replacements on
multi-line hunks of code. Regular expressions and editors like VS Code could
somewhat achieve this, although they required escaping special characters and
carefully specifying indentation. In other words, those tools proved to be too
rigid and inflexible.

Given these constraints, I conceived of a utility that could perform multi-line
replacements with a friendlier authoring experience and greater indentation
awareness. The implementation took several iterations to achieve positive
results, but by the end, it contributed significantly to the successful
migration of all 17 projects. From there, I decided to release it to the world
as a more flexible and automated system for replacing multi-line hunks of code.

[uv]: https://docs.astral.sh/uv/
[ruff]: https://docs.astral.sh/ruff/
