"""Script to generate the README file by concatenating selected documentation files.

This script clears the README file and appends the contents of specified documentation files in order.
"""

import typer

from ..commons import DOCS_PATH, README_FILE_PATH, File

files_used_in_readme = ["index", "requirements", "installation", "usage"]


def main() -> None:
    """Generate the README file by concatenating documentation files.

    This function clears the README file and writes the contents of
    'index.md', 'requirements.md', 'installation.md', and 'usage.md'
    from the docs directory into the README file.
    """
    typer.echo("Generating readme")

    typer.echo("Clearing readme")
    with File(README_FILE_PATH, "w") as readme_file:
        readme_file.write("\n")

    with File(README_FILE_PATH, "w") as readme_file:
        docs_files_path_with_extension = [DOCS_PATH / f"{i}.md" for i in files_used_in_readme]
        for doc_file_path in docs_files_path_with_extension:
            typer.echo(f"Concatenating doc: {doc_file_path.name}")
            with File(doc_file_path) as doc_file:
                doc_file_content = doc_file.read()
                readme_file.write(doc_file_content)

    typer.echo("Generated readme")
