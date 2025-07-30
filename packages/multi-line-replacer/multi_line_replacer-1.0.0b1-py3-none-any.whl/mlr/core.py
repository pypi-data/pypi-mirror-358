#!/usr/bin/env python3.13
import os
import re
import sys
from pathlib import PosixPath, WindowsPath

# Detect proper Path subclass to inherit from based on the user's platform,
# since the top-level Path subclass is not designed to be subclassed directly
BasePath = WindowsPath if sys.platform == "win32" else PosixPath


class ExpandedPath(BasePath):
    """
    Path subclass that automatically expands the user' home directory (i.e. ~)
    """

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, os.path.expanduser(*args), **kwargs)


def extract_code_blocks(md_text):
    """Extract fenced code blocks from the given Markdown text"""
    code_blocks = re.findall(
        r"```(?:[\w\-]*)\n(.*?)\n```",
        md_text,
        flags=re.DOTALL,
    )
    # If number of code blocks is not even
    if len(code_blocks) % 2 != 0:
        raise RuntimeError(
            "Replacement file must have an even number of fenced code blocks."
        )
    return code_blocks


def get_indent_unit(text):
    """
    Find the string representing the base unit of indentation in a given string
    of text; this can be either two spaces, four spaces, or a tab character.
    """
    for indent_level in ((" " * 2), (" " * 4), "\t"):
        # The positive lookahead is because since 2-space indent is really a
        # subset of 4-space indent, we need to be able to distinguish between
        # the two, so we check to see if there
        if re.search(rf"^{indent_level}(?=\S)", text, flags=re.MULTILINE):
            return indent_level
    return None


def evaluate_wildcard_variables(text):
    """
    Evaluate textual wildcard variables in the given target text to achieve
    certain behaviors (like wildcard-matching through the end of a line, or a
    wildcard-match for only a single word)
    """
    wildcard_evaluations = {
        # Match all non-newline characters until the end of the line is reached
        "MATCH_UNTIL_END_OF_LINE": r"[^\n]*",
        # Match all non-newline characters between two delimiters (like quotes)
        "MATCH_ALL_BETWEEN": r"[^\n]*?",
    }
    for wildcard_var_name, replacement in wildcard_evaluations.items():
        text = re.sub(
            re.escape(wildcard_var_name),
            replacement,
            text,
        )
    return text


def replace_text(input_text, target_text, replacement_text):
    """
    Replace the given text in the input text with the replacement text,
    preserving indentation
    """
    replace_this_patt = "\n".join(
        (
            # Evaluate special wildcard variables like
            # MATCH_UNTIL_END_OF_LINE
            evaluate_wildcard_variables(rf"([ \t]*){re.escape(line.strip())}")
            if line
            else ""
        )
        for line in target_text.splitlines()
    )
    # Retrieve the base indentation level in the target text to ensure that the
    # replacement text is indented the same amount
    base_indent_matches = re.search(replace_this_patt, input_text)
    if not base_indent_matches:
        return input_text, 0
    base_indent_level = base_indent_matches.group(1)
    # Ensure that the replacement text's preferred indentation unit matches that
    # of the input text
    replacement_indent_unit = get_indent_unit(replacement_text)
    if replacement_indent_unit:
        replacement_text = re.sub(
            replacement_indent_unit,
            get_indent_unit(input_text),
            replacement_text,
        )
    # Ensure that the replacement text is indented to the same amount as the
    # target text it is replacing
    replacement_text = "\n".join(
        # The ternary syntax is to prevent trailing whitespace from being added
        # to blank lines
        base_indent_level + line if line else ""
        for line in replacement_text.splitlines()
    )
    return re.subn(replace_this_patt, replacement_text, input_text)
