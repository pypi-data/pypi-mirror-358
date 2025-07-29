"""A dict-like configuration with support for envvars, validation and type conversion"""

import inspect
import os
import re
from collections import UserDict
from pathlib import Path
from typing import Any, Self, Type, TypeVar

from pydantic import BaseModel

from configaroo import loaders
from configaroo.exceptions import MissingEnvironmentVariableError

ModelT = TypeVar("ModelT", bound=BaseModel)


class Configuration(UserDict):
    """A Configuration is a dict-like structure with some conveniences"""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | UserDict[str, Any] | Self) -> Self:
        """Construct a Configuration from a dictionary

        The dictionary is referenced directly, a copy isn't made
        """
        configuration = cls()
        if isinstance(data, UserDict | Configuration):
            configuration.data = data.data
        else:
            configuration.data = data
        return configuration

    @classmethod
    def from_file(
        cls,
        file_path: str | Path,
        loader: str | None = None,
        envs: dict[str, str] | None = None,
        env_prefix: str = "",
        extra_dynamic: dict[str, Any] | None = None,
    ) -> Self:
        """Read a Configuration from a file"""
        config_dict = loaders.from_file(file_path, loader=loader)
        return cls(config_dict).initialize(
            envs=envs, env_prefix=env_prefix, extra_dynamic=extra_dynamic
        )

    def initialize(
        self,
        envs: dict[str, str] | None = None,
        env_prefix: str = "",
        extra_dynamic: dict[str, Any] | None = None,
    ) -> Self:
        """Initialize a configuration.

        The initialization adds environment variables and parses dynamic values.
        """
        self = self if envs is None else self.add_envs(envs, prefix=env_prefix)
        return self.parse_dynamic(extra_dynamic)

    def with_model(self, model: Type[ModelT]) -> ModelT:
        """Apply a pydantic model to a configuration."""
        return self.validate_model(model).convert_model(model)

    def __getitem__(self, key: str) -> Any:
        """Make sure nested sections have type Configuration"""
        value = self.data[key]
        if isinstance(value, dict | UserDict | Configuration):
            return Configuration.from_dict(value)
        else:
            return value

    def __getattr__(self, key: str) -> Any:
        """Create attribute access for config keys for convenience"""
        try:
            return self[key]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' has no attribute or key '{key}'"
            )

    def __contains__(self, key: object) -> bool:
        """Add support for dotted keys"""
        if key in self.data:
            return True
        prefix, _, rest = str(key).partition(".")
        try:
            return rest in self[prefix]
        except KeyError:
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Allow dotted keys when using .get()"""
        if key in self.data:
            return self[key]

        prefix, _, rest = key.partition(".")
        try:
            return self[prefix].get(rest, default=default)
        except KeyError:
            return default

    def add(self, key: str, value: Any) -> Self:
        """Add a value, allow dotted keys"""
        prefix, _, rest = key.partition(".")
        if not rest:
            return self | {key: value}
        cls = type(self)
        return self | {prefix: cls(self.setdefault(prefix, {})).add(rest, value)}

    def add_envs(self, envs: dict[str, str], prefix: str = "") -> Self:
        """Add environment variables to configuration"""
        for env, key in envs.items():
            env_key = f"{prefix}{env}"
            if env_value := os.getenv(env_key):
                self = self.add(key, env_value)
            elif key not in self:
                raise MissingEnvironmentVariableError(
                    f"required environment variable '{env_key}' not found"
                )
        return self

    def parse_dynamic(
        self, extra: dict[str, Any] | None = None, _include_self: bool = True
    ) -> Self:
        """Parse dynamic values of the form {section.key}"""
        cls = type(self)
        variables = (
            (self.to_flat_dict() if _include_self else {})
            | {"project_path": _find_pyproject_toml()}
            | ({} if extra is None else extra)
        )
        parsed = cls(
            {
                key: (
                    value.parse_dynamic(extra=variables, _include_self=False)
                    if isinstance(value, Configuration)
                    else _incomplete_format(value, variables)
                    if isinstance(value, str)
                    else value
                )
                for key, value in self.items()
            }
        )
        if parsed == self:
            return parsed
        # Continue parsing until no more replacements are made.
        return parsed.parse_dynamic(extra=extra, _include_self=_include_self)

    def validate_model(self, model: Type[BaseModel]) -> Self:
        """Validate the configuration against the given model."""
        model.model_validate(self.data)
        return self

    def convert_model(self, model: Type[ModelT]) -> ModelT:
        """Convert data types to match the given model"""
        return model(**self.data)

    def to_dict(self) -> dict[str, Any]:
        """Dump the configuration into a Python dictionary"""
        return {
            key: value.to_dict() if isinstance(value, Configuration) else value
            for key, value in self.items()
        }

    def to_flat_dict(self, _prefix: str = "") -> dict[str, Any]:
        """Dump the configuration into a flat dictionary.

        Nested configurations are converted into dotted keys.
        """
        return {
            f"{_prefix}{key}": value
            for key, value in self.items()
            if not isinstance(value, Configuration)
        } | {
            key: value
            for nested_key, nested_value in self.items()
            if isinstance(nested_value, Configuration)
            for key, value in (
                self[nested_key].to_flat_dict(_prefix=f"{_prefix}{nested_key}.").items()
            )
        }


def _find_pyproject_toml(
    path: Path | None = None, _file_name: str = "pyproject.toml"
) -> Path:
    """Find a directory that contains a pyproject.toml file.

    This searches the given directory and all direct parents. If a
    pyproject.toml file isn't found, then the root of the file system is
    returned.
    """
    path = _get_foreign_path() if path is None else path
    if (path / _file_name).exists() or path == path.parent:
        return path.resolve()
    else:
        return _find_pyproject_toml(path.parent, _file_name=_file_name)


def _get_foreign_path() -> Path:
    """Find the path to the library that called this package.

    Search the call stack for the first source code file outside of configaroo.
    """
    self_prefix = Path(__file__).parent.parent
    return next(
        path
        for frame in inspect.stack()
        if not (path := Path(frame.filename)).is_relative_to(self_prefix)
    )


def _incomplete_format(text: str, replacers: dict[str, Any]) -> str:
    """Replace some, but not necessarily all format specifiers in a text string.

    Regular .format() raises an error if not all {replace} parameters are
    supplied. Here, we only replace the given replace arguments and leave the
    rest untouched.
    """
    dot = "__DOT__"  # Escape . in fields as they have special meaning in .format()
    pattern = r"({{{word}(?:![ars])?(?:|:[^}}]*)}})"  # Match {word} or {word:...}

    for word, replacement in replacers.items():
        for match in re.findall(pattern.format(word=word), text):
            # Split expression to only replace . in the field name
            field, colon, fmt = match.partition(":")
            replacer = f"{field.replace('.', dot)}{colon}{fmt}".format(
                **{word.replace(".", dot): replacement}
            )
            text = text.replace(match, replacer)
    return text
