import argshell
from pathier import Pathier
from printbuddies import Progress, track

from packagelister import packagelister


def get_args() -> argshell.Namespace:
    parser = argshell.ArgumentParser(
        prog="whouses",
        description=""" Determine what sub-folders in the current directory use the specified package.
        Useful for knowing which projects need to be updated when upgrading an installed package.""",
    )

    parser.add_help_preview()

    parser.add_argument(
        "package",
        type=str,
        help=""" Scan the current working directory for project folders that use this package.""",
    )

    parser.add_argument(
        "-i",
        "--ignore",
        nargs="*",
        default=[],
        type=str,
        help=""" Ignore these folders. """,
    )
    args = parser.parse_args()

    return args


def find(root: Pathier, package: str, ignore: list[str] = []) -> list[str]:
    """Find what sub-folders of `root`, excluding those in `ignore`, have files that use `package`."""
    package_users: list[str] = []
    scan_fails: dict[str, list[Pathier]] = {}  # Error message: [projects]
    projects = [
        path
        for path in track(root.iterdir(), "Scanning for projects...")
        if path.is_dir() and path.stem not in ignore
    ]
    num_projects = len(projects)
    with Progress() as prog:
        scan = prog.add_task(total=num_projects)
        for project in projects:
            prog.update(scan, suffix=f"Scanning {project.stem}...")
            try:
                if package in packagelister.scan_dir(project, True).packages.names:
                    package_users.append(project.stem)
            except Exception as e:
                err = str(e)
                if err not in scan_fails:
                    scan_fails[err] = [project]
                else:
                    scan_fails[err].append(project)
            prog.update(scan, advance=1)
    print()
    if scan_fails:
        print("The following errors occured during the scan:")
        for fail in scan_fails:
            print(f"ERROR: {fail}:")
            print(*scan_fails[fail], sep="\n")
            print()
    return package_users


def main(args: argshell.Namespace | None = None):
    if not args:
        args = get_args()
    package_users = find(
        Pathier.cwd(), args.package, [".pytest_cache", "__pycache__"] + args.ignore
    )
    print(f"The following folders have files that use `{args.package}`:")
    print(*package_users, sep="\n")


if __name__ == "__main__":
    main(get_args())
