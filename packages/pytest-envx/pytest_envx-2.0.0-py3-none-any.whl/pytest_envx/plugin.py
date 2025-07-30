from __future__ import annotations

import ast
import os
import re
import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

import pytest
from dotenv import dotenv_values

if sys.version_info >= (3, 11):  # pragma: no cover
    pass
else:  # pragma: no cover
    pass

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class Metadata:
    paths_to_load: list[str] = field(default_factory=list)
    paths_to_interpolate: list[str] = field(default_factory=list)
    override_load: bool = False
    override_interpolate: bool = False


@dataclass
class Entry:
    value: str
    interpolate: bool


class IniEnvManager:
    """Manages environment variables from pytest.ini."""

    _TEMPLATE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"\{%(\w+)%}")

    def __init__(self, pytest_config: pytest.Config) -> None:
        self._pytest_config = pytest_config

    def _extract_placeholders(self, value: str) -> set[str]:
        """Extract template variables in format {%VAR_NAME%} from a string."""
        return set(self._TEMPLATE_PATTERN.findall(value))

    @staticmethod
    def _parse_entry(entry: Any) -> Entry:
        """Convert a raw config entry (string or dict) into an EnvEntry."""
        if isinstance(entry, str):
            return Entry(value=entry, interpolate=True)
        if isinstance(entry, dict):
            value = entry.get("value")
            if not isinstance(value, str):
                raise ValueError("argument 'value' in entry must be a 'str'")
            interpolate = entry.get("interpolate", True)
            if not isinstance(interpolate, bool):
                raise TypeError("Entry 'interpolate' must be a 'bool'")
            return Entry(value=value, interpolate=interpolate)
        raise TypeError(f"Entry must be a 'str' or dict-like, got {type(entry).__name__!r}")

    @staticmethod
    def _parse_metadata(metadata: str) -> Metadata:
        if not metadata:
            return Metadata()
        eval_metadata: dict[str, Any]
        try:
            eval_metadata = ast.literal_eval(metadata)
            if not isinstance(eval_metadata, dict):
                raise TypeError(f"key 'envx_metadata' must be a 'dict', got {type(eval_metadata).__name__!r}")
        except (SyntaxError, ValueError) as e:
            raise type(e)(f"Invalid 'envx_metadata' from config file: {metadata!r}") from e

        paths_to_load = eval_metadata.get("paths_to_load", [])
        if not isinstance(paths_to_load, list):
            raise TypeError("argument 'paths_to_load' of key 'envx_metadata' must be a 'list'")

        paths_to_interpolate = eval_metadata.get("paths_to_interpolate", [])
        if not isinstance(paths_to_interpolate, list):
            raise TypeError("argument 'paths_to_interpolate' of key 'envx_metadata' must be a 'list'")

        override_load = eval_metadata.get("override_load", True)
        if not isinstance(override_load, bool):
            raise TypeError("argument 'override_load' of key 'envx_metadata' must be a 'bool'")

        override_interpolate = eval_metadata.get("override_interpolate", True)
        if not isinstance(override_interpolate, bool):
            raise TypeError("argument 'override_interpolate' of key 'envx_metadata' must be a 'bool'")

        for path in paths_to_load:
            if not isinstance(path, str):
                raise TypeError(f"Path in 'paths_to_load' must be a 'str', got {type(path).__name__!r}")

        for path in paths_to_interpolate:
            if not isinstance(path, str):
                raise TypeError(f"Path in 'paths_to_interpolate' must be a 'str', got {type(path).__name__!r}")

        return Metadata(
            paths_to_load=paths_to_load,
            paths_to_interpolate=paths_to_interpolate,
            override_load=override_load,
            override_interpolate=override_interpolate,
        )

    def _interpolate(self, value: str, interpolate_vars: dict[str, str | None]) -> str:
        """Replace placeholders (e.g., {%VAR_NAME%}) with values from interpolate_vars."""

        def replace_match(match: re.Match[str]) -> str:
            var_name = match.group(1)
            # Replace None with empty string to avoid type errors
            return interpolate_vars.get(var_name, match.group(0)) or ""

        return self._TEMPLATE_PATTERN.sub(replace_match, value)

    @staticmethod
    def _load_dotenv(paths: Sequence[str | os.PathLike[str]], override: bool) -> dict[str, str | None]:
        """Load environment variables from .env files."""
        env_vars: dict[str, str | None] = {}
        for i, dotenv_path in enumerate(paths):
            file_vars: dict[str, str | None] = dotenv_values(dotenv_path=dotenv_path)
            if override:
                env_vars.update(file_vars)
            else:
                if i == 0:
                    env_vars.update(file_vars)
                else:
                    env_vars = {**file_vars, **env_vars}
        return env_vars

    def _set_env_var(self, key: str, entry: Entry, interpolate_vars: dict[str, str | None]) -> None:
        """Set an environment variable based on the entry and interpolation vars."""
        value: str = (
            self._interpolate(value=entry.value, interpolate_vars=interpolate_vars)
            if entry.interpolate and entry.value and interpolate_vars
            else entry.value
        )
        os.environ[key] = value

    def _apply_env_vars(self, config_vars: dict[str, Any], metadata: Metadata) -> None:
        loaded_vars = (
            self._load_dotenv(metadata.paths_to_load, metadata.override_load) if metadata.paths_to_load else {}
        )

        interpolate_vars = (
            self._load_dotenv(metadata.paths_to_interpolate, metadata.override_interpolate)
            if metadata.paths_to_interpolate
            else {}
        )

        env_vars: dict[str, Any] = loaded_vars | config_vars

        # Set environment variables
        for key, entry_str in env_vars.items():  # type: str, Any
            os.environ.pop(key, None)  # Clear existing environment variables that will be set
            try:
                entry: Entry = self._parse_entry(entry=entry_str)
                self._set_env_var(key=key, entry=entry, interpolate_vars=interpolate_vars)
            except (TypeError, ValueError) as e:
                raise type(e)(f"Invalid entry for {key!r}: {e}") from e

    def setup(self) -> bool:
        """Configure environment from pytest.ini or tox.ini."""
        metadata_str: str = self._pytest_config.getini("envx_metadata")
        metadata: Metadata = self._parse_metadata(metadata=metadata_str)

        env_lines = self._pytest_config.getini("env")
        config_vars: dict[str, Any] = {}
        for line in env_lines:
            if "=" not in line:
                raise ValueError(f"Invalid env line format (missing '='): {line!r}")
            key, _, value = line.partition("=")
            config_vars[key.strip()] = ast.literal_eval(value.strip())

        self._apply_env_vars(config_vars=config_vars, metadata=metadata)
        return True


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add configuration options for the plugin."""
    parser.addini(
        name="env",
        type="linelist",
        help="List of environment variables in format KEY=VALUE",
        default=[],
    )
    parser.addini(
        name="envx_metadata",
        type="string",
        help="List of paths to .env files",
        default="",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(early_config: pytest.Config) -> None:
    if early_config.inipath is not None and early_config.inipath.exists():
        IniEnvManager(pytest_config=early_config).setup()
