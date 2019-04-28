import logging
import os
from typing import List
from kubails.utils.service_helpers import call_command


logger = logging.getLogger(__name__)

VALUES_FOLDER = "values"
TEMPLATES_FOLDER = "templates"


class Helm:
    def __init__(self, helm_folder, base_values_file):
        self.helm_folder = helm_folder
        self.values_folder = os.path.join(helm_folder, VALUES_FOLDER)
        self.base_values_file = base_values_file

        self.base_command = ["helm"]

    def template(
        self,
        output_dir: str,
        value_files: List[str] = [],
        template_files: List[str] = [],
        string_vars: List[str] = []
    ) -> bool:
        command = self.base_command + [
            "template", "--output-dir", output_dir, "--values", self.base_values_file
        ]

        for value_file in value_files:
            command.extend(["--values", os.path.join(self.values_folder, value_file)])

        for template_file in template_files:
            command.extend(["-x", os.path.join(TEMPLATES_FOLDER, template_file)])

        for string_var in string_vars:
            command.extend(["--set-string", string_var])

        command.append(self.helm_folder)

        return call_command(command)
