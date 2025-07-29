from typing import Annotated, Dict, List, Optional, Set, Tuple

from fastapi import Depends, Query

from logiclayer_complexity.dependencies import (
    parse_cuts,
    parse_drilldowns,
    parse_having,
    parse_measures,
    parse_threshold,
)

from .structs import RcaHistoricalParameters, RcaParameters, RcaSubnationalParameters


def prepare_rca_params(
    cube: Annotated[
        str,
        Query(
            description="The cube to retrieve the main data",
        ),
    ],
    activity: Annotated[
        str,
        Query(
            description="Productivity categories for the RCA calculation",
        ),
    ],
    location: Annotated[
        str,
        Query(
            description="Geographical categories for the RCA calculation",
        ),
    ],
    measure: Annotated[
        str,
        Query(
            description="Values to use for the RCA calculations",
        ),
    ],
    cuts: Tuple[Dict[str, Set[str]], Dict[str, Set[str]]] = Depends(parse_cuts),
    locale: Annotated[
        Optional[str],
        Query(description="Defines the locale variation for the labels in the data"),
    ] = None,
    parents: Annotated[
        bool,
        Query(
            description="Specifies if the response items should include the "
            "parent levels for activity and location.",
        ),
    ] = False,
    threshold: Dict[str, Tuple[str, int]] = Depends(parse_threshold),
    ascending: Annotated[
        Optional[bool],
        Query(
            description=(
                "Outputs the results in ascending or descending order. "
                "If not defined, results will be returned sorted by level member."
            ),
        ),
    ] = None,
    rank: Annotated[
        bool,
        Query(
            description=(
                "Adds a 'Ranking' column to the data. "
                "This value represents the index in the whole result list, sorted by value."
            ),
        ),
    ] = False,
):
    cuts_include, cuts_exclude = cuts
    return RcaParameters(
        cube=cube,
        activity=activity,
        location=location,
        measure=measure,
        cuts_include=cuts_include,
        cuts_exclude=cuts_exclude,
        locale=locale,
        parents=parents,
        threshold=threshold,
        rank=rank,
        sort_ascending=ascending,
    )


def prepare_subnatrca_global_params(
    cube: Annotated[
        str,
        Query(
            alias="global_cube",
            description="The cube to retrieve the global data",
        ),
    ],
    activity: Annotated[
        str,
        Query(
            alias="global_activity",
            description="Productivity categories for the RCA calculation",
        ),
    ],
    location: Annotated[
        str,
        Query(
            alias="global_location",
            description="Geographical categories for the RCA calculation",
        ),
    ],
    measure: Annotated[
        str,
        Query(
            alias="global_measure",
            description="Measurement to use for the RCA calculations",
        ),
    ],
    cuts: Annotated[
        List[str],
        Query(
            alias="global_cuts",
            description=(
                "Limits the results returned by the output. Only members of a "
                "dimension matching one of the parameters will be kept in the response."
            ),
        ),
    ] = [],
    locale: Annotated[
        Optional[str],
        Query(description="Locale for the labels in the data"),
    ] = None,
    threshold: Annotated[
        List[str],
        Query(
            alias="global_threshold",
            description="Restricts the data to be used in the calculation, "
            "to rows where the sum of all values through the other dimension "
            "fulfills the condition.",
        ),
    ] = [],
):
    cuts_include, cuts_exclude = parse_cuts(cuts)
    return RcaParameters(
        cube=cube,
        activity=activity,
        location=location,
        measure=measure,
        cuts_include=cuts_include,
        cuts_exclude=cuts_exclude,
        locale=locale,
        threshold=parse_threshold(threshold),
    )


