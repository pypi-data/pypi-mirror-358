import ast
import importlib.metadata
import sys
from dataclasses import dataclass

from pathier import Pathier, Pathish
from printbuddies import track
from typing_extensions import Self
from younotyou import younotyou

# figured it's more efficient to have this on hand than calling the function everytime I need the mapping
packages_distributions = importlib.metadata.packages_distributions()
# A list of distributions for this Python install
distributions = set(
    [
        name
        for distributions in packages_distributions.values()
        for name in distributions
    ]
)


def is_builtin(package_name: str) -> bool:
    """Returns whether `package_name` is a standard library module or not."""
    return package_name in sys.stdlib_module_names


@dataclass
class Package:
    """Dataclass representing an imported package.

    #### Fields:
    * `name: str`
    * `distribution_name: str` - the name used to `pip install`, sometimes this differs from `name`
    * `version: str`
    * `builtin: bool` - whether this is a standard library package or not"""

    name: str
    distribution_name: str
    version: str
    builtin: bool

    def get_formatted_requirement(self, version_specifier: str):
        """Returns a string of the form `{self.distribution_name}{version_specifier}{self.version}`.
        e.g for this package: `"packagelister>=2.0.0"`"""
        return f"{self.distribution_name}{version_specifier}{self.version}"

    @classmethod
    def from_name(cls, package_name: str) -> Self:
        """Returns a `Package` instance from the package name.

        Will attempt to determine the other class fields."""
        distributions = packages_distributions.get(package_name)
        if distributions:
            distribution_name = distributions[0]
            version = importlib.metadata.version(distribution_name)
        else:
            distribution_name = ""
            version = ""
        return cls(package_name, distribution_name, version, is_builtin(package_name))

    @classmethod
    def from_distribution_name(cls, distribution_name: str) -> Self:
        """Returns a `Package` instance from the distribution name.

        Returned instance will have an empty `name` field.

        Raises `ValueError` if `distribution_name` isn't found in `importlib.metadata.packages_distributions()`.
        """
        if distribution_name not in distributions:
            raise ValueError(
                f"`{distribution_name}` not found in Python's installed distributions."
            )
        version = importlib.metadata.version(distribution_name)
        return cls("", distribution_name, version, False)


class PackageList(list[Package]):
    """A subclass of `list` to add convenience methods when working with a list of `packagelister.Package` objects."""

    @property
    def names(self) -> list[str]:
        """Returns a list of `Package.name` strings."""
        return [package.name for package in self]

    @property
    def distribution_names(self) -> list[str | None]:
        """Returns a list of `Package.distribution_name` strings for third party packages in this list."""
        return [package.distribution_name for package in self.third_party]

    @property
    def third_party(self) -> Self:
        """Returns a `PackageList` instance for the third party packages in this list."""
        return self.__class__(
            [
                package
                for package in self
                if not package.builtin and package.distribution_name
            ]
        )

    @property
    def builtin(self) -> Self:
        """Returns a `PackageList` instance for the standard library packages in this list."""
        return self.__class__([package for package in self if package.builtin])


@dataclass
class File:
    """Dataclass representing a scanned file and its list of imported packages.

    #### Fields:
    * `path: Pathier` - Pathier object representing the path to this file
    * `packages: packagelister.PackageList` - List of Package objects imported by this file
    """

    path: Pathier
    packages: PackageList


@dataclass
class Project:
    """Dataclass representing a directory that's had its files scanned for imports.

    #### Fields:
    * `files: list[packagelister.File]`"""

    files: list[File]

    @property
    def packages(self) -> PackageList:
        """Returns a `packagelister.PackageList` object for this instance with no duplicates."""
        packages: list[Package] = []
        for file in self.files:
            for package in file.packages:
                if package not in packages:
                    packages.append(package)
        return PackageList(sorted(packages, key=lambda p: p.name))

    @property
    def requirements(self) -> PackageList:
        """Returns a `packagelister.PackageList` object of third party packages used by this project."""
        return self.packages.third_party

    def get_formatted_requirements(
        self, version_specifier: str | None = None
    ) -> list[str]:
        """Returns a list of formatted requirements (third party packages) using `version_specifier` (`==`,`>=`, `<=`, etc.).

        If no `version_specifier` is given, the returned list will just be package names.
        """
        return [
            (
                requirement.get_formatted_requirement(version_specifier)
                if version_specifier
                else requirement.distribution_name or requirement.name
            )
            for requirement in self.requirements
        ]

    def get_files_by_package(self) -> dict[str, list[Pathier]]:
        """Returns a dictionary where the keys are package names and the values are lists of files that import the package."""
        files_by_package: dict[str, list[Pathier]] = {}
        for package in self.packages:
            for file in self.files:
                name = package.name
                if name in file.packages.names:
                    if name not in files_by_package:
                        files_by_package[name] = [file.path]
                    else:
                        files_by_package[name].append(file.path)
        return files_by_package


def get_package_names_from_source(source: str) -> list[str]:
    """Scan `source` and extract the names of imported packages/modules."""
    tree = ast.parse(source)
    packages: list[str] = []
    for node in ast.walk(tree):
        type_ = type(node)
        package: str = ""
        if type_ == ast.Import:
            package = node.names[0].name  # type: ignore
        elif type_ == ast.ImportFrom:
            package = node.module  # type: ignore
        if package:
            if "." in package:
                package = package[: package.find(".")]  # type: ignore
            packages.append(package)  # type: ignore
    return sorted(list(set(packages)))


def scan_file(file: Pathish) -> File:
    """Scan `file` for imports and return a `packagelister.File` instance."""
    file = Pathier(file) if not type(file) == Pathier else file
    source = file.read_text(encoding="utf-8")
    packages = get_package_names_from_source(source)
    used_packages = PackageList(
        [
            Package.from_name(package)
            for package in packages
            if package
            not in file.parts  # don't want to pick up modules in the scanned directory
        ]
    )
    return File(file, used_packages)


def scan_dir(path: Pathish, quiet: bool = False, excludes: list[str] = []) -> Project:
    """
    Recursively scan the given directory for `.py` files and determine their imports

    Args:
        path (Pathish): The directory to scan.
        quiet (bool, optional): Suppress progress bar. Defaults to False.
        excludes (list[str], optional): A list of wildcard patterns for files to exclude from the scan. Defaults to [].

    Returns:
        Project: Object representing the scanned project.
    """
    path = Pathier(path) if not type(path) == Pathier else path
    files = list(path.rglob("*.py"))
    if excludes:
        # Converting to relative and back to absolute
        # so that `excludes` don't need to prefixed with '*'
        files = [
            Pathier(f).absolute()
            for f in younotyou(
                (str(file.relative_to(path)) for file in files),
                exclude_patterns=excludes,
            )
        ]
    if quiet:
        project = Project([scan_file(file) for file in files])
    else:
        num_files = len(files)
        print(f"Scanning {num_files} files in {path} for imports...")
        project = Project([scan_file(file) for file in track(files, "")])
    return project
