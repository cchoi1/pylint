"""
Create a file listing the contributors of a git repository.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional, Union

from contributors_txt.const import DEFAULT_CONTRIBUTOR_PATH
from contributors_txt.create_content import (
    create_content,
    get_aliases,
    get_shortlog_output,
)
from contributors_txt.update_content import update_content


def main(args: Optional[list[str]] = None) -> None:
    parsed_args = parse_args(args)
    create_contributors_txt(
        parsed_args.aliases, parsed_args.output, parsed_args.verbose
    )


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(__doc__)
    add_default_arguments(parser)
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_CONTRIBUTOR_PATH),
        help="Where to output the contributor list",
    )
    parsed_args: argparse.Namespace = parser.parse_args(args)
    return parsed_args


def add_default_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-a",
        "--aliases",
        default=None,
        help="The path to the aliases file.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Display logging messages",
    )


def set_logging(verbose: bool) -> None:
    if verbose:
        logging.basicConfig(level=logging.DEBUG)


def create_contributors_txt(
    aliases_file: Union[Path, str], output: Union[Path, str], verbose: bool = False
) -> None:
    set_logging(verbose)
    aliases = get_aliases(aliases_file)
    shortlog_output = get_shortlog_output()
    if Path(output).is_file():
        content = update_content(output, aliases, shortlog_output, str(aliases_file))
    else:
        content = create_content(aliases, shortlog_output, str(aliases_file))
    with open(output, "w", encoding="utf8") as f:
        f.write(content)


if __name__ == "__main__":
    main()
