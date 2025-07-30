# dotenv-loader

Flexible and secure .env loader for Python projects with support for environment switching, nested project structures, and external configuration directories.

## 📚 Table of Contents
- [Overview](#-overview)
- [Historical Context](#-historical-context)
- [Features](#-features)
- [Security and Best Practices](#-security-and-best-practices)
- [Installation](#️-installation)
- [Python Compatibility](#-python-compatibility)
- [Usage](#-usage)
  - [Basic Usage](#basic-usage)
  - [Advanced Usage](#advanced-usage)
  - [Environment Variables](#environment-variables)
  - [Typical Directory Structure](#typical-directory-structure)
- [.env Resolution Rules and Precedence](#-env-resolution-rules-and-precedence)
- [Use Cases](#-use-cases)
- [License](#-license)
- [Contributing](#-contributing)
- [Acknowledgments](#-acknowledgments)
- [Changelog](#-changelog)


## 📖 Overview

**dotenv-loader** ([Git](https://github.com/dbdeveloper/dotenv-loader), [PyPI](https://pypi.org/project/dotenv-loader/)) provides a flexible yet straightforward way to load environment variables from `.env` files, tailored specifically for Python applications, including Django, Flask, Celery, FastCGI, WSGI, CLI tools, and more. It supports hierarchical configuration, making it extremely convenient to manage multiple environments (development, testing, production) without manually switching `.env` files or cluttering code with environment-specific logic.


## 🚀 Historical Context

Managing environment-specific settings is crucial in modern software development. The excellent [python-dotenv](https://pypi.org/project/python-dotenv/) package provides robust and versatile `.env` file loading functionality, but it lacks flexible mechanisms for dynamically switching configurations across multiple deployment environments or nested project structures.

**dotenv-loader** is built upon `python-dotenv`, enhancing it specifically to address the following practical challenges:

- Dynamically switch environments without modifying code or manually managing environment variables.
- Support flexible directory structures, such as monorepos or Django sub-applications.
- Provide clear, hierarchical separation of environment-specific configurations to improve clarity and reduce human error.

While **dotenv-loader** specializes in dynamic and hierarchical environment selection tailored for specific deployment scenarios, **python-dotenv** offers broader and more general-purpose capabilities. Users whose needs aren't fully met by `dotenv-loader` are strongly encouraged to leverage `python-dotenv`'s comprehensive functionality directly.


## ✨ Features

- **Hierarchical and prioritized .env file search**: dotenv-loader follows a clear and intuitive priority order:
  1. Explicit path provided via `DOTENV` environment variable.
  2. Configuration directory (`DOTCONFIG_ROOT`) with customizable subdirectories per project and environment stage (`DOTSTAGE`).
  3. Automatic fallback to `.env` file located directly in the project root.

- **Dynamic project and stage selection**: Quickly switch configurations by setting the `DOTPROJECT` and `DOTSTAGE` environment variables, allowing effortless toggling between multiple environments or projects.

- **Customizable file names**: Use custom `.env` filenames to further separate and manage your configurations.


## 🔒 Security and Best Practices

Storing `.env` files separately in a dedicated configuration directory (`DOTCONFIG_ROOT`) outside your project source tree is a secure and recommended best practice. This approach significantly reduces the risk of accidentally leaking sensitive information (such as API keys, database credentials, etc.) during backups, version control operations, or file transfers. By keeping secrets separate from your codebase, dotenv-loader helps enforce a clear boundary between configuration and code, enhancing security and compliance.


## ⚙️ Installation

```bash
pip install dotenv-loader
```


## ✅ Python Compatibility

This package is tested on the following Python versions via GitHub Actions:

| Python version | Status       |
|----------------|--------------|
| 3.9            | ✅ Supported |
| 3.10           | ✅ Supported |
| 3.11           | ✅ Supported |
| 3.12           | ✅ Supported |
| 3.13           | ✅ Supported |

> Automated tests are run on every push and pull request to ensure consistent support.


## 🛠 Usage

### Basic Usage

By default, dotenv-loader automatically identifies the `.env` file from the current project's root directory:

```python
import dotenv_loader

dotenv_loader.load_env()  # Locate the resolved .env file and populate os.environ
                          # with its variables
```


### Advanced Usage

```python
from dotenv_loader import load_env

# Load environment with custom default settings:
load_env(
    project='mega-project',           # - explicitly set project name
    stage='production',               # - explicitly set stage name
    dotenv='./dir/.env.test'          # - explicitly set .env file 
    config_root='~/custom-configs',   # - custom config directory
    steps_to_project_root=1,          # - how many directories up to look for project root
    default_env_filename='custom.env',# - change the default '.env' name to you name
    override=True,                    # - whether to overwrite existing values in os.environ
    dry_run=False                     # - if True, only return the resolved .env path
                                      #   without loading it
)
```


### Dry-run Usage

Use dry-run mode when you want to inspect or parse the .env file manually (e.g., without modifying the environment):

```python
from dotenv_loader import load_env
from dotenv import dotenv_values

env_file = load_env(dry_run=True)  # Return the resolved .env file path without applying
                                   # it to os.environ 
if env_file:
   config = dotenv_values(env_file)  # Load variables into a dict without affecting the
                                     # environment:
                                     # config = {"USER": "foo", "EMAIL": "foo@example.org"}
else:
  raise FileNotFoundError(".env file was not found!")
```


### Parameters of `load_env()`

The `load_env()` function accepts the following optional parameters:

|N| Parameter              | Type                      | Description |
|-|------------------------|---------------------------|-------------|
|1| `project`              | `str`                     | Explicit project name to use. Overrides automatic detection from directory name. |
|2| `stage`                | `str`                     | Environment stage (e.g., `prod`, `dev`, `test`). Combined with filename to locate `.env`, eg.: `.env[.${stage}]`. |
|3| `dotenv`               | `str` or `Path`           | Explicit path to `.env` file or directory. If a file is given and not found, raises `FileNotFoundError`. |
|4| `config_root`          | `str` or `Path`           | Override the default configuration root directory (`~/.config/python-projects`). |
|5| `steps_to_project_root`| `int`                     | How many parent directories to traverse when resolving the project root (default value is 0) |
|6| `default_env_filename` | `str`                     | The base filename to use instead of default `.env` (e.g., `"custom.env"` → `custom.env.test`). |
|7| `override`             | `bool` (default: `True`)  | Whether to overwrite existing environment variables already defined in os.environ. Use False to preserve values already present (e.g. from OS or CI/CD), or True to always prefer .env contents. |
|8| `dry_run`              | `bool` (default: `False`) | If `True`, does not load anything — only returns the path to the `.env` file if found, or `None` otherwise. Useful for inspection or custom loading logic. |

> **⚠️  Note:** Each parameter is optional and first four parameters (`project`, `stage`, `dotenv` and `config_root`) can also be controlled via environment variables: `DOTPROJECT`, `DOTSTAGE`, `DOTENV`, and `DOTCONFIG_ROOT`, respectively.


### Environment Variables

You can control the behavior of dotenv-loader using the following environment variables:

#### **DOTENV** — Path to the .env file or directory.

- If a full file path is given, it overrides all other options. If the file is not found, a `FileNotFoundError` is raised.
- If a directory path is given, the loader will look for an environment file in that directory, based on `default_env_filename` and `DOTSTAGE` (or fallback `stage`).
    
Examples:
  
```bash
DOTENV=/home/user/.env.custom python manage.py
# Uses this exact file; raises an error if not found
 
DOTENV=~/myconfigs/myproject python manage.py
DOTSTAGE=prod
# Loads ~/myconfigs/myproject/.env.prod
 
DOTENV=~/configs/project python manage.py  # calling load_env(stage='local')
# Loads ~/configs/project/.env.local
```

#### **DOTPROJECT** — Quickly switch between project environments:

```bash
DOTPROJECT=test python manage.py
# Loads: ~/.config/python-projects/test/.env
```

#### **DOTSTAGE** — Select a configuration stage within a project (prod, staging, test):

```bash
DOTSTAGE=staging python manage.py
# Loads: ~/.config/python-projects/myproject/.env.staging
```

#### **DOTCONFIG_ROOT** — Override the default configuration root directory:

```bash
DOTCONFIG_ROOT=~/myconfigs python manage.py
# Loads: ~/myconfigs/myproject/.env
```

#### **DOTVERBOSE** — Print the resolved path of the loaded .env file to stdout:

```bash
DOTVERBOSE=1 python manage.py
# Output: Use DOTENV file from: /home/user/.config/python-projects/projectname/.env 
```

> **⚠️ Note**  
> Unlike other dotenv-loader variables, `DOTVERBOSE` doesn't influence the selection of the `.env` file — it only controls whether its path is printed to stdout.  
> This makes it safe and convenient to define `DOTVERBOSE` inside your `.env` file (e.g. during development) to always see which file was loaded.  
> Supported truthy values (case-insensitive): `'1'`, `'true'`, `'yes'`, `'on'`, `'ja'`.  
> **The `DOTVERBOSE` environment variable takes precedence over the value defined in the `.env` file.**


### Typical Directory Structure

```bash
~/.config/python-projects/
└── myproject/
    ├── .env          # Default configuration (typically a symlink 
    │                 # to .env.prod)
    │ 
    ├── .env.prod     # Production configuration. Use explicitly with:
    │                 # DOTSTAGE=prod python manage.py
    │ 
    ├── .env.staging  # Staging configuration. Use explicitly with: 
    │                 # DOTSTAGE=staging python manage.py
    │ 
    └── .env.test     # Testing configuration. Use explicitly with: 
                      # DOTSTAGE=test python manage.py

myproject/
└── manage.py  # By default, loads ~/.config/python-projects/myproject/.env
    .env       # Used only if no .env.* files are found in 
               # ~/.config/python-projects/myproject
```

## 🧽 `.env` Resolution Rules and Precedence

`dotenv-loader` uses a deterministic and secure resolution strategy when selecting the appropriate `.env` file to load. The logic ensures maximum flexibility while maintaining clarity and safety.

### Resolution Rules

1. **Environment Variables Take Precedence**

    The following environment variables override their corresponding `load_env()` arguments:
    
    - `DOTENV` overrides `dotenv`
    - `DOTPROJECT` overrides `project`
    - `DOTSTAGE` overrides `stage`
    - `DOTCONFIG_ROOT` overrides `config_root`

2. **Relative Paths Are Context-Aware**

    - Paths defined in environment variables (e.g., `DOTENV`, `DOTCONFIG_ROOT`) are resolved relative to the current working directory (`PWD`, as seen with `pwd`).

    - Paths passed directly to `load_env()` (e.g., `dotenv`, `config_root`) are resolved relative to the calling script's location, adjusted by `steps_to_project_root`.

    For example, if manage.py is at `~/projects/proj1/app/manage.py` and `steps_to_project_root=1`, then project_root is considered to be `~/projects/proj1`.

3. **Project and Stage Names Must Be Basenames**

    Both `DOTPROJECT`/`project` and `DOTSTAGE`/`stage` must not include slashes. They are treated strictly as simple names (i.e., `Path(name).name`).

4. **Highest Priority: Explicit .env Path or Directory**

    If either `DOTENV` or `dotenv` is defined, it takes priority over all other resolution logic.
    
    - If the value is a **full path to a file**, that file is loaded directly. If it doesn't exist, a `FileNotFoundError` is raised and **no fallback is attempted**.
    - If the value is a **directory path**, the loader will **only search within that directory**, constructing the target filename as `[default_env_filename][.stage]`, where `stage` comes from `DOTSTAGE` or the `stage` argument.

5. **Project Name Determination**

    The project name is determined as follows:
    
    - If `DOTPROJECT` or `project` is defined, its basename is used
    - Otherwise, it defaults to the basename of the computed `project_root` directory

    > **⚠️ Note:**
    > The `project_root` is computed relative to the file that **directly calls** `load_env()`, using the `steps_to_project_root` parameter.
    > - If `steps_to_project_root=0` (default), `project_root` is the directory containing the calling file
    > - If `steps_to_project_root=1`, it's the parent of that directory, and so on
    
    For example:
    
    If `load_env()` is called from `~/projects/proj1/app/manage.py` and `steps_to_project_root=1`, then `project_root = ~/projects/proj1`, and the fallback project name is `proj1`.

6. **.env Filename Construction**

    The `.env` filename is constructed as:
    
    `"[default_env_filename][[.]STAGE]"`
    
    where:
    
    - `default_env_filename` is `.env` by default
    - `STAGE` comes from `DOTSTAGE`or `stage` (if defined)

7. **Primary Search Location**

    If no explicit file path is provided via `DOTENV`/`dotenv`, the loader checks:
    
    `[DOTCONFIG_ROOT | config_root] / [DOTPROJECT | project] / [default_env_filename][.stage]`

8. **Fallback Location**

    If the file is not found in the config directory, a fallback search is performed in the computed project root:
    `[project_root] / [default_env_filename][.stage]`

9. **Error Handling**
    If no valid `.env` file is found after all resolution attempts, a `FileNotFoundError` is raised. The error message includes a list of all tried paths for easier debugging.


## 🎯 Use Cases

dotenv-loader is especially useful when:

- Deploying applications to multiple environments (development, testing, staging, production).
- Managing complex directory structures (monorepos or multi-app Django projects).
- Simplifying CI/CD workflows by dynamically selecting environment configurations.


## 📜 License

[MIT License](https://dbdeveloper.github.io/dotenv-loader/license)


## 🤝 Contributing

We welcome contributions from the community! Please see [CONTRIBUTING](https://dbdeveloper.github.io/dotenv-loader/contributing) for details on how to get started.


## 🤖 Acknowledgments

This project was created in collaboration with ChatGPT (OpenAI), utilizing the GPT-4o, GPT-4.5, and GPT-3 models.


## 📅 Changelog

For detailed release notes, see [CHANGELOG](https://dbdeveloper.github.io/dotenv-loader/changelog).

---

By clearly managing your environment variables and enabling dynamic configuration switching, dotenv-loader helps you streamline your deployment and development workflows, reduce errors, and maintain cleaner, more maintainable code.

