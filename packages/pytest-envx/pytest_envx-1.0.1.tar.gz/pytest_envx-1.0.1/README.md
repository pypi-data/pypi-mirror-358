<p align="center">
  <img width="792" height="369" src="docs/images/logo.png" alt="logo">
</p>

[![PyPI version](https://badge.fury.io/py/pytest-envx.svg)](https://badge.fury.io/py/pytest-envx)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-envx.svg)](https://pypi.org/project/pytest-envx/)
[![codecov](https://codecov.io/gh/eugeneliukindev/pytest-envx/graph/badge.svg?token=JRCQR1PFZ0)](https://codecov.io/gh/eugeneliukindev/pytest-envx)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

<details>
<summary><b>🌍 Select Language</b></summary>

- [English](https://github.com/eugeneliukindev/pytest-envx/blob/master/README.md)
- [Русский](https://github.com/eugeneliukindev/pytest-envx/blob/master/docs/README.ru.md)
</details>

# 🔧 pytest-envx

**pytest-envx** is a powerful and user-friendly plugin for [pytest](https://pytest.org), allowing you to easily manage environment variables from configuration files like `pyproject.toml` and `pytest.ini`.

---

## 🚀 Features

- ✔️ Environment variable interpolation via templates
- ✔️ Load variables from `.env` files
- ✔️ Compatible with both `pyproject.toml` and `pytest.ini`
- ✔️ Easy to configure and use
- ✔️ Flexible support for overriding and loading order

---

## ⚡️ Installation

```bash
pip install pytest-envx
```

---

## 📦 Quick Start

Create a configuration file — either `pyproject.toml` ⚙️ or `pytest.ini` ⚙️
By default, `pytest` prioritizes `pytest.ini` ⚙️

### ✅ Example 1: Simple Variable

<table>
  <tr>
    <th>pyproject.toml ⚙️</th>
    <th>pytest.ini ⚙️</th>
  </tr>
  <tr>
    <td>
      <pre lang="toml"><code>[tool.pytest_envx]
HELLO = "WORLD"</code></pre>
    </td>
    <td>
      <pre lang="ini"><code>[pytest]
env =
    HELLO="WORLD"</code></pre>
    </td>
  </tr>
</table>

**`test_example.py`** 🐍:

```python
import os

def test_env_var():
    assert os.getenv("HELLO") == "WORLD"
```

---

### ✅ Example 2: Load from `.env` 🔐 files with override

<table>
  <tr>
    <th>.env-template 🔐</th>
    <th>.env 🔐</th>
  </tr>
  <tr>
    <td>
      <pre lang="dotenv">
NAME=ALICE
LASTNAME=BAILER
      </pre>
    </td>
    <td>
      <pre lang="dotenv">
NAME=BOB
      </pre>
    </td>
  </tr>
</table>

<table>
  <tr>
    <th>pyproject.toml ⚙️</th>
    <th>pytest.ini ⚙️</th>
  </tr>
  <tr>
    <td>
      <pre lang="toml">
[tool.pytest_envx]
envx_metadata = { paths_to_load = [".env-template", ".env"], override_load = true }
GREETING = "Hello"
      </pre>
    </td>
    <td>
      <pre lang="ini">
[pytest]
envx_metadata = {"paths_to_load": [".env-template", ".env"], "override_load": True}
env =
    GREETING="Hello"
      </pre>
    </td>
  </tr>
</table>

**`test_env_load.py`** 🐍:

```python
import os

def test_env_loading():
    assert os.getenv("NAME") == "BOB"
    assert os.getenv("LASTNAME") == "BAILER"
    assert os.getenv("GREETING") == "Hello"
```

---

### ✅ Example 3: Load from `.env` 🔐 files without override

<table>
  <tr>
    <th>.env.default 🔐</th>
    <th>.env.dev 🔐</th>
  </tr>
  <tr>
    <td>
      <pre lang="dotenv">
MODE=default
      </pre>
    </td>
    <td>
      <pre lang="dotenv">
MODE=development
LEVEL=DEV
      </pre>
    </td>
  </tr>
</table>

<table>
  <tr>
    <th>pyproject.toml ⚙️</th>
    <th>pytest.ini ⚙️</th>
  </tr>
  <tr>
    <td>
      <pre lang="toml">
[tool.pytest_envx]
envx_metadata = { paths_to_load = [".env.default", ".env.dev"], override_load = false }
      </pre>
    </td>
    <td>
      <pre lang="ini">
[pytest]
envx_metadata = {"paths_to_load": [".env.default", ".env.dev"], "override_load": False}
      </pre>
    </td>
  </tr>
</table>

**`test_priority.py`** 🐍:

```python
import os

def test_env_priority():
    assert os.getenv("MODE") == "default"
    assert os.getenv("LEVEL") == "DEV"
```

### ✅ Example 4: Variable Interpolation

<table>
  <tr>
    <th>.env 🔐</th>
  </tr>
  <tr>
    <td>
      <pre lang="dotenv">
USER=john
PASS=secret
HOST=db.local
PORT=5432
      </pre>
    </td>
  </tr>
</table>

<table>
  <tr>
    <th>pyproject.toml ⚙️</th>
    <th>pytest.ini ⚙️</th>
  </tr>
  <tr>
    <td>
      <pre lang="toml">
[tool.pytest_envx]
envx_metadata = { paths_to_interpolate = [".env"] }
DB_URL_WITH_INTERPOLATION = "postgresql://{%USER%}:{%PASS%}@{%HOST%}:{%PORT%}/app"
WITHOUT_INTERPOLATION = { value = "{%USER%}", interpolate = false }
NOT_FOUND = "{%NOT_FOUND%}"
      </pre>
    </td>
    <td>
      <pre lang="ini">
[pytest]
envx_metadata = {"paths_to_interpolate": [".env"]}
env =
    DB_URL_WITH_INTERPOLATION="postgresql://{%USER%}:{%PASS%}@{%HOST%}:{%PORT%}/app"
    WITHOUT_INTERPOLATION={"value": "{%USER%}", "interpolate": False}
    NOT_FOUND = "{%NOT_FOUND%}"
      </pre>
    </td>
  </tr>
</table>

**`test_interpolation.py`** 🐍:

```python
import os

def test_interpolated_value():
    assert os.getenv("DB_URL_WITH_INTERPOLATION") == "postgresql://john:secret@db.local:5432/app"
    assert os.getenv("WITHOUT_INTERPOLATION") == "{%USER%}"
    assert os.getenv("NOT_FOUND") == "{%NOT_FOUND%}"
    assert os.getenv("USER") !=  "john"
    assert os.getenv("PASS") !=  "secret"
    assert os.getenv("HOST") !=  "db.local"
    assert os.getenv("PORT") !=  "5432"
```

---

## ⚙️ envx_metadata

| Parameter               | Type     | Description |
|------------------------|----------|-------------|
| `paths_to_load`        | list     | Paths to `.env` files to load environment variables from (loaded in order) |
| `override_load`        | (bool, default=True) | Whether to override existing environment variables during load |
| `paths_to_interpolate` | list     | Paths to files for value interpolation |
| `override_interpolate` | (bool, default=True) | Whether to override variables during interpolation |


## 📄 License

[MIT](LICENSE.txt)
