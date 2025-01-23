import argparse
import json
import logging
import re
from pathlib import Path
from typing import Optional

from contributors_txt.__main__ import add_default_arguments, set_logging
from contributors_txt.const import DEFAULT_CONTRIBUTOR_PATH, DEFAULT_TEAM_ROLE
from contributors_txt.create_content import Alias
from contributors_txt.normalize import dump_normalized_aliases

THE_REGEX = re.compile(
    r"(?P<name>[\w\-\. ()'\",]+)<(?P<mail>[\w\.@+\- ]+)>(?P<comment>.*)", re.DOTALL
)


def main(args: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(__doc__)
    add_default_arguments(parser)
    parser.add_argument(
        "input",
        default=str(DEFAULT_CONTRIBUTOR_PATH),
        help="The existing CONTRIBUTORS.txt",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_CONTRIBUTOR_PATH),
        help="Where to output the contributor aliases",
    )
    parsed_args: argparse.Namespace = parser.parse_args(args)
    set_logging(parsed_args.verbose)
    logging.debug("Launching comment extraction with %s", parsed_args)
    extract_comment(
        Path(parsed_args.input), Path(parsed_args.aliases), Path(parsed_args.output)
    )


def extract_comment(input_path: Path, aliases_path: Path, output_path: Path) -> None:
    inputs = _get_input_to_parse(input_path)
    aliases = _get_aliases(aliases_path)
    for input_ in inputs:
        authoritative_mail = input_["mail"]
        old_alias = aliases.get(authoritative_mail)
        new_alias = _get_new_alias(authoritative_mail, old_alias, input_)
        if (
            old_alias is not None
            or new_alias.comment
            or new_alias.team != DEFAULT_TEAM_ROLE
        ):
            aliases[authoritative_mail] = new_alias
    dump_normalized_aliases(list(aliases.values()), output_path)


def _get_new_alias(
    authoritative_mail: str, old_alias: Optional[Alias], input_: dict[str, str]
) -> Alias:
    comment = input_.get("comment", "")
    if old_alias is None:
        name_ = input_["name"].rstrip(" ")
        return Alias(
            authoritative_mail=authoritative_mail,
            mails=[authoritative_mail],
            name=name_,
            team=DEFAULT_TEAM_ROLE,
            comment=comment,
        )
    if old_alias.comment and comment:
        raise ValueError(
            f"Choose between {old_alias.comment} and {comment} for {authoritative_mail}"
        )
    if comment:
        return Alias(
            authoritative_mail=old_alias.authoritative_mail,
            mails=old_alias.mails,
            name=old_alias.name,
            team=old_alias.team,
            comment=comment,
        )
    return old_alias


def _get_input_to_parse(input_path: Path) -> list[dict[str, str]]:
    with open(input_path, encoding="utf8") as f:
        inputs = f.read()
    results = []
    for input_ in inputs.split("\n- "):
        match = THE_REGEX.match(input_)
        if match is None:
            logging.warning("Did not match the expected pattern in %s", input_)
        else:
            result = match.groupdict()
            results.append(result)
    return results


def _get_aliases(aliases_path: Path) -> dict[str, Alias]:
    with open(aliases_path, encoding="utf8") as f:
        aliases_raw = json.load(f)
    aliases: dict[str, Alias] = {}
    for mail, info in aliases_raw.items():
        mails: list[str] = info.get("mails")
        name: str = info.get("name")
        team: str = info.get("team", DEFAULT_TEAM_ROLE)
        aliases[mail] = Alias(
            authoritative_mail=mail, mails=mails, name=name, team=team
        )
    return aliases
