import os
from collections.abc import Generator, Sequence
from pathlib import Path
from typing import Union

import pytest
from _pytest.pytester import Pytester

from pytest_envx.plugin import IniEnvManager, TomlEnvManager


@pytest.fixture
def toml_config_manager(pytestconfig: pytest.Config) -> TomlEnvManager:
    return TomlEnvManager(pytestconfig)


@pytest.fixture(autouse=True)
def clear_test_env(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    original_env = os.environ.copy()
    yield
    new_vars = set(os.environ) - set(original_env)
    for var in new_vars:
        monkeypatch.delenv(var, raising=False)
    for var, value in original_env.items():
        if os.getenv(var) != value:
            monkeypatch.setenv(var, value)


def _create_env_files(pytester: Pytester, env_sources: Sequence[Sequence[str]]) -> list[Path]:
    env_paths = []
    for i, env_source in enumerate(env_sources):
        env_path = pytester.makefile(f".env{i + 1}", *env_source)
        env_paths.append(env_path)
    return env_paths


def _verify_env_vars(expected_result: dict[str, str]) -> None:
    for var_name, expected_value in expected_result.items():
        assert os.getenv(var_name) == expected_value, f"Expected {var_name}={expected_value}, got {os.getenv(var_name)}"


class TestTomlEnvManager:
    @pytest.mark.parametrize(
        "env_sources, toml_source, expected_result",
        [
            pytest.param(
                [
                    ["DB_HOST=localhost", "DB_PORT=5432", "API_KEY=SECRET"],
                    ["DB_HOST=overridehost", "DB_PORT=3333"],
                ],
                """
                [tool.pytest_envx]
                envx_metadata = { paths_to_load = ["{env_path1}", "{env_path2}"], paths_to_interpolate = ["{env_path1}", "{env_path2}"] }
                DB_URL = { value = "{%DB_HOST%}:{%DB_PORT%}" }
                GOOGLE_API_KEY = "SERVICE_{%API_KEY%}_API_KEY"
                KEY1="{%NOT_EXIST%}"
                """,
                {
                    "DB_HOST": "overridehost",
                    "DB_PORT": "3333",
                    "DB_URL": "overridehost:3333",
                    "API_KEY": "SECRET",
                    "GOOGLE_API_KEY": "SERVICE_SECRET_API_KEY",
                    "KEY1": "{%NOT_EXIST%}",
                },
                id="multiple_env_files_with_overrides_and_interpolation",
            ),
            pytest.param(
                [
                    ["DB_HOST=localhost", "DB_PORT=5432"],
                    ["DB_HOST=overridehost", "DB_PORT=3333", "KEY1=VALUE1"],
                ],
                """
                [tool.pytest_envx]
                envx_metadata = { paths_to_load = ["{env_path1}", "{env_path2}"], paths_to_interpolate = ["{env_path1}"], override_load = false }
                DB_URL = { value = "{%DB_HOST%}:{%DB_PORT%}" }
                """,
                {
                    "DB_HOST": "localhost",
                    "DB_PORT": "5432",
                    "DB_URL": "localhost:5432",
                    "KEY1": "VALUE1",
                },
                id="multiple_env_files_no_override_load_first_file_priority",
            ),
            pytest.param(
                [
                    ["API_KEY=GOOGLE_API_KEY"],
                ],
                """
                [tool.pytest_envx]
                envx_metadata = { paths_to_load = ["{env_path1}"], paths_to_interpolate = [], override_load = false, override_interpolate = false }
                API_KEY = { value = "SERVICE_{%API_KEY%}", interpolate = false }
                """,
                {"API_KEY": "SERVICE_{%API_KEY%}"},
                id="single_env_file_with_interpolation_disabled",
            ),
            pytest.param(
                [["API_KEY=GOOGLE_API_KEY"]],
                """
                [tool.pytest_envx]
                envx_metadata = { paths_to_load = ["{env_path1}"], paths_to_interpolate = ["{env_path1}"], override_load = true, override_interpolate = true }
                API_KEY = { value = "SERVICE_{%API_KEY%}", interpolate = true }
                """,
                {"API_KEY": "SERVICE_GOOGLE_API_KEY"},
                id="single_env_file_with_interpolation_enabled",
            ),
            pytest.param(
                [
                    ["SOME_SYSTEM_ENV_KEY=SOME_SYSTEM_ENV_VALUE"],
                    ["SOME_SYSTEM_ENV_KEY=DANGEROUS_VALUE"],
                ],
                """
                [tool.pytest_envx]
                envx_metadata = { paths_to_load = ["{env_path1}", "{env_path2}"], paths_to_interpolate = [], override_load = false, override_interpolate = true }
                """,
                {"SOME_SYSTEM_ENV_KEY": "SOME_SYSTEM_ENV_VALUE"},
                id="multiple_env_files_no_override_load_protects_existing_values",
            ),
            pytest.param(
                [
                    ["SOME_SYSTEM_ENV_KEY=SOME_SYSTEM_ENV_VALUE"],
                    ["SOME_SYSTEM_ENV_KEY=DANGEROUS_VALUE"],
                ],
                """
                [tool.pytest_envx]
                envx_metadata = { paths_to_load = ["{env_path1}", "{env_path2}"], paths_to_interpolate = [], override_load = false, override_interpolate = false }
                SOME_SYSTEM_ENV_KEY = { value = "{%SAFE_VALUE%}", interpolate = false }
                """,
                {"SOME_SYSTEM_ENV_KEY": "{%SAFE_VALUE%}"},
                id="explicit_value_overrides_env_file_when_interpolation_disabled",
            ),
            pytest.param(
                [
                    [],
                ],
                """
                [tool.pytest_envx]
                VAR1 = "VALUE1"
                VAR2 = "{%VAR1%}"
                """,
                {
                    "VAR1": "VALUE1",
                    "VAR2": "{%VAR1%}",
                },
                id="no_env_files_with_direct_values_and_uninterpolated_placeholder",
            ),
            pytest.param(
                [
                    ["KEY1=VALUE1"],
                    ["KEY2=VALUE2"],
                ],
                """
                [tool.pytest_envx]
                envx_metadata = { paths_to_load = ["{env_path1}", "{env_path2}"], paths_to_interpolate = ["{env_path1}"], override_load = true, override_interpolate = false }
                DATA = { value = "GAME_{%KEY1%}" }
                """,
                {
                    "KEY1": "VALUE1",
                    "KEY2": "VALUE2",
                    "DATA": "GAME_VALUE1",
                },
                id="multiple_env_files_with_selective_interpolation",
            ),
        ],
    )
    def test_parse_toml_file_success(
        self,
        env_sources: Sequence[Sequence[str]],
        toml_source: str,
        expected_result: dict[str, str],
        pytester: Pytester,
        toml_config_manager: TomlEnvManager,
    ) -> None:
        """Test successful TOML config parsing."""
        if env_sources[0]:
            env_paths = _create_env_files(pytester=pytester, env_sources=env_sources)

            # Replace {env_pathX} placeholders in toml_source with actual paths
            for i, env_path in enumerate(env_paths):
                placeholder = f"{{env_path{i + 1}}}"
                toml_source = toml_source.replace(placeholder, str(env_path))

        # Create pyproject.toml using pytester
        toml_path = pytester.makepyprojecttoml(toml_source)

        # Set the TOML file path in toml_config_manager
        toml_config_manager._pytest_config._inipath = toml_path
        toml_config_manager.setup()

        _verify_env_vars(expected_result=expected_result)

    @pytest.mark.parametrize(
        "env_sources, toml_source, expected_error, expected_error_message",
        [
            pytest.param(
                [],
                """
                [tool.pytest_envx]
                envx_metadata = "not_a_dict"
                """,
                TypeError,
                "key 'envx_metadata' must be a dict, got str",
                id="metadata_not_a_dictionary",
            ),
            pytest.param(
                [],
                """
                [tool.pytest_envx]
                envx_metadata = { paths_to_load = 42 }
                """,
                TypeError,
                "argument 'paths_to_load' of key 'envx_metadata' must be a list",
                id="paths_to_load_not_a_list",
            ),
            pytest.param(
                [],
                """
                [tool.pytest_envx]
                envx_metadata = { paths_to_load = [32] }
                """,
                TypeError,
                "Path in 'paths_to_load' must be a string, got int",
                id="path_entry_not_a_string",
            ),
            pytest.param(
                [],
                """
                [tool.pytest_envx]
                envx_metadata = { paths_to_load = [], paths_to_interpolate = [42] }
                """,
                TypeError,
                "Path in 'paths_to_interpolate' must be a string, got int",
                id="interpolation_path_not_a_string",
            ),
            pytest.param(
                [],
                """
                [tool.pytest_envx]
                DB_URL = { value = 42 }
                """,
                ValueError,
                "'value' must be a string",
                id="env_value_not_a_string",
            ),
            pytest.param(
                [],
                """
                [tool.pytest_envx]
                DB_URL = { value = "test", interpolate = "not_a_bool" }
                """,
                TypeError,
                "Entry 'interpolate' must be a bool",
                id="interpolate_flag_not_a_boolean",
            ),
            pytest.param(
                [],
                """
                [tool.pytest_envx]
                DB_URL = 42
                """,
                TypeError,
                "Entry must be a string or dict, got int",
                id="env_entry_invalid_type",
            ),
        ],
    )
    def test_parse_toml_file_errors(
        self,
        env_sources: Sequence[Sequence[str]],
        toml_source: str,
        expected_error: type[Exception],
        expected_error_message: str,
        pytester: Pytester,
        toml_config_manager: TomlEnvManager,
    ) -> None:
        """Test TOML config parsing with error cases and edge cases."""
        toml_path = pytester.makepyprojecttoml(toml_source)
        toml_config_manager._pytest_config._inipath = toml_path

        with pytest.raises(expected_error, match=expected_error_message):
            toml_config_manager.setup()


class TestIniManager:
    """Tests for IniEnvManager with comprehensive positive scenarios."""

    @pytest.mark.parametrize(
        "env_sources, ini_content, expected_result",
        [
            pytest.param(
                [
                    ["DB_HOST=localhost", "DB_PORT=5432"],
                ],
                """
                [pytest]
                envx_metadata = {
                    "paths_to_load": ["{env_path1}"],
                    "paths_to_interpolate": ["{env_path1}"]
                    }
                env =
                    DB_URL="postgresql://{%DB_HOST%}:{%DB_PORT%}"
                    API_TIMEOUT="30"
                """,
                {
                    "DB_HOST": "localhost",
                    "DB_PORT": "5432",
                    "DB_URL": "postgresql://localhost:5432",
                    "API_TIMEOUT": "30",
                },
                id="single_env_file_with_interpolation",
            ),
            pytest.param(
                [
                    ["FEATURE_FLAG=ENABLED", "LOG_LEVEL=DEBUG"],
                    ["FEATURE_FLAG=DISABLED", "MAX_RETRIES=3"],
                ],
                """
                [pytest]
                envx_metadata = {"paths_to_load": ["{env_path1}", "{env_path2}"], "paths_to_interpolate": ["{env_path1}"], "override_load": False}
                env =
                    CONFIG={"value": "{%FEATURE_FLAG%}_{%LOG_LEVEL%}", "interpolate": True}
                    SERVICE_NAME="payment"
                """,
                {
                    "FEATURE_FLAG": "ENABLED",
                    "LOG_LEVEL": "DEBUG",
                    "MAX_RETRIES": "3",
                    "CONFIG": "ENABLED_DEBUG",
                    "SERVICE_NAME": "payment",
                },
                id="multiple_env_files_with_selective_interpolation_and_no_override",
            ),
            pytest.param(
                [
                    ["SECRET_KEY=abc123"],
                ],
                """
                [pytest]
                envx_metadata = {"paths_to_load": ["{env_path1}"]}
                env =
                    ENCRYPTED_KEY={"value": "enc_{%SECRET_KEY%}"}
                    DEBUG_MODE="True"
                """,
                {
                    "SECRET_KEY": "abc123",
                    "ENCRYPTED_KEY": "enc_{%SECRET_KEY%}",
                    "DEBUG_MODE": "True",
                },
                id="single_env_file_with_disabled_interpolation_by_default",
            ),
            pytest.param(
                [
                    ["COLOR_SCHEME=dark", "FONT_SIZE=14"],
                ],
                """
                [pytest]
                envx_metadata = {
                    "paths_to_load": ["{env_path1}"],
                    "paths_to_interpolate": ["{env_path1}"]
                    }
                env =
                    UI_CONFIG={"value": "{%COLOR_SCHEME%}-{%FONT_SIZE%}"}
                    CACHE_TTL="3600"
                """,
                {
                    "COLOR_SCHEME": "dark",
                    "FONT_SIZE": "14",
                    "UI_CONFIG": "dark-14",
                    "CACHE_TTL": "3600",
                },
                id="single_env_file_with_multiple_interpolations",
            ),
        ],
    )
    def test_parse_ini_file_success(
        self,
        env_sources: Sequence[Sequence[str]],
        ini_content: str,
        expected_result: dict[str, str],
        pytester: Pytester,
    ) -> None:
        env_paths = _create_env_files(pytester=pytester, env_sources=env_sources)
        for i, env_path in enumerate(env_paths):
            ini_content = ini_content.replace(f"{{env_path{i + 1}}}", str(env_path))
        ini_path = pytester.makeini(ini_content)
        pytest_config = pytester.parseconfigure(ini_path)
        ini_config_manager = IniEnvManager(pytest_config=pytest_config)
        ini_config_manager.setup()
        _verify_env_vars(expected_result=expected_result)

    @pytest.mark.parametrize(
        "env_sources, ini_content, expected_error, expected_error_message",
        [
            pytest.param(
                [],
                """
                [pytest]
                envx_metadata = not_a_dict
                """,
                ValueError,
                r"Invalid envx_metadata from ini file, 'not_a_dict'",
                id="invalid_metadata_syntax_not_json",
            ),
            pytest.param(
                [],
                """
                [pytest]
                envx_metadata = {"paths_to_load": 42}
                """,
                TypeError,
                r"argument 'paths_to_load' of key 'envx_metadata' must be a list",
                id="paths_to_load_not_a_list",
            ),
            pytest.param(
                [],
                """
                [pytest]
                envx_metadata = {"paths_to_interpolate": [42]}
                """,
                TypeError,
                r"Path in 'paths_to_interpolate' must be a string, got int",
                id="interpolation_path_not_a_string",
            ),
            pytest.param(
                [],
                """
                [pytest]
                env =
                    DB_URL=42
                """,
                TypeError,
                r"Invalid entry for DB_URL: Entry must be a string or dict, got int",
                id="env_value_invalid_type",
            ),
            pytest.param(
                [],
                """
                [pytest]
                env =
                    DB_URL={"value": "test", "interpolate": "not_a_bool"}
                """,
                TypeError,
                r"Invalid entry for DB_URL: Entry 'interpolate' must be a bool",
                id="interpolate_flag_not_a_boolean",
            ),
            pytest.param(
                [],
                """
                [pytest]
                env =
                    DB_URL
                """,
                ValueError,
                r"Invalid env line format \(missing '='\): 'DB_URL'",
                id="missing_equals_in_env_line",
            ),
        ],
    )
    def test_parse_ini_file_errors(
        self,
        env_sources: Sequence[Sequence[str]],
        ini_content: str,
        expected_error: type[Exception],
        expected_error_message: str,
        pytester: Pytester,
    ) -> None:
        """Test INI config parsing with error cases and edge cases."""
        with pytest.raises(expected_error, match=expected_error_message):
            ini_path = pytester.makeini(ini_content)
            pytester.parseconfig(ini_path)


@pytest.mark.parametrize(
    "inipath_name, expected_setup_result",
    [
        pytest.param("pytest.ini", False, id="toml_manager_with_pytest_ini_file"),
        pytest.param("tox.ini", False, id="toml_manager_with_tox_ini_file"),
        pytest.param(None, False, id="toml_manager_with_no_config_file"),
    ],
)
def test_invalid_inipath(
    inipath_name: Union[str, None],
    expected_setup_result: bool,
    pytester: Pytester,
    toml_config_manager: TomlEnvManager,
) -> None:
    if inipath_name:
        inipath = pytester.path / inipath_name
        inipath.touch()
        toml_config_manager._pytest_config._inipath = inipath
    else:
        toml_config_manager._pytest_config._inipath = None
    assert toml_config_manager.setup() == expected_setup_result
