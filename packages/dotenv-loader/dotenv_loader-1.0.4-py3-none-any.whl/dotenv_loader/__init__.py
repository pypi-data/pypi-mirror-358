# src/dotenv_loader/__init__.py

import os
import inspect
from pathlib import Path
from typing import Union, Optional
from dotenv import load_dotenv

DEFAULT_CONFIG_ROOT = "~/.config/python-projects"
DEFAULT_ENV_FILENAME = ".env"


def _resolve_path(path: Union[str, Path], base_path: Optional[Path] = None):
    path = Path(path).expanduser()
    if path.is_absolute(): return path
    elif base_path:        return (base_path / path).resolve()
    else:                  return path.resolve()


def _str_to_bool(value: str) -> bool:
    """ Change the string value (such as 'yes', 'Yes', 'YES', '1', 'Ja', etc.)
        to bool value = True, otherwise - False
    """
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on', 'ja')


def load_env(
    project:               Optional[str]              = None,
    stage:                 Optional[str]              = None,
    dotenv:                Optional[Union[str, Path]] = None,
    config_root:           Optional[Union[str, Path]] = None,
    steps_to_project_root: int                        = 0,
    default_env_filename:  Optional[str]              = None,
    override:              bool                       = True,
    dry_run:               bool                       = False
):
    """
    Load environment variables from a .env file with a flexible and hierarchical lookup strategy.

    Priority order for finding and loading .env files:

        1. Explicitly set via DOTENV environment variable (absolute or relative path).

        2. Config directory:
            - Project name is set via DOTPROJECT environment variable (if provided),
              otherwise, use the provided `project` parameter, or directory name based
              on `steps_to_project_root`.
            - Config directory root is set via DOTCONFIG_ROOT environment variable,
              otherwise default to `~/.config/python-projects`.

        3. Fallback to `.env` file located in the project's root directory.

    Parameters:
        project (str, optional): 
        ~~~~~~~~~~~~~~~~~~~~~~~~
            Explicit project name if DOTPROJECT env var is not set. If None, the name is 
            inferred from the parent directory at the given `steps_to_project_root`.

        stage (str, optional):
        ~~~~~~~~~~~~~~~~~~~~~~
            Explicit staging suffix for the default_env_filename if DOTSTAGE env var is not set. 
            If None, the default_env_filename parameter is used (e.g.: '.env'). With stage='test' or 
            DOTSTAGE=test, the name of the default_env_filename will be '.env.test'

        dotenv (str | Path, optional):
        ~~~~~~~~~~~~~~~~~~~~~~~
            Explicit path to the dotenv file if DOTENV env var is not set. 
            If None, the .env file will be compiled from all other parameters

        config_root (str | Path, optional, default: '~/.config/python-projects'): 
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Base directory for storing .env files, defaults to '~/.config/python-projects'.
            Can be overridden via the DOTCONFIG_ROOT environment variable.

        steps_to_project_root (int, optional, default: 0): 
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Defines how many parent directories to traverse up from the current file location
            to determine the project root.
               - 0: Current directory
               - 1: One level above
               - 2: Two levels above, etc.

        default_env_filename (str, optional, default: ".env"): 
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Base directory for storing .env files, defaults to '~/.config/python-projects'.
            Filename of the .env file. Defaults to '.env'.

        override (bool, optional, default: True): 
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Whether to overwrite existing environment variables already defined in os.environ. 
            Use False to preserve values already present (e.g. from OS or CI/CD), or True to 
            always prefer .env contents.

        dry_run (bool, optional, default: False):
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Locate the .env file without loading it. load_env() returns the path to the 
            discovered .env file or None, which can then be used by other libraries for
            loading.


    Returns:
        pathlib.Path: 
        ~~~~~~~~~~~~~
            Path object pointing to the loaded .env file. Can be used for debugging or logging

    Raises:
        FileNotFoundError: If no suitable .env file is found at any of the candidate locations.

    Example directory layout:

        configs:
            ~/.config/python-projects/proj1/.env
            ~/.config/python-projects/proj2/.env
            ~/.config/python-projects/proj2/.env.test

        usage:
            proj1/manage.py:
                load_env()  # loads ~/.config/python-projects/proj1/.env automatically

            proj2/app/manage.py:
                load_env(steps_to_project_root=1)  # loads ~/.config/python-projects/proj2/.env automatically
                load_env("proj2")  # set the project name explicitely. Loads ~/.config/python-projects/proj2/.env

            Use the config from another project. For proj1/manage.py:
                DOTPROJECT=proj2 python manage.py  # loads ~/.config/python-projects/proj2/.env

            Override the config for testing. For proj2/manage.py:
                DOTSTAGE=test python manage.py  # loads ~/.config/python-projects/proj2/.env.test

            Override the config directory. For proj1/manage.py:
                DOTCONFIG_ROOT=~/conf python manage.py  # loads ~/conf/proj1/.env

            Explicit file override:
                DOTENV=~/.env-custom python manage.py  # loads ~/.env-custom explicitly
    """
    # Create a prioritized list of candidate paths
    candidate_paths = []

    # Determine the base directory based on steps_to_project_root
    caller_file = Path(inspect.stack()[1].filename).resolve()
    base_dir = caller_file.parents[steps_to_project_root]

    # Resolve the env file name
    env_filename = Path(default_env_filename or DEFAULT_ENV_FILENAME).name
    env_stage = Path(os.getenv("DOTSTAGE", stage or '')).name
    if env_stage:
       env_filename += f".{env_stage}"

    # Check if user explicitly specified the .env file via DOTENV | dotenv
    enveron_dotenv = os.getenv("DOTENV")

    explicit_env_path = None
    if enveron_dotenv:
       explicit_env_path = _resolve_path(enveron_dotenv) 
    elif dotenv:
       explicit_env_path = _resolve_path(dotenv, base_dir)

    if explicit_env_path:
        if explicit_env_path.is_dir():
            explicit_env_path = explicit_env_path / env_filename 

        # Highest (and only the one) priority: explicitly provided .env file
        candidate_paths.append(explicit_env_path)
    else:
        # Determine the project name from environment or provided parameter
        project_name = Path(os.getenv("DOTPROJECT", project or base_dir)).name

        # Determine the configuration root directory
        raw_config_root = os.getenv("DOTCONFIG_ROOT")
        if raw_config_root:
           config_root_path =_resolve_path(raw_config_root) 
        else:
           raw_config_root = (config_root or DEFAULT_CONFIG_ROOT)
           config_root_path =_resolve_path(raw_config_root, base_dir)

        # Second priority: standard config root + project name + env file
        candidate_paths.append(config_root_path / project_name / env_filename)

        # Third priority: fallback to project directory's root
        candidate_paths.append(base_dir / env_filename)

    dotverbose_from_env = os.getenv("DOTVERBOSE")

    # Try loading from the first existing candidate file
    for dotenv_path in candidate_paths:
        if dotenv_path.exists():
            if dry_run or load_dotenv(dotenv_path, override=override):
                if _str_to_bool(dotverbose_from_env if dotverbose_from_env is not None else os.getenv("DOTVERBOSE")):
                    print(f"Use DOTENV file from {dotenv_path}")
                return dotenv_path


    # No file was found and loaded, raise an informative error
    searched_paths = ", ".join(str(path) for path in candidate_paths)
    error_message = f"No DOTENV file found. Paths checked: {searched_paths}" 

    if dry_run:
        # In `dry_run` mode, return None instead of raising an exception if the .env file is not found.
        if _str_to_bool(dotverbose_from_env):
            print(error_message)
        return None

    raise FileNotFoundError(error_message)

