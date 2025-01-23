import json
import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Optional, Union

from contributors_txt.__main__ import parse_args, set_logging
from contributors_txt.const import DEFAULT_TEAM_ROLE
from contributors_txt.create_content import Alias, get_aliases


def main(args: Optional[list[str]] = None) -> None:
    parsed_args = parse_args(args)
    if parsed_args.output is None:
        parsed_args.output = parsed_args.aliases
    logging.debug("Launching normalization with %s", args)
    normalize_configuration(
        parsed_args.aliases, parsed_args.output, parsed_args.verbose
    )


def normalize_configuration(
    aliases_file: Union[Path, str], output: Union[Path, str], verbose: bool = False
) -> None:
    aliases = get_aliases(aliases_file, normalize=True)
    set_logging(verbose)
    dump_normalized_aliases(aliases, output)


def dump_normalized_aliases(aliases: list[Alias], output: Union[Path, str]) -> None:
    content = get_new_aliases(aliases)
    with open(output, "w", encoding="utf8") as f:
        json.dump(content, f, indent=4, sort_keys=True, ensure_ascii=False)


def get_new_aliases(
    aliases: list[Alias],
) -> dict[Optional[str], dict[str, Union[Sequence[str], str]]]:
    result = {}
    for alias in aliases:
        updated_alias = {
            "mails": alias.mails,
            "name": alias.name,
        }
        if alias.team != DEFAULT_TEAM_ROLE:
            updated_alias["team"] = alias.team
        if alias.comment:
            updated_alias["comment"] = alias.comment
        result[alias.authoritative_mail] = updated_alias
    return result
