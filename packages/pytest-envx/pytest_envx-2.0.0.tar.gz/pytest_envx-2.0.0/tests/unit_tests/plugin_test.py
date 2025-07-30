from __future__ import annotations

import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from _pytest.pytester import Pytester

from pytest_envx.plugin import Entry, IniEnvManager, Metadata


# Фикстуры
@pytest.fixture
def mock_config(pytester: Pytester) -> pytest.Config:
    # Используем pytester для создания временного pytest.ini
    return pytester.parseconfig()


@pytest.fixture
def inimanager(mock_config: pytest.Config) -> IniEnvManager:
    class MockManager(IniEnvManager):
        def setup(self) -> bool:
            return True  # pragma: no cover

    return MockManager(mock_config)


# Тесты
def test_extract_placeholders(inimanager: IniEnvManager) -> None:
    assert inimanager._extract_placeholders("{%VAR1%}:{%VAR2%}") == {"VAR1", "VAR2"}
    assert inimanager._extract_placeholders("no_placeholders") == set()
    assert inimanager._extract_placeholders("{%INVALID@%}") == set()


def test_parse_raw_entry_string(inimanager: IniEnvManager) -> None:
    entry: Entry = inimanager._parse_entry("test_value")
    assert entry == Entry(value="test_value", interpolate=True)


def test_parse_raw_entry_dict(inimanager: IniEnvManager) -> None:
    entry: Entry = inimanager._parse_entry({"value": "test_value", "interpolate": False})
    assert entry == Entry(value="test_value", interpolate=False)
    entry = inimanager._parse_entry({"value": "test_value"})
    assert entry == Entry(value="test_value", interpolate=True)


def test_parse_raw_entry_invalid_dict(inimanager: IniEnvManager) -> None:
    with pytest.raises(ValueError, match="argument 'value' in entry must be a 'str'"):
        inimanager._parse_entry({"value": 1})
    with pytest.raises(TypeError, match=r"Entry 'interpolate' must be a 'bool'"):
        inimanager._parse_entry({"value": "test_value", "interpolate": 1})


def test_parse_raw_entry_invalid_type(inimanager: IniEnvManager) -> None:
    with pytest.raises(TypeError, match="Entry must be a 'str' or dict-like, got 'int'"):
        inimanager._parse_entry(123)


def test_parse_metadata_empty(inimanager: IniEnvManager) -> None:
    metadata: Metadata = inimanager._parse_metadata("")
    assert metadata == Metadata(
        paths_to_load=[], paths_to_interpolate=[], override_load=False, override_interpolate=False
    )


def test_parse_metadata_valid(inimanager: IniEnvManager) -> None:
    raw_metadata = "{'paths_to_load': ['.env1', '.env2'],'paths_to_interpolate': ['.env1'],'override_load': False,'override_interpolate': True}"
    metadata: Metadata = inimanager._parse_metadata(raw_metadata)
    assert metadata == Metadata(
        paths_to_load=[".env1", ".env2"],
        paths_to_interpolate=[".env1"],
        override_load=False,
        override_interpolate=True,
    )


def test_parse_metadata_invalid_type(inimanager: IniEnvManager) -> None:
    with pytest.raises((SyntaxError, ValueError), match="Invalid 'envx_metadata' from config file: 'not_a_dict'"):
        inimanager._parse_metadata("not_a_dict")


def test_parse_metadata_invalid_type_2(inimanager: IniEnvManager) -> None:
    with pytest.raises(TypeError, match="key 'envx_metadata' must be a 'dict', got 'list'"):
        inimanager._parse_metadata("[]")


def test_parse_metadata_invalid_paths_to_interpolate(inimanager: IniEnvManager) -> None:
    with pytest.raises(TypeError, match="argument 'paths_to_interpolate' of key 'envx_metadata' must be a 'list'"):
        inimanager._parse_metadata("{'paths_to_interpolate': 'not_a_list'}")


def test_parse_metadata_invalid_paths_to_load(inimanager: IniEnvManager) -> None:
    with pytest.raises(TypeError, match="argument 'paths_to_load' of key 'envx_metadata' must be a 'list'"):
        inimanager._parse_metadata("{'paths_to_load': 'not_a_list'}")


