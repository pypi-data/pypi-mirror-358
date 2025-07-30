import importlib
import os
import sys
from argparse import ArgumentParser

from pydantic_core import PydanticUndefined
from pydantic_settings import BaseSettings


def main():
    # add current working directory relative
    # to where the sample-env command started
    sys.path.append(os.getcwd())
    parser = ArgumentParser()
    parser.add_argument(
        "class_path", help="Pass class of the pydantic-settings BaseSettings"
    )
    args = parser.parse_args()

    if args.class_path:
        module_path, settings_name = args.class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        settings_class = getattr(module, settings_name)

        if not issubclass(settings_class, BaseSettings):
            print("Provided class does not inherit from BaseSettings")

        lines: list[str] = []

        for field_name, model_field in settings_class.model_fields.items():
            env_name: str = model_field.alias or field_name.upper()
            if isinstance(env_name, (list, tuple)):
                env_name = env_name[0]

            default = model_field.default
            description = model_field.description

            default = (
                ""
                if model_field.default is PydanticUndefined
                else (
                    model_field.default
                    if model_field.default is not None
                    else ""
                )
            )
            if default is None:
                line = f"{env_name}="
            else:
                line = f"{env_name}={default}"

            if description is not None:
                line += f" # {description}"

            lines.append(line)

        lines.append("")
        output_path = ".env.sample"
        with open(output_path, "w") as f:
            f.write("\n".join(lines))


if __name__ == "__main__":
    main()
