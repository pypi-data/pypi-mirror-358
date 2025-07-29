from __future__ import annotations

import ast
import os
import re
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Literal, cast

import pytest
from dotenv import dotenv_values

if sys.version_info >= (3, 11):  # pragma: no cover
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

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


class BasePytestEnvManager(ABC):
    """Base class for pytest configuration managers tatal."""

    _TEMPLATE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"\{%(\w+)%}")

    def __init__(self, pytest_config: pytest.Config) -> None:
        self._pytest_config: pytest.Config = pytest_config

    def _extract_placeholders(self, value: str) -> set[str]:
        """Extract template variables in format {%VAR_NAME%} from a string."""
        return set(self._TEMPLATE_PATTERN.findall(value))

    @staticmethod
    def _parse_raw_entry(raw_entry: Any) -> Entry:
        """Convert a raw config entry (string or dict) into an EnvEntry."""
        if isinstance(raw_entry, str):
            return Entry(value=raw_entry, interpolate=True)
        if isinstance(raw_entry, dict):
            value = raw_entry.get("value")
            if not isinstance(value, str):
                raise ValueError("'value' must be a string")
            interpolate = raw_entry.get("interpolate", True)
            if not isinstance(interpolate, bool):
                raise TypeError("Entry 'interpolate' must be a bool")
            return Entry(value=value, interpolate=interpolate)
        raise TypeError(f"Entry must be a string or dict, got {type(raw_entry).__name__}")

    @staticmethod
    def _parse_metadata(metadata_from_config: Any) -> Metadata:
        if not metadata_from_config:
            return Metadata()
        if not isinstance(metadata_from_config, dict):
            raise TypeError(f"key 'envx_metadata' must be a dict, got {type(metadata_from_config).__name__}")

        load_paths: Any = metadata_from_config.get("paths_to_load", [])
        interpolate_paths: Any = metadata_from_config.get("paths_to_interpolate", [])
        override_load: Any = metadata_from_config.get("override_load", True)
        override_interpolate: Any = metadata_from_config.get("override_interpolate", True)

        if not isinstance(load_paths, list):
            raise TypeError("argument 'paths_to_load' of key 'envx_metadata' must be a list")
        if not isinstance(interpolate_paths, list):
            raise TypeError("argument 'paths_to_interpolate' of key 'envx_metadata' must be a list")
        if not isinstance(override_load, bool):
            raise TypeError("argument 'override_load' of key 'envx_metadata' must be a bool")
        if not isinstance(override_interpolate, bool):
            raise TypeError("argument 'override_interpolate' of key 'envx_metadata' must be a bool")

        for path in load_paths:
            if not isinstance(path, str):
                raise TypeError(f"Path in 'paths_to_load' must be a string, got {type(path).__name__}")
        for path in interpolate_paths:
            if not isinstance(path, str):
                raise TypeError(f"Path in 'paths_to_interpolate' must be a string, got {type(path).__name__}")
        return Metadata(
            paths_to_load=load_paths,
            paths_to_interpolate=interpolate_paths,
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

    def _is_valid_inifile(self, filename: Literal["pyproject.toml", "pytest.ini", "tox.ini"]) -> bool:
        """Check if the pytest config's inifile exists and matches the given filename."""
        inipath = self._pytest_config.inipath
        return inipath is not None and inipath.exists() and inipath.name == filename

    def _set_env_var(self, key: str, entry: Entry, interpolate_vars: dict[str, str | None]) -> None:
        """Set an environment variable based on the entry and interpolation vars."""
        value: str = (
            self._interpolate(value=entry.value, interpolate_vars=interpolate_vars)
            if entry.interpolate and entry.value and interpolate_vars
            else entry.value
        )
        os.environ[key] = value

    def _apply_env_vars(self, raw_config_vars: dict[str, Any], metadata: Metadata) -> None:
        loaded_vars = (
            self._load_dotenv(metadata.paths_to_load, metadata.override_load) if metadata.paths_to_load else {}
        )

        interpolate_vars = (
            self._load_dotenv(metadata.paths_to_interpolate, metadata.override_interpolate)
            if metadata.paths_to_interpolate
            else {}
        )

        env_vars: dict[str, Any] = loaded_vars | raw_config_vars

        # Set environment variables
        for key, raw_entry in env_vars.items():  # type: str, Any
            os.environ.pop(key, None)  # Clear existing environment variables that will be set
            try:
                entry: Entry = self._parse_raw_entry(raw_entry=raw_entry)
                self._set_env_var(key=key, entry=entry, interpolate_vars=interpolate_vars)
            except (TypeError, ValueError) as e:
                raise type(e)(f"Invalid entry for {key}: {e}") from e

    @abstractmethod
    def setup(self) -> bool:
        """Load and apply environment configuration."""
        raise NotImplementedError()


class TomlEnvManager(BasePytestEnvManager):
    """Manages environment variables from pyproject.toml."""

    def __init__(self, pytest_config: pytest.Config) -> None:
        super().__init__(pytest_config=pytest_config)

    @staticmethod
    def _load_toml_config(path: Path) -> dict[str, Any]:
        """Load pytest_envx section from a TOML file."""
        config = tomllib.loads(path.read_text())
        return cast(dict[str, Any], config.get("tool", {}).get("pytest_envx", {}))

    def setup(self) -> bool:
        """Configure environment from pyproject.toml."""
        if not self._is_valid_inifile("pyproject.toml"):
            return False

        assert self._pytest_config.inipath is not None  # Type narrowing for mypy
        toml_config = self._load_toml_config(self._pytest_config.inipath)
        if not toml_config:
            return False

        metadata = self._parse_metadata(toml_config.pop("envx_metadata", None))
        raw_config_vars = toml_config  # We delete metadata from toml_config, now there only config_vars
        self._apply_env_vars(raw_config_vars=raw_config_vars, metadata=metadata)
        return True


class IniEnvManager(BasePytestEnvManager):
    """Manages environment variables from pytest.ini."""

    def __init__(self, pytest_config: pytest.Config) -> None:
        super().__init__(pytest_config=pytest_config)

    def setup(self) -> bool:
        """Configure environment from pytest.ini or tox.ini."""
        if not (self._is_valid_inifile("pytest.ini") or self._is_valid_inifile("tox.ini")):
            return False

        metadata_from_inifile: Any = self._pytest_config.getini("envx_metadata")
        if metadata_from_inifile:
            try:
                metadata_from_inifile = ast.literal_eval(metadata_from_inifile)
            except (SyntaxError, ValueError) as e:
                raise type(e)(f"Invalid envx_metadata from ini file, {metadata_from_inifile!r}") from e

        metadata = self._parse_metadata(metadata_from_inifile)

        env_lines = self._pytest_config.getini("env")
        raw_config_vars: dict[str, Any] = {}
        for line in env_lines:
            if "=" not in line:
                raise ValueError(f"Invalid env line format (missing '='): {line!r}")
            key, _, raw_entry = line.partition("=")
            raw_config_vars[key.strip()] = ast.literal_eval(raw_entry.strip())

        self._apply_env_vars(raw_config_vars=raw_config_vars, metadata=metadata)
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
    TomlEnvManager(pytest_config=early_config).setup()
    IniEnvManager(pytest_config=early_config).setup()
