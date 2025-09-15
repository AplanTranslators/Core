import argparse
import sys
from pathlib import Path
from typing import Type
from .tool import BaseTool


class ToolCLI:
    """A generic class for handling CLI for any BaseTool-based tool."""

    def __init__(self, tool_class: Type[BaseTool], description: str):
        self.tool_class = tool_class
        self.description = description
        self.parser = self._setup_arg_parsers()

    def _setup_arg_parsers(self) -> argparse.ArgumentParser:
        """Creates the main parser and subparsers for commands."""
        main_parser = argparse.ArgumentParser(
            description=self.description,
            formatter_class=argparse.RawTextHelpFormatter,
        )

        main_parser.add_argument(
            "-V",
            "--version",
            action="version",
            version="%(prog)s 1.0",
            help="Show program version and exit.",
        )

        subparsers = main_parser.add_subparsers(
            dest="command", required=True, help="Available commands"
        )

        # --- Subparser for the 'start' command ---
        start_parser = subparsers.add_parser(
            "start",
            help="Translate a single file.",
            description="Translate a single source file to the target model.",
        )
        start_parser.add_argument(
            "fpath", type=Path, help="Path to the source file."
        )
        start_parser.add_argument(
            "-rpath",
            "--result-path",
            type=Path,
            default=None,
            help='Path to the result folder. If not specified, a "results" folder will be created.',
        )

        # --- Subparser for the 'test' command ---
        test_parser = subparsers.add_parser(
            "test",
            help="Run tests from a list of examples.",
            description="Run translation tests using a JSON file with example paths.",
        )
        test_parser.add_argument(
            "e_path", type=Path, help="Path to the JSON file with the list of examples."
        )

        # --- Subparser for the 'regenerate' command ---
        regenerate_parser = subparsers.add_parser(
            "regenerate",
            help="Regenerate code for examples or a single file.",
            description="Regenerate code based on a list of examples or for a single file.",
        )
        regenerate_group = regenerate_parser.add_mutually_exclusive_group(required=True)
        regenerate_group.add_argument(
            "-e_path",
            "--examples-path",
            type=Path,
            help="Path to the JSON file with the list of examples to regenerate.",
        )
        regenerate_group.add_argument(
            "-fpath",
            "--file-path",
            type=Path,
            help="Path to a single source file to regenerate.",
        )

        return main_parser

    def run(self):
        """Parses arguments and runs the appropriate command."""
        if len(sys.argv) < 2:
            self.parser.print_help()
            sys.exit(1)

        args = self.parser.parse_args()
        tool = self.tool_class()

        if args.command == "start":
            tool.start(args.fpath, args.result_path)
        elif args.command == "test":
            tool.testsStart(args.e_path)
        elif args.command == "regenerate":
            if args.examples_path:
                tool.regenerationStart(examples_list_path=args.examples_path)
            elif args.file_path:
                tool.regenerationStart(path_to_file=args.file_path)