def prepare_subnatrca_subnat_params(
    cube: Annotated[
        str,
        Query(
            alias="subnat_cube",
            description="The cube to retrieve the main data",
        ),
    ],
    activity: Annotated[
        str,
        Query(
            alias="subnat_activity",
            description="Productivity categories for the RCA calculation",
        ),
    ],
    location: Annotated[
        str,
        Query(
            alias="subnat_location",
            description="Geographical categories for the RCA calculation",
        ),
    ],
    measure: Annotated[
        str,
        Query(
            alias="subnat_measure",
            description="Measurement to use for the RCA calculations",
        ),
    ],
    cuts: Annotated[
        List[str],
        Query(
            alias="subnat_cuts",
            description=(
                "Limits the results returned by the output. Only members of a "
                "dimension matching one of the parameters will be kept in the response."
            ),
        ),
    ] = [],
    locale: Annotated[
        Optional[str],
        Query(description="Locale for the labels in the data"),
    ] = None,
    parents: Annotated[
        bool,
        Query(
            description="Specifies if the response items should include the "
            "parent levels for activity and location.",
        ),
    ] = False,
    threshold: Annotated[
        List[str],
        Query(
            alias="subnat_threshold",
            description=(
                "Restricts the data to be used in the calculation, to rows where "
                "the sum of all values through the other dimension fulfills the condition."
            ),
        ),
    ] = [],
):
    cuts_include, cuts_exclude = parse_cuts(cuts)
    return RcaParameters(
        cube=cube,
        activity=activity,
        location=location,
        measure=measure,
        cuts_include=cuts_include,
        cuts_exclude=cuts_exclude,
        locale=locale,
        parents=parents,
        threshold=parse_threshold(threshold),
    )


def prepare_subnatrca_params(
    subnat_params: RcaParameters = Depends(prepare_subnatrca_subnat_params),
    global_params: RcaParameters = Depends(prepare_subnatrca_global_params),
    ascending: Annotated[
        Optional[bool],
        Query(
            description=(
                "Outputs the results in ascending or descending order. "
                "If not defined, results will be returned sorted by level member."
            ),
        ),
    ] = None,
    rank: Annotated[
        bool,
        Query(
            description=(
                "Adds a 'Ranking' column to the data. "
                "This value represents the index in the whole result list, sorted by value."
            ),
        ),
    ] = False,
):
    return RcaSubnationalParameters(
        global_params=global_params,
        subnat_params=subnat_params,
        rank=rank,
        sort_ascending=ascending,
    )


def prepare_historicalrca_params(
    cube: Annotated[
        str,
        Query(
            description="The cube to retrieve the main data",
        ),
    ],
    activity: Annotated[
        str,
        Query(
            description="Productivity categories for the RCA calculation",
        ),
    ],
    location: Annotated[
        str,
        Query(
            description="Geographical categories for the RCA calculation",
        ),
    ],
    time: Annotated[
        str,
        Query(
            description="Unit of time used for calculations",
        ),
    ],
    measure: Annotated[
        str,
        Query(
            description="Values to use for the RCA calculations",
        ),
    ],
    cuts: Tuple[Dict[str, Set[str]], Dict[str, Set[str]]] = Depends(parse_cuts),
    locale: Annotated[
        Optional[str],
        Query(description="Defines the locale variation for the labels in the data"),
    ] = None,
    time_filter: Annotated[
        Optional[str],
        Query(description="parameter similar to time.latest of tesseract python"),
    ] = None,
    properties: Annotated[
        Optional[list[str]],
        Query(description="properties of the original cube"),
    ] = None,
    complementary_drilldowns: list[str] = Depends(parse_drilldowns),
    complementary_measures: list[str] = Depends(parse_measures),
    parents: Annotated[
        bool,
        Query(
            description="Specifies if the response items should include the "
            "parent levels for activity and location.",
        ),
    ] = False,
    threshold: Dict[str, Tuple[str, int]] = Depends(parse_threshold),
    ascending: Annotated[
        Optional[bool],
        Query(
            description=(
                "Outputs the results in ascending or descending order. "
                "If not defined, results will be returned sorted by level member."
            ),
        ),
    ] = None,
    rank: Annotated[
        bool,
        Query(
            description=(
                "Adds a 'Ranking' column to the data. "
                "This value represents the index in the whole result list, sorted by value."
            ),
        ),
    ] = False,
    having: dict[str, tuple[str, float]] = Depends(parse_having),
):
    cuts_include, cuts_exclude = cuts
    return RcaHistoricalParameters(
        cube=cube,
        activity=activity,
        location=location,
        measure=measure,
        time=time,
        cuts_include=cuts_include,
        cuts_exclude=cuts_exclude,
        locale=locale,
        time_filter=time_filter,
        properties=properties,
        complementary_drilldowns=complementary_drilldowns,
        complementary_measures=complementary_measures,
        parents=parents,
        threshold=threshold,
        having=having,
        rank=rank,
        sort_ascending=ascending,
    )
