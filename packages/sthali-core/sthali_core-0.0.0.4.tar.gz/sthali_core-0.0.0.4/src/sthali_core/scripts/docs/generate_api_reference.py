"""Script to generate and update the API Reference section in mkdocs.yml based on available API reference files."""

import os

import typer
import yaml

from ..commons import API_REFERENCE_PATH, MKDOCS_FILE_PATH, File


def main() -> None:
    """Generate and update the API Reference section in mkdocs.yml.

    This function scans the API reference directory, updates the 'API Reference' section
    in the mkdocs.yml navigation, and writes the changes back to the file.
    """
    typer.echo("Generating API Reference")

    typer.echo("Getting references")
    api_references = sorted(os.listdir(API_REFERENCE_PATH))

    typer.echo("Reading mkdocs.yml")
    with File(MKDOCS_FILE_PATH) as mkdocs_file:
        mkdocs_dict = yaml.safe_load(mkdocs_file.read())

    typer.echo("Rendering mkdocs_dict with the data")
    for section in mkdocs_dict["nav"]:
        if "API Reference" in section:
            section["API Reference"] = [
                {"_".join(i.split("_")[1:]).rsplit(".", 1)[0]: f"api/{i}"} for i in api_references
            ]

    typer.echo("Writing mkdocs.yml")
    with File(MKDOCS_FILE_PATH, "w") as mkdocs_file:
        yaml.dump(mkdocs_dict, mkdocs_file)

    typer.echo("Generated API Reference")
