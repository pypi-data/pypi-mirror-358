from typing import List

from bluer_options.terminal import show_usage


def help_is_accessible(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@url",
            "is_accessible",
            "<url>",
        ],
        "is <url> accessible?",
        mono=mono,
    )


help_functions = {
    "is_accessible": help_is_accessible,
}
