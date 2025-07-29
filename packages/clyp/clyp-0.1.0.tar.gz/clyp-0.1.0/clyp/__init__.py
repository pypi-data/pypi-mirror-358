# This package provides the clyp (curly language yielding python) programming language,
# which is designed to be a simple and intuitive way to write Python code using static typing and curly braces.
import typeguard

__all__ = ['Version', '__version__']


@typeguard.typechecked
class Version:
    """
    Represents the version of the clyp package.
    This class is used to store and retrieve the version information.
    """

    def __init__(self, major: int, minor: int, patch: int):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


__version__: Version = Version(0, 1, 0)