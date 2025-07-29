import argshell
from pathier import Pathier

from packagelister import packagelister


def get_args() -> argshell.Namespace:
    parser = argshell.ArgumentParser(
        prog="packagelister",
        description=""" Scan the current directory for imported packages. """,
    )
    parser.add_help_preview()

    parser.add_argument(
        "-f",
        "--files",
        action="store_true",
        help=""" Show which files imported each of the packages. """,
    )

    parser.add_argument(
        "-g",
        "--generate_requirements",
        action="store_true",
        help=""" Generate a requirements.txt file in the current directory. """,
    )

    parser.add_argument(
        "-v",
        "--versions",
        type=str,
        default=None,
        choices=["==", "<", "<=", ">", ">=", "~="],
        help=""" When generating a requirements.txt file, include the versions of the packages using this relation.
            (You may need to put quotes around some of the options.)""",
    )

    parser.add_argument(
        "-b",
        "--builtins",
        action="store_true",
        help=""" Include built in standard library modules in terminal display. """,
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help=""" Print the Package objects found during the scan. """,
    )

    parser.add_argument(
        "-e",
        "--exclude",
        nargs="*",
        type=str,
        default=[],
        help=""" Wildcard patterns to exclude from scan.""",
    )

    args = parser.parse_args()

    return args


def main(args: argshell.Namespace | None = None):
    if not args:
        args = get_args()
    project = packagelister.scan_dir(Pathier.cwd(), excludes=args.exclude)
    print(f"Packages imported by {Pathier.cwd().stem}:")
    print(
        *(
            project.get_formatted_requirements(" v")
            + ([] if not args.builtins else project.packages.builtin.names)
        ),
        sep="\n",
    )
    if args.generate_requirements:
        print("Generating `requirements.txt`.")
        (Pathier.cwd() / "requirements.txt").join(
            project.get_formatted_requirements(args.versions)
        )
    if args.files:
        print("Files importing each package:")
        files_by_package = project.get_files_by_package()
        if not args.builtins:
            files_by_package = {
                k: v
                for k, v in files_by_package.items()
                if k in project.packages.third_party.names
            }
        for package, files in files_by_package.items():
            print(f"{package}:")
            print(*[f"  {file}" for file in files], sep="\n")
    if args.debug:
        print(*project.packages, sep="\n")


if __name__ == "__main__":
    main(get_args())
