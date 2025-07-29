"""Script to generate the license documentation file from the main LICENSE file.

This script clears the license documentation file and writes the contents of the LICENSE file into it.
"""

import typer

from ..commons import LICENSE_DOC_PATH, LICENSE_PATH, File


def main() -> None:
    """Generate the license documentation file.

    This function clears the license documentation file and writes the contents
    of the LICENSE file into the documentation file.
    """
    typer.echo("Generating license")

    typer.echo("Clearing license")
    with File(LICENSE_DOC_PATH, "w") as license_doc_file:
        license_doc_file.write("\n")

    with File(LICENSE_DOC_PATH, "w") as license_doc_file, File(LICENSE_PATH) as license_file:
        license_file_content = license_file.read()
        license_doc_file.write(license_file_content)

    typer.echo("Generated license")