def test_parse_metadata_invalid_paths_into_paths_to_load(inimanager: IniEnvManager) -> None:
    with pytest.raises(TypeError, match="Path in 'paths_to_load' must be a 'str', got 'int'"):
        inimanager._parse_metadata("{'paths_to_load': [123]}")


def test_parse_metadata_invalid_override_load(inimanager: IniEnvManager) -> None:
    with pytest.raises(TypeError, match="argument 'override_load' of key 'envx_metadata' must be a 'bool'"):
        inimanager._parse_metadata("{'override_load': 'not_a_bool'}")


def test_parse_metadata_invalid_override_interpolate(inimanager: IniEnvManager) -> None:
    with pytest.raises(TypeError, match="argument 'override_interpolate' of key 'envx_metadata' must be a 'bool'"):
        inimanager._parse_metadata("{'override_interpolate': 'not_a_bool'}")


def test_parse_metadata_invalid_path_type(inimanager: IniEnvManager) -> None:
    with pytest.raises(TypeError, match="paths_to_load' of key 'envx_metadata' must be a 'list'"):
        inimanager._parse_metadata("{'paths_to_load': '[123]'}")


def test_interpolate_success(inimanager: IniEnvManager) -> None:
    env_vars: dict[str, str | None] = {"VAR1": "value1", "VAR2": "value2", "VAR3": None}
    result: str = inimanager._interpolate("{%VAR1%}:{%VAR2%}:{%VAR3%}", env_vars)
    assert result == "value1:value2:"


def test_interpolate_no_placeholders(inimanager: IniEnvManager) -> None:
    result: str = inimanager._interpolate("no_placeholders", {})
    assert result == "no_placeholders"


def test_interpolate_missing_variable(inimanager: IniEnvManager) -> None:
    result: str = inimanager._interpolate("{%VAR%}", {})
    assert result == "{%VAR%}"


def test_interpolate_value_is_none(inimanager: IniEnvManager) -> None:
    result: str = inimanager._interpolate("{%VAR%}", {"VAR": None})
    assert result == ""


@patch("pytest_envx.plugin.dotenv_values")
def test_load_dotenv_empty(mock_dotenv_values: MagicMock, inimanager: IniEnvManager, pytester: Pytester) -> None:
    mock_dotenv_values.return_value = {}
    env_path = pytester.makefile(".env", "")
    result: dict[str, str | None] = inimanager._load_dotenv([env_path], override=True)
    assert result == {}
    mock_dotenv_values.assert_called_once_with(dotenv_path=env_path)


@patch("pytest_envx.plugin.dotenv_values")
def test_load_dotenv_non_existent(mock_dotenv_values: MagicMock, inimanager: IniEnvManager) -> None:
    result = inimanager._load_dotenv(["non_existent.env"], override=True)
    assert result == {}
    mock_dotenv_values.assert_called_once_with(dotenv_path="non_existent.env")


@patch("pytest_envx.plugin.dotenv_values")
def test_load_dotenv_multiple_files(
    mock_dotenv_values: MagicMock, inimanager: IniEnvManager, pytester: Pytester
) -> None:
    mock_dotenv_values.side_effect = [
        {"KEY1": "value1", "KEY2": "value2"},
        {"KEY2": "override2", "KEY3": "value3"},
    ]
    env1_path = pytester.makefile(".env", env1="")
    env2_path = pytester.makefile(".env", env2="")
    result: dict[str, str | None] = inimanager._load_dotenv([str(env1_path), str(env2_path)], override=True)
    assert result == {"KEY1": "value1", "KEY2": "override2", "KEY3": "value3"}
    mock_dotenv_values.side_effect = [
        {"KEY1": "value1", "KEY2": "value2"},
        {"KEY2": "override2", "KEY3": "value3"},
    ]
    result: dict[str, str | None] = inimanager._load_dotenv([str(env1_path), str(env2_path)], override=False)  # type: ignore[no-redef]
    assert result == {"KEY1": "value1", "KEY2": "value2", "KEY3": "value3"}
    assert mock_dotenv_values.call_count == 4


