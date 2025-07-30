"""共円ゲーム"""

from importlib.metadata import metadata

import fire

from .cocircular import run_game
from .feature import (
    CircularFeature,
    LineFeature,
    Point,
    get_circular_feature,
    get_feature,
    get_line_feature,
)

_package_metadata = metadata(str(__package__))
__version__ = _package_metadata["Version"]
__author__ = _package_metadata.get("Author-email", "")

__all__ = [
    "CircularFeature",
    "LineFeature",
    "Point",
    "__author__",
    "__version__",
    "get_circular_feature",
    "get_feature",
    "get_line_feature",
]


def main() -> None:
    """スクリプト実行"""
    fire.Fire(run_game)
