import os
from cookiecutter.main import cookiecutter
from kubails.utils.service_helpers import get_codebase_subfolder


TEMPLATES_FOLDER = get_codebase_subfolder("templates")


class Templater:
    @staticmethod
    def template_primary() -> None:
        cookiecutter(os.path.join(TEMPLATES_FOLDER, "primary"))

    @staticmethod
    def template_service(service_type: str, title: str, name: str, output_dir: str) -> None:
        context = {
            "title": title,
            "name": name
        }

        cookiecutter(
            os.path.join(TEMPLATES_FOLDER, service_type),
            no_input=True,
            extra_context=context,
            output_dir=output_dir
        )
