import tomllib

from modules_generator import PYPROJECT_TOML


def get_version_from_pyproject():
    with open(PYPROJECT_TOML, "rb") as f:
        pyproject_data = tomllib.load(f)
    return pyproject_data["project"]["version"]
