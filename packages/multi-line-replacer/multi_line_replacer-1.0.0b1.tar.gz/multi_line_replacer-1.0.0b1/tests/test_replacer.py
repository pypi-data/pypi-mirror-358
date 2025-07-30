#!/usr/bin/env python3

from tests.utils import MLRTestCase


class TestMLR(MLRTestCase):
    """Test all multi-line-replacer (mlr) functionality"""

    def test_literal_replacement(self):
        """Should perform a literal textual replacement"""
        self.assert_file_replace(
            input_filenames=["input/test.editorconfig"],
            rule_filenames=["rules/editorconfig.md"],
            output_filenames=["output/test.editorconfig"],
            expected_cli_message="1 file changed (1 replacement), 0 files unchanged",
        )

    def test_literal_target_misindented(self):
        """
        Should perform a literal textual replacement even if target text is
        misindented
        """
        self.assert_file_replace(
            input_filenames=["input/test.editorconfig"],
            rule_filenames=["rules/editorconfig-misindented.md"],
            output_filenames=["output/test.editorconfig"],
            expected_cli_message="1 file changed (1 replacement), 0 files unchanged",
        )

    def test_match_until_end_of_line(self):
        """Should perform a replacement with MATCH_UNTIL_END_OF_LINE"""
        self.assert_file_replace(
            input_filenames=["input/lint.yml"],
            rule_filenames=["rules/ruff.md"],
            output_filenames=["output/lint-ruff.yml"],
            expected_cli_message="1 file changed (1 replacement), 0 files unchanged",
        )

    def test_match_all_between(self):
        """Should perform a replacement with MATCH_ALL_BETWEEN"""
        self.assert_file_replace(
            input_filenames=["input/lint.yml"],
            rule_filenames=["rules/python-version.md"],
            output_filenames=["output/lint-python-version.yml"],
            expected_cli_message="1 file changed (1 replacement), 0 files unchanged",
        )

    def test_normalize_indent_unit_in_replacement(self):
        """
        Should normalize indent unit in replacement to match indent unit of
        input text
        """
        self.assert_file_replace(
            input_filenames=["input/lint.yml"],
            rule_filenames=["rules/ruff-tab-indent.md"],
            output_filenames=["output/lint-ruff.yml"],
            expected_cli_message="1 file changed (1 replacement), 0 files unchanged",
        )

    def test_no_match(self):
        """
        Should leave the file untouched if no matches are found
        """
        self.assert_file_replace(
            input_filenames=["input/publish.yml"],
            rule_filenames=["rules/ruff.md"],
            output_filenames=["input/publish.yml"],
            expected_cli_message="1 file unchanged (no replacements made)",
        )

    def test_missing_code_blocks(self):
        """
        Should raise a RuntimeError if there are an odd number of code blocks
        """
        with self.assertRaises(RuntimeError):
            self.assert_file_replace(
                input_filenames=["input/publish.yml"],
                rule_filenames=["rules/missing-code-blocks.md"],
                output_filenames=["input/publish.yml"],
            )
