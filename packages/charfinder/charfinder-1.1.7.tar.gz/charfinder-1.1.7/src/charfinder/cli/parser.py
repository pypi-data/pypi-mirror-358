"""CLI argument parser definition for CharFinder.

Defines the main ArgumentParser used by the CLI.

Responsibilities:
    - Define CLI arguments and options.
    - Attach custom validators (e.g. threshold_range).
    - Provide choices for color output.
    - Provide output format: json or text.
    - Attach --version.
    - Enable argcomplete tab completion.

Used by:
    cli_main.py to parse CLI arguments.

Functions:
    create_parser(): Returns the configured ArgumentParser instance.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import argparse

from charfinder.cli.args import (
    ARG_COLOR,
    ARG_DEBUG,
    ARG_EXACT_MATCH_MODE,
    ARG_FORMAT,
    ARG_FUZZY,
    ARG_FUZZY_ALGO,
    ARG_FUZZY_MATCH_MODE,
    ARG_HYBRID_AGG_FN,
    ARG_NORMALIZATION_PROFILE,
    ARG_POSITIONAL_QUERY,
    ARG_PREFER_FUZZY,
    ARG_QUERY,
    ARG_QUERY_LONG,
    ARG_SHOW_SCORE,
    ARG_THRESHOLD,
    ARG_VERBOSE,
    ARG_VERBOSE_LONG,
    ARG_VERSION,
)
from charfinder.cli.handlers import get_version
from charfinder.config.constants import (
    DEFAULT_COLOR_MODE,
    DEFAULT_EXACT_MATCH_MODE,
    DEFAULT_FUZZY_ALGO,
    DEFAULT_FUZZY_MATCH_MODE,
    DEFAULT_HYBRID_AGG_FUNC,
    DEFAULT_NORMALIZATION_PROFILE,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_SHOW_SCORE,
    DEFAULT_THRESHOLD,
    VALID_COLOR_MODES,
    VALID_EXACT_MATCH_MODES,
    VALID_FUZZY_ALGO_ALIASES,
    VALID_FUZZY_ALGO_NAMES,
    VALID_FUZZY_MATCH_MODES,
    VALID_HYBRID_AGG_FUNCS,
    VALID_NORMALIZATION_PROFILES,
    VALID_OUTPUT_FORMATS,
)
from charfinder.validators import (
    ValidateFuzzyAlgoAction,
    threshold_range,
    validate_show_score,
)

__all__ = ["create_parser"]

# ---------------------------------------------------------------------
# Parser Creation
# ---------------------------------------------------------------------


def create_parser() -> argparse.ArgumentParser:
    """
    Build and return the CLI ArgumentParser.

    Defines the following arguments:
    - query: The search query string (required positional).
    - --fuzzy: Enable fuzzy search if no exact matches.
    - --prefer-fuzzy: Include fuzzy results even if exact matches exist (hybrid mode).
    - --threshold: Fuzzy match threshold (float between 0.0 and 1.0).
    - --color: Color output mode ('auto', 'always', 'never').
    - --verbose: Enable console output.
    - --debug: Enable debug diagnostics output.
    - --fuzzy-algo: Fuzzy algorithm to use.
    - --fuzzy-match-mode: Fuzzy match mode.
    - --exact-match-mode: Exact match strategy (substring or word-subset).
    - --format: Output format (text or json).
    - --version: Show version and exit.

    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Find Unicode characters by name using substring or fuzzy search.",
        epilog="""Examples:
            charfinder heart
            charfinder heart --verbose
            charfinder heart --fuzzy --threshold 0.6
            charfinder heart --debug
            CHARFINDER_DEBUG_ENV_LOAD=1 charfinder heart
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # ---------------------------------------------------------------------
    # Positional Arguments
    # ---------------------------------------------------------------------

    parser.add_argument(
        ARG_POSITIONAL_QUERY,
        nargs="*",
        help="Search query for Unicode characters (positional).",
    )

    # Optional query
    parser.add_argument(
        ARG_QUERY,
        ARG_QUERY_LONG,
        dest="option_query",
        nargs="+",
        help="Search query for Unicode characters (alternative to positional).",
    )

    # ---------------------------------------------------------------------
    # Core Options
    # ---------------------------------------------------------------------

    parser.add_argument(
        ARG_FUZZY,
        action="store_true",
        help="Enable fuzzy search if no exact matches.",
    )

    parser.add_argument(
        ARG_PREFER_FUZZY,
        action="store_true",
        help="Include fuzzy results even if exact matches are found (hybrid mode).",
    )

    parser.add_argument(
        ARG_THRESHOLD,
        type=threshold_range,
        default=DEFAULT_THRESHOLD,
        help="Fuzzy match threshold (0.0 to 1.0).",
    )

    parser.add_argument(
        ARG_COLOR,
        choices=VALID_COLOR_MODES,
        default=None,
        help=f"Control color output.Default: {DEFAULT_COLOR_MODE}.",
    )

    parser.add_argument(
        ARG_VERBOSE,
        ARG_VERBOSE_LONG,
        dest="verbose",
        action="store_true",
        default=False,
        help="Enable console output (stdout/stderr). Default is off.",
    )

    parser.add_argument(
        ARG_DEBUG,
        action="store_true",
        help="Enable debug diagnostics output.",
    )

    # ---------------------------------------------------------------------
    # Matching Options
    # ---------------------------------------------------------------------

    parser.add_argument(
        f"--{ARG_EXACT_MATCH_MODE.replace('_', '-')}",
        choices=VALID_EXACT_MATCH_MODES,
        default=DEFAULT_EXACT_MATCH_MODE,
        help=(
            "How to perform exact matching when --fuzzy is not enabled.\n"
            "\t substring: Match query string as a substring of the character name.\n"
            "\t word-subset (default): Match if all words in the query appear "
            "in the character name order-independent."
        ),
    )

    parser.add_argument(
        ARG_FUZZY_ALGO,
        dest="fuzzy_algo",
        action=ValidateFuzzyAlgoAction,
        default=DEFAULT_FUZZY_ALGO,
        help=(
            "Fuzzy matching algorithm to use (case-insensitive).\n"
            f"\t Options: {', '.join(sorted(VALID_FUZZY_ALGO_NAMES))}.\n"
            f"\t Aliases: {','.join(sorted(VALID_FUZZY_ALGO_ALIASES))}.\n"
            f"\t Default: {DEFAULT_FUZZY_ALGO}."
        ),
    )

    parser.add_argument(
        f"--{ARG_FUZZY_MATCH_MODE.replace('_', '-')}",
        choices=VALID_FUZZY_MATCH_MODES,
        default=DEFAULT_FUZZY_MATCH_MODE,
        help=(
            "Fuzzy match mode when --fuzzy is enabled.\n"
            "\t single : Uses algo determined by --fuzzy-algo.\n"
            "\t hybrid (default): Weighted aggregation of mutiple algorithms.\n"
        ),
    )

    parser.add_argument(
        ARG_HYBRID_AGG_FN,
        choices=VALID_HYBRID_AGG_FUNCS,
        default=DEFAULT_HYBRID_AGG_FUNC,
        help=f"Aggregation function for hybrid match mode (default: {DEFAULT_HYBRID_AGG_FUNC}).",
    )
    # ---------------------------------------------------------------------
    # Normalization Options
    # ---------------------------------------------------------------------

    parser.add_argument(
        ARG_NORMALIZATION_PROFILE,
        choices=VALID_NORMALIZATION_PROFILES,
        default=None,
        help=(
            "Character normalization profile to apply before matching.\n"
            "\t Options: raw, light, medium, aggressive. "
            f"\t Default: {DEFAULT_NORMALIZATION_PROFILE}."
        ),
    )

    # ---------------------------------------------------------------------
    # Output Options
    # ---------------------------------------------------------------------

    parser.add_argument(
        ARG_FORMAT,
        choices=VALID_OUTPUT_FORMATS,
        default=DEFAULT_OUTPUT_FORMAT,
        help=(
            "Output format:\n"
            "\t'text' for human-friendly table (default), 'json' for structured output.\n"
            "\t Default: {DEFAULT_OUTPUT_FORMAT}"
        ),
    )

    # Enable argcomplete
    try:
        import argcomplete  # noqa: PLC0415

        argcomplete.autocomplete(parser)
    except ImportError:
        pass

    parser.add_argument(
        ARG_SHOW_SCORE,
        type=validate_show_score,
        default=None,
        help=(
            "Whether to show similarity scores for fuzzy matches.\n"
            "\t Accepts: true, false, 1, 0, yes, no (case-insensitive).\n"
            f"\t Default: {DEFAULT_SHOW_SCORE}."
        ),
    )

    # ---------------------------------------------------------------------
    # Version Option
    # ---------------------------------------------------------------------

    parser.add_argument(
        ARG_VERSION,
        action="version",
        version=get_version(),
    )

    return parser