def test_set_env_var_interpolate(inimanager: IniEnvManager) -> None:
    entry: Entry = Entry(value="{%VAR%}", interpolate=True)
    with patch.dict(os.environ, clear=True):
        inimanager._set_env_var("KEY", entry, {"VAR": "value"})
        assert os.getenv("KEY") == "value"


def test_set_env_var_no_interpolate(inimanager: IniEnvManager) -> None:
    entry: Entry = Entry(value="{%VAR%}", interpolate=False)
    with patch.dict(os.environ, clear=True):
        inimanager._set_env_var("KEY", entry, {"VAR": "value"})
        assert os.getenv("KEY") == "{%VAR%}"


def test_set_env_var_no_interpolate_vars(inimanager: IniEnvManager) -> None:
    entry: Entry = Entry(value="{%VAR%}", interpolate=True)
    with patch.dict(os.environ, clear=True):
        inimanager._set_env_var("KEY", entry, {})
        assert os.getenv("KEY") == "{%VAR%}"


@patch("pytest_envx.plugin.dotenv_values")
def test_apply_env_vars(mock_dotenv_values: MagicMock, inimanager: IniEnvManager, pytester: Pytester) -> None:
    mock_dotenv_values.return_value = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    env_path = pytester.makefile(".env", "")
    metadata: Metadata = Metadata(
        paths_to_load=[str(env_path)],
        paths_to_interpolate=[str(env_path)],
        override_load=True,
        override_interpolate=True,
    )
    config_vars: dict[str, Any] = {"DB_URL": {"value": "{%DB_HOST%}:{%DB_PORT%}", "interpolate": True}}
    with patch.dict(os.environ, clear=True):
        inimanager._apply_env_vars(config_vars, metadata)
        assert os.getenv("DB_HOST") == "localhost"
        assert os.getenv("DB_PORT") == "5432"
        assert os.getenv("DB_URL") == "localhost:5432"


@patch("pytest_envx.plugin.dotenv_values")
def test_apply_env_vars_no_load_paths(mock_dotenv_values: MagicMock, inimanager: IniEnvManager) -> None:
    metadata: Metadata = Metadata(
        paths_to_load=[], paths_to_interpolate=[], override_load=True, override_interpolate=True
    )
    config_vars: dict[str, str] = {"KEY": "value"}
    with patch.dict(os.environ, clear=True):
        inimanager._apply_env_vars(config_vars, metadata)
        assert os.getenv("KEY") == "value"
    mock_dotenv_values.assert_not_called()


def test_apply_env_vars_invalid_entry(inimanager: IniEnvManager) -> None:
    metadata: Metadata = Metadata()
    config_vars: dict[str, Any] = {"INVALID_KEY": 123}
    with pytest.raises(
        TypeError, match="Invalid entry for 'INVALID_KEY': Entry must be a 'str' or dict-like, got 'int'"
    ):
        inimanager._apply_env_vars(config_vars, metadata)


def test_ini_setup_invalid_env_line(pytester: Pytester) -> None:
    ini_path = pytester.makeini(
        """
        [pytest]
        env =
            INVALID_ENV_LINE
        """
    )
    with pytest.raises(ValueError, match=r"Invalid env line format \(missing '='\): 'INVALID_ENV_LINE'"):
        pytester.parseconfig(ini_path)


def test_ini_setup_invalid_metadata(pytester: Pytester) -> None:
    ini_path = pytester.makeini(
        """
        [pytest]
        envx_metadata = invalid_syntax
        """
    )
    with pytest.raises((ValueError, SyntaxError), match="Invalid 'envx_metadata' from config file: 'invalid_syntax'"):
        pytester.parseconfig(ini_path)


def test_ini_setup_empty_metadata(pytester: Pytester) -> None:
    pytester.makeini(
        """
        [pytest]
        env =
            KEY="value"
        """,
    )
    config = pytester.parseconfig()
    manager = IniEnvManager(config)
    with patch.dict(os.environ, clear=True):
        assert manager.setup()
        assert os.getenv("KEY") == "value"
