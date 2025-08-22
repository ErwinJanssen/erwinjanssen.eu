"""Helper script to format Markdown files with Pandoc."""

import argparse
import subprocess


def format_markdown_file(filename: str) -> None:
    """Use Pandoc to format the file in-place."""
    # Command to read and write back the file using pandoc
    command = [
        "pandoc",
        # Process the specified file.
        filename,
        # Write the output to the same file.
        f"--output={filename}",
        # Without this option, the YAML metadata block is stripped.
        "--standalone",
        # Use the same number of columns as for Python code.
        "--columns=79",
        # Use reference links instead of in-line.
        "--reference-links",
        # Keep reference links close to where they are defined.
        "--reference-location=block",
    ]
    subprocess.run(command, check=True)  # noqa: S603


def main() -> None:
    """Entrypoint for this helper script."""
    parser = argparse.ArgumentParser(description="Format Markdown files using Pandoc.")
    parser.add_argument(
        "filenames",
        metavar="FILE",
        type=str,
        nargs="+",
        help="a list of filenames to process",
    )

    args = parser.parse_args()

    for filename in args.filenames:
        format_markdown_file(filename)
        print(f"Formatted {filename}")  # noqa: T201


if __name__ == "__main__":
    main()
