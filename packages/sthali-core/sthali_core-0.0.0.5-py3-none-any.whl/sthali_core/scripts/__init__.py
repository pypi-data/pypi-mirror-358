"""The module that contains the CLI commands.

Classes:
    Command: The commands that can be executed by the CLI.
    Generate: The class that executes the commands based on the provided arguments.
"""

import enum

from .docs.generate_api_reference import main as main_api_reference
from .docs.generate_docstring import main as main_docstring
from .docs.generate_licence import main as main_licence
from .docs.generate_readme import main as main_readme
from .docs.generate_requirements import main as main_requirements
from .project.generate_project import main as main_project
from .project.update_pyproject_dependencies import main as update_pyproject_dependencies


class Generate:
    """The class that executes the options based on the provided arguments.

    Methods:
        execute: Executes the option based on the provided arguments.
    """

    class GenerateOptionsEnum(str, enum.Enum):
        """The options that can be executed by the CLI.

        Options:
            api_reference
            docs
            docstring
            project
            readme
            requirements
        """

        api_reference = "api-reference"
        docs = "docs"
        docstring = "docstring"
        licence = "licence"
        project = "project"
        readme = "readme"
        requirements = "requirements"

    @staticmethod
    def execute(option: GenerateOptionsEnum, project_name: str | None = None) -> None:
        """Executes the option based on the provided arguments."""
        match option:
            case Generate.GenerateOptionsEnum.api_reference:
                main_api_reference()

            case Generate.GenerateOptionsEnum.docs:
                main_requirements()
                main_readme()

                main_docstring()
                main_api_reference()

                main_licence()

            case Generate.GenerateOptionsEnum.docstring:
                main_docstring()

            case Generate.GenerateOptionsEnum.licence:
                main_licence()

            case Generate.GenerateOptionsEnum.project:
                assert project_name is None, "Project name is required for project"
                main_project(project_name)
                main_licence()

            case Generate.GenerateOptionsEnum.readme:
                main_readme()

            case Generate.GenerateOptionsEnum.requirements:
                main_requirements()


class Update:
    """The class that executes the options based on the provided arguments.

    Methods:
        execute: Executes the option based on the provided arguments.
    """

    class UpdateOptionsEnum(str, enum.Enum):
        """The options that can be executed by the CLI."""

        requirements = "requirements"

    @staticmethod
    def execute(option: UpdateOptionsEnum) -> None:
        """Executes the option based on the provided arguments."""
        match option:
            case Update.UpdateOptionsEnum.requirements:
                update_pyproject_dependencies()
