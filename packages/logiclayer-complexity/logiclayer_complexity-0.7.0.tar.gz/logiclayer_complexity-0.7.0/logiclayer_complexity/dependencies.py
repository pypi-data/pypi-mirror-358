from __future__ import annotations

from collections import defaultdict
from typing import Annotated, Optional

from fastapi import Header, HTTPException, Query
from logiclayer import AuthToken, AuthTokenType

from .common import VALID_COMPARISONS, split_dict, split_list
from .structs import TopkIntent


def auth_token(
    header_auth: Annotated[Optional[str], Header(alias="authorization")] = None,
    header_jwt: Annotated[Optional[str], Header(alias="x-tesseract-jwt")] = None,
    query_token: Annotated[Optional[str], Query(alias="token")] = None,
):
    if header_jwt:
        return AuthToken(AuthTokenType.JWTOKEN, header_jwt)
    if query_token:
        return AuthToken(AuthTokenType.SEARCHPARAM, query_token)
    if header_auth:
        if header_auth.startswith("Bearer "):
            return AuthToken(AuthTokenType.JWTOKEN, header_auth[7:])
        if header_auth.startswith("Basic "):
            return AuthToken(AuthTokenType.BASIC, header_auth[6:])
        if header_auth.startswith("Digest "):
            return AuthToken(AuthTokenType.DIGEST, header_auth[7:])

    return None


def parse_alias(
    aliases: Annotated[
        list[str],
        Query(
            alias="alias",
            description="Changes the label of a Level in the response tidy data dictionaries.",
        ),
    ] = [],
):
    """Alias dependency.

    Parses the alias parameter into a dict of {Level: Alias label}.

    The parameter is a list of strings, but each item is split by comma anyway
    to ensure compatibility with URLSearchParams of both formats:
    - `alias[]=label1:alias1&alias[]=label2:alias2`
    - `alias=label1:alias1,label2:alias2`
    """
    try:
        # Note keys and values are inverted,
        # this because values must be unique for DataFrame.rename()
        parsed_alias = {label: level for level, label in split_dict(aliases, ",")}
    except ValueError:
        raise HTTPException(400, "Malformed 'alias' parameter") from None

    # keys and values are inverted back here
    alias_dict = {level: label for label, level in parsed_alias.items()}
    alias_dict.update(
        {f"{level} ID": f"{label} ID" for level, label in alias_dict.items()},
    )
    return alias_dict


def parse_cuts(
    cuts: Annotated[
        list[str],
        Query(
            description=(
                "Limits the results returned by the output. Only members of a "
                "dimension matching one of the parameters will be kept in the response."
            ),
        ),
    ] = [],
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Cuts dependency.

    Parses the cuts parameter into a dict of {Level: [Member1,...]}

    The parameter is a list of strings, but each item is split by semicolon to
    ensure compatibility with URLSearchParams of both formats:
    - `cuts[]=label1:1,2,3&cuts[]=label2:4,5,6`
    - `cuts=label1:1,2,3;label2:4,5,6`
    """
    acc = defaultdict(set)
    try:
        for key, values in split_dict(cuts, ";", ":"):
            acc[key].update(values.split(","))
    except ValueError:
        raise HTTPException(400, "Malformed 'cuts' parameter") from None

    cuts_include = {key: values for key, values in acc.items() if not key.startswith("~")}
    cuts_exclude = {key.lstrip("~"): values for key, values in acc.items() if key.startswith("~")}
    return cuts_include, cuts_exclude


def parse_filter(
    items: Annotated[
        list[str],
        Query(
            alias="filter",
            description=(
                "Limits the results returned by the output. Only members of a "
                "dimension matching one of the parameters will be kept in the response."
            ),
        ),
    ] = [],
):
    """Filter dependency.

    Parses the filter parameter into a dict of {Level: (Member IDs, ...)}.

    Each token in the parameter has the shape `Level:id1,id2...`
    """
    try:
        return {key: tuple(values.split(",")) for key, values in split_dict(items, ";")}
    except ValueError:
        raise HTTPException(400, "Malformed 'filter' parameter")


def parse_threshold_singleton(params: str):
    """Parses a threshold singleton from a string."""
    if ":" in params:
        comparison, value = params.split(":", maxsplit=1)
    else:
        comparison, value = "gte", params

    if comparison not in VALID_COMPARISONS:
        raise HTTPException(
            400,
            f"Malformed 'threshold' parameter, '{comparison}' is not a valid comparison keyword. "
            f"Accepted values are: {', '.join(VALID_COMPARISONS)}",
        )

    try:
        value = float(value)
    except ValueError:
        raise HTTPException(400, f"Malformed 'threshold' parameter, '{value}' must be numeric")

    return comparison, value


def parse_threshold(
    threshold: Annotated[
        list[str],
        Query(
            description=(
                "Restricts the data to be used in the calculation, to rows where "
                "the sum of all values through the other dimension fulfills the condition."
            ),
        ),
    ] = [],
):
    """Threshold dependency.

    Parses the threshold parameter into a dict of {Level: (Comparison, Value)}.

    The parameter is a list of strings, but each item is split by comma anyway
    to ensure compatibility with URLSearchParams of both formats:
    - `threshold[]=level1:gte:10&threshold[]=level2:lt:20`
    - `threshold=level1:gte:10;level2:lt:20`
    """
    return {
        level: parse_threshold_singleton(params) for level, params in split_dict(threshold, ";")
    }


def parse_topk(
    top: Annotated[str, Query(description=(""))] = "",
) -> Optional[TopkIntent]:
    return TopkIntent.model_validate(top) if top else None


def parse_drilldowns(
    complementary_drilldowns: Annotated[
        list[str],
        Query(
            description="Defines descriptive columns complementary to those used for the calculation base",
        ),
    ] = [],
) -> list[str]:
    return [item for item in split_list(complementary_drilldowns) if item]


def parse_measures(
    complementary_measures: Annotated[
        list[str],
        Query(description="Defines extra measures complementary to RCA"),
    ] = [],
) -> list[str]:
    return [item for item in split_list(complementary_measures) if item]


def parse_having(
    having: Annotated[
        list[str],
        Query(
            description=("filter results by measures"),
        ),
    ] = [],
):
    return {
        level: (op, float(count))
        for item in split_list(having, ";")
        for level, op, count in [item.split(".", maxsplit=2)]
    }
