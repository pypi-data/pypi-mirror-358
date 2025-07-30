#!/usr/bin/env python3.13

import argparse

from mlr.core import ExpandedPath, extract_code_blocks, replace_text


def pluralize(singular, plural, count):
    """
    Return "1 <singular>" or "<count> <plural>", where the noun is either in
    singular or plural form depending on the supplied count
    """
    if count == 1:
        return f"{count} {singular}"
    else:
        return f"{count} {plural}"


def get_cli_args():
    """Define and parse CLI arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_paths",
        metavar="INPUT_FILE",
        nargs="+",
        type=ExpandedPath,
        help="One or more paths to files to apply replacements to.",
    )
    parser.add_argument(
        "-r",
        "--rules",
        metavar="RULE_FILE",
        dest="rule_paths",
        nargs="+",
        required=True,
        type=ExpandedPath,
        help="One or more paths to replacement rule Markdown files. Each file should contain pairs of triple-backtick (```) fenced code blocks, where the first fenced block is the text to be replaced and the second fenced block is the replacement text.",  # noqa: E501
    )
    return parser.parse_args()


def main():
    """The entry point for the `multi-line-replacer` / `mlr` CLI program"""
    args = get_cli_args()
    total_replacement_count = 0
    total_files_changed = 0
    for input_path in args.input_paths:
        input_text = input_path.read_text()
        # Apply each replacement rule to each input file
        for rule_path in args.rule_paths:
            rule_text = rule_path.read_text()
            code_blocks = extract_code_blocks(rule_text)
            # Enumerate fenced code blocks in pairs to get each pair of
            # target/replacement rules
            for target_text, replacement_text in zip(
                code_blocks[0::2], code_blocks[1::2]
            ):
                input_text, replacement_count = replace_text(
                    input_text, target_text, replacement_text
                )
                total_replacement_count += replacement_count
        if replacement_count:
            total_files_changed += 1
        input_path.write_text(input_text)
        if total_files_changed:
            print(
                f"{pluralize('file', 'files', total_files_changed)} changed ({pluralize('replacement', 'replacements', total_replacement_count)}), {pluralize('file', 'files', len(args.input_paths) - total_files_changed)} unchanged"  # noqa: E501
            )
        else:
            print(
                f"{pluralize('file', 'files', len(args.input_paths) - total_files_changed)} unchanged (no replacements made)"  # noqa: E501
            )


if __name__ == "__main__":
    main()
