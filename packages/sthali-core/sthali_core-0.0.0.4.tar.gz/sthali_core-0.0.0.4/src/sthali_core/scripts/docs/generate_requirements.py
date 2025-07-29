"""Script to generate the requirements documentation from pyproject.toml.

This script reads the Python version, dependencies, and optional dependencies from pyproject.toml,
renders them into a Markdown template, and writes the result to the requirements documentation file.
"""

import jinja2
import tomli
import typer

from ..commons import PYPROJECT_FILE_PATH, REQUIREMENTS_PATH, File

TEMPLATE = """
---

### Requirements

#### Prerequisites
- `python {{ python_version }}`
- `pip` package manager

#### Runtime Dependencies
This project requires the following Python packages with specific versions:
{% for dependency in dependencies %}
- `{{ dependency }}`
{% endfor %}

{% if optional_dependencies %}
#### Optional Dependencies
This project has optional dependencies that can be installed for additional features:
{% for group, deps in optional_dependencies.items() %}
##### {{ group }}
{% for dep in deps %}
- `{{ dep }}`
{% endfor %}
{% endfor %}
{% endif %}
"""


def main() -> None:
    """Generate the requirements documentation file.

    This function reads the Python version and dependencies from pyproject.toml,
    renders them into a Markdown template, and writes the output to the requirements file.
    """
    typer.echo("Generating requirements")

    typer.echo("Clearing requirements")
    with File(REQUIREMENTS_PATH, "w") as requirements_file:
        requirements_file.write("\n")

    typer.echo("Reading pyproject.toml")
    with File(PYPROJECT_FILE_PATH) as pyproject_file:
        pyproject_file_content = tomli.loads(pyproject_file.read())

    typer.echo("Getting requirements")
    python_version = pyproject_file_content["project"]["requires-python"]
    dependencies = pyproject_file_content["project"]["dependencies"]
    optional_dependencies = pyproject_file_content["project"]["optional-dependencies"]

    typer.echo("Rendering the template with the data")
    requirements = jinja2.Template(TEMPLATE).render(
        python_version=python_version,
        dependencies=dependencies,
        optional_dependencies=optional_dependencies,
    )

    typer.echo("Writing requirements")
    with File(REQUIREMENTS_PATH, "w") as requirements_file:
        requirements_file.write(requirements)

    typer.echo("Generated requirements")
