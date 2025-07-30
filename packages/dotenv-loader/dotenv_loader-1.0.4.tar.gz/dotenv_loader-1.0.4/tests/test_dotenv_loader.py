import os
import pytest
from pathlib import Path

import dotenv_loader as dl
from tests.proj1 import manage as proj1_manage
from tests.proj2.app import manage as proj2_manage


tests_dir = Path(__file__).parent.resolve()


# call patched load_env() in  proj1
def proj1_load_env(*args, **kwargs) -> Path:
    return proj1_manage.test_load_env(dl, *args, **kwargs)

# call patched load_env() in proj2
def proj2_load_env(*args, **kwargs) -> Path:
    return proj2_manage.test_load_env(dl, *args, **kwargs)

@pytest.fixture
def setup_dotconfig_root(monkeypatch) -> Path:
    # Patch the dotenv_loader to use testing DEFAULT_CONFIG_ROOT
    config_root = Path("tests/dotconfig_root").resolve()
    monkeypatch.setattr(dl, "DEFAULT_CONFIG_ROOT", str(config_root))

    # Clear DOT* environment variables
    monkeypatch.delenv("DOTCONFIG_ROOT", raising=False)
    monkeypatch.delenv("DOTPROJECT", raising=False)
    monkeypatch.delenv("DOTSTAGE", raising=False)
    monkeypatch.delenv("DOTENV", raising=False)
    monkeypatch.delenv("DOTVERBOSE", raising=False)
    monkeypatch.delenv("SETTING", raising=False)

    return config_root

def test_proj1_default_env_using_project_param_loading(setup_dotconfig_root, monkeypatch):
    # Read .env file from the default position
    env_path = proj1_load_env()
    assert os.getenv("SETTING") == "default_proj1"
    assert env_path == setup_dotconfig_root / "proj1/.env"
    
    # Read other .env file when override=False
    env_path = proj1_load_env(project="other-proj", override=False)
    assert os.getenv("SETTING") == "default_proj1"
    assert env_path == setup_dotconfig_root / "other-proj/.env"

    # Read other .env file when override=True (default value)
    env_path = proj1_load_env(project="other-proj")
    assert os.getenv("SETTING") == "default_other_proj"
    assert env_path == setup_dotconfig_root / "other-proj/.env"

    # As a project name, only the basename is used
    env_path = proj1_load_env(project="./blabla/blabla/other-proj")
    assert os.getenv("SETTING") == "default_other_proj"
    assert env_path == setup_dotconfig_root / "other-proj/.env"

def test_proj1_default_env_using_DOTPROJECT_env_loading(setup_dotconfig_root, monkeypatch):
    # Read .env file using project name from DOTPROJECT environment variable
    monkeypatch.setenv("DOTPROJECT", "other-proj")
    env_path = proj1_load_env()
    assert os.getenv("SETTING") == "default_other_proj"
    assert env_path == setup_dotconfig_root / "other-proj/.env"
    
    # Environment variable DOTPROJECT has preferences an 'project' function parameter
    monkeypatch.setenv("DOTPROJECT", "proj2")
    env_path = proj1_load_env(project="other-proj")
    assert os.getenv("SETTING") == "default_proj2"
    assert env_path == setup_dotconfig_root / "proj2/.env"

    # As a project name, only the basename is used
    monkeypatch.setenv("DOTPROJECT", "./bla/proj1")
    env_path = proj1_load_env(project="other-proj")
    assert os.getenv("SETTING") == "default_proj1"
    assert env_path == setup_dotconfig_root / "proj1/.env"

def test_proj1_default_env_and_stage_param_loading(setup_dotconfig_root, monkeypatch):
    # Read .env file from the default position
    env_path = proj1_load_env(stage='prod')
    assert os.getenv("SETTING") == "prod_proj1"
    assert env_path == setup_dotconfig_root / "proj1/.env.prod"
    
    env_path = proj1_load_env(project="proj2", stage='staging')
    assert os.getenv("SETTING") == "staging_proj2"
    assert env_path == setup_dotconfig_root / "proj2/.env.staging"

    # Read other .env file when use project and staging together
    env_path = proj1_load_env(project="other-proj", stage='test')
    assert os.getenv("SETTING") == "test_other_proj"
    assert env_path == setup_dotconfig_root / "other-proj/.env.test"

    env_path = proj1_load_env(project="other-proj", stage='other')
    assert os.getenv("SETTING") == "local_other_proj1"
    assert env_path == tests_dir / "proj1/.env.other"

def test_proj1_use_custom_default_env_filename(setup_dotconfig_root, monkeypatch):
    # Read a custom dotenv file
    env_path = proj1_load_env(default_env_filename="./custom.env")
    assert os.getenv("SETTING") == "custom_env_proj1"
    assert env_path == setup_dotconfig_root / "proj1/custom.env"

    # Use Path instead of string 
    env_path = proj1_load_env(default_env_filename=Path("./custom.env"))
    assert os.getenv("SETTING") == "custom_env_proj1"
    assert env_path == setup_dotconfig_root / "proj1/custom.env"

def test_proj1_use_unique_dotenv_file_with_param(setup_dotconfig_root, monkeypatch):
    # Read a unique user-defined dotenv file
    # NOTE: The relative path resolved using the path to project_root=proj1 as working directory
    env_path = proj1_load_env(dotenv="../other_config_root/other-proj/.env")
    assert os.getenv("SETTING") == "other_default_other_proj"
    assert env_path == tests_dir / "other_config_root/other-proj/.env"

    # Use Path instead of string 
    env_path = proj1_load_env(dotenv=Path("../other_config_root/other-proj/.env"))
    assert os.getenv("SETTING") == "other_default_other_proj"
    assert env_path == tests_dir / "other_config_root/other-proj/.env"

    # Empty dotenv - use default path
    env_path = proj1_load_env(dotenv="")
    assert os.getenv("SETTING") == "default_proj1"
    assert env_path == setup_dotconfig_root / "proj1/.env"

    # Use empty Path instead of empty string
    # Empty Path() is equal to Path('.')
    env_path = proj1_load_env(dotenv=Path(""))
    assert os.getenv("SETTING") == "local_proj1"
    assert env_path == tests_dir / "proj1/.env"

def test_proj1_use_unique_dotenv_file_with_env_perf_param(setup_dotconfig_root, monkeypatch):
    # Read a unique user-defined dotenv file. Environment variables has preference on the function parameters
    monkeypatch.setenv("DOTENV", "tests/proj1/.env.other")
    env_path = proj1_load_env(dotenv="../other_config_root/other-proj/.env")
    assert os.getenv("SETTING") == "local_other_proj1"
    assert env_path == tests_dir / "proj1/.env.other"

def test_proj1_use_unique_dotenv_file_with_env(setup_dotconfig_root, monkeypatch):
    # Read a unique user-defined dotenv file. 
    # NOTE: The working directory is a directory from where pytest is started
    monkeypatch.setenv("DOTENV", "tests/other_config_root/other-proj/.env")
    env_path = proj1_load_env()
    assert os.getenv("SETTING") == "other_default_other_proj"
    assert env_path == tests_dir / "other_config_root/other-proj/.env"

def test_proj2_use_unique_dotenv_file_with_param(setup_dotconfig_root, monkeypatch):
    # read a custom dotenv file. 
    # NOTE:  The relative path resolved using the path to proj2/manage.py as an active directory
    env_path = proj2_load_env(dotenv="./custom.env")
    assert os.getenv("SETTING") == "local_custom_dotenv_proj2"
    assert env_path == tests_dir / "proj2/app/custom.env"

    env_path = proj2_load_env(dotenv=Path("./custom.env"))
    assert os.getenv("SETTING") == "local_custom_dotenv_proj2"
    assert env_path == tests_dir / "proj2/app/custom.env"

    env_path = proj2_load_env(steps_to_project_root=1, dotenv="./app/custom.env")
    assert os.getenv("SETTING") == "local_custom_dotenv_proj2"
    assert env_path == tests_dir / "proj2/app/custom.env"

    env_path = proj2_load_env(steps_to_project_root=1, dotenv=Path("./app/custom.env"))
    assert os.getenv("SETTING") == "local_custom_dotenv_proj2"
    assert env_path == tests_dir / "proj2/app/custom.env"

def test_proj2_use_unique_dotenv_file_with_custom_default_env_filename_param(setup_dotconfig_root, monkeypatch):
    # read a custom dotenv file. 
    # NOTE:  The relative path resolved using the path to proj2/manage.py as an active directory
    env_path = proj2_load_env(dotenv=".", default_env_filename="custom.env")
    assert os.getenv("SETTING") == "local_custom_dotenv_proj2"
    assert env_path == tests_dir / "proj2/app/custom.env"

    env_path = proj2_load_env(dotenv=Path(""), default_env_filename=Path("blabla/custom.env"))
    assert os.getenv("SETTING") == "local_custom_dotenv_proj2"
    assert env_path == tests_dir / "proj2/app/custom.env"

    env_path = proj2_load_env(steps_to_project_root=1, dotenv="./app", default_env_filename='custom.env')
    assert os.getenv("SETTING") == "local_custom_dotenv_proj2"
    assert env_path == tests_dir / "proj2/app/custom.env"

def test_proj2_use_unique_dotenv_file_with_custom_default_env_filename_env(setup_dotconfig_root, monkeypatch):
    # read a custom dotenv file. 
    # NOTE:  The relative path resolved using the directory where pytest is executed (root project directory)

    monkeypatch.setenv("DOTENV", "./tests/proj2/app")
    env_path = proj2_load_env(default_env_filename="custom.env")
    assert os.getenv("SETTING") == "local_custom_dotenv_proj2"
    assert env_path == tests_dir / "proj2/app/custom.env"

    monkeypatch.setenv("DOTENV", "./tests/proj2/app")
    env_path = proj2_load_env(steps_to_project_root=1, dotenv="wrong-dir", default_env_filename='custom.env')
    assert os.getenv("SETTING") == "local_custom_dotenv_proj2"
    assert env_path == tests_dir / "proj2/app/custom.env"

    monkeypatch.setenv("DOTENV", "./tests/proj2/app/custom.env")
    env_path = proj2_load_env(steps_to_project_root=1, dotenv="wrong-dir", default_env_filename='.env')
    assert os.getenv("SETTING") == "local_custom_dotenv_proj2"
    assert env_path == tests_dir / "proj2/app/custom.env"


def test_pro1_use_unique_dotenv_file_with_custom_default_env_filename_param(setup_dotconfig_root, monkeypatch):
    env_path = proj1_load_env(dotenv=".", stage='other')
    assert os.getenv("SETTING") == "local_other_proj1"
    assert env_path == tests_dir / "proj1/.env.other"

def test_pro1_use_unique_dotenv_file_with_stage_param(setup_dotconfig_root, monkeypatch):
    monkeypatch.setenv("DOTSTAGE", "other")
    env_path = proj1_load_env(dotenv=".", stage='')
    assert os.getenv("SETTING") == "local_other_proj1"
    assert env_path == tests_dir / "proj1/.env.other"

    # DOTSTAGE env variable is empty but defined, use "default" DOTSTAGE:
    monkeypatch.setenv("DOTSTAGE", "")
    env_path = proj1_load_env(dotenv=".", stage='other')
    assert os.getenv("SETTING") == "local_proj1"
    assert env_path == tests_dir / "proj1/.env"

    # Use unique filename (.env), so DOTSTAGE is ignoring
    monkeypatch.setenv("DOTSTAGE", "other")
    env_path = proj1_load_env(dotenv=".env")
    assert os.getenv("SETTING") == "local_proj1"
    assert env_path == tests_dir / "proj1/.env"

def test_pro1_use_unique_dotenv_file_with_stage_env(setup_dotconfig_root, monkeypatch):
    monkeypatch.setenv("DOTENV", "./tests/proj1")
    env_path = proj1_load_env(steps_to_project_root=2, dotenv="wrong-dir/wrong-env")
    assert os.getenv("SETTING") == "local_proj1"
    assert env_path == tests_dir / "proj1/.env"

    monkeypatch.setenv("DOTENV", "./tests/proj1")
    monkeypatch.setenv("DOTSTAGE", "other")
    env_path = proj1_load_env(steps_to_project_root=3, dotenv="wrong-dir/.env")
    assert os.getenv("SETTING") == "local_other_proj1"
    assert env_path == tests_dir / "proj1/.env.other"

def test_proj2_use_unique_dotenv_file_with_env(setup_dotconfig_root, monkeypatch):
    # read a custom dotenv file using DOTENV environment variable
    monkeypatch.setenv("DOTENV", "tests/proj2/app/custom.env")
    env_path = proj2_load_env()
    assert os.getenv("SETTING") == "local_custom_dotenv_proj2"
    assert env_path == tests_dir / "proj2/app/custom.env"

    monkeypatch.setenv("DOTENV", "tests/proj2/app/")
    env_path = proj2_load_env(default_env_filename='custom.env')
    assert os.getenv("SETTING") == "local_custom_dotenv_proj2"
    assert env_path == tests_dir / "proj2/app/custom.env"

def test_proj2_wrong_unique_dotenv_file_with_param2(setup_dotconfig_root, monkeypatch):
    # read a custom dotenv file. 
    # NOTE:  The relative path resolved using the path to proj2/manage.py as an active directory
    with pytest.raises(FileNotFoundError):
       env_path = proj2_load_env(steps_to_project_root=0, dotenv=".")

    with pytest.raises(FileNotFoundError):
       env_path = proj2_load_env(steps_to_project_root=0, dotenv=Path())

    with pytest.raises(FileNotFoundError):
       env_path = proj2_load_env(steps_to_project_root=1, dotenv="./app")

def test_proj2_error_wrong_step_to_project_root(setup_dotconfig_root, monkeypatch):
    # proj2 has two directory levels:  proj2/app/.
    # It means that by default the project name will be 'app' and not 'proj2' 
    # .env file will be not found
    with pytest.raises(FileNotFoundError):
       env_path = proj2_load_env()

def test_proj2_dry_run_when_path_is_wrong(setup_dotconfig_root, monkeypatch, capsys):
    env_path = proj2_load_env(dry_run=True)
    assert os.getenv("SETTING") is None
    assert env_path is None

    monkeypatch.setenv("DOTVERBOSE", "ON")
    env_path = proj2_load_env(dry_run=True)
    captured = capsys.readouterr()
    dotenv_path1 = setup_dotconfig_root / "app/.env"
    dotenv_path2 = tests_dir / "proj2/app/.env"

    assert os.getenv("SETTING") is None
    assert env_path is None
    assert captured.out.strip() == f"No DOTENV file found. Paths checked: {dotenv_path1}, {dotenv_path2}"

def test_proj2_dry_run(setup_dotconfig_root, monkeypatch):
    # run load_env() in the `dry_run` mode
    env_path = proj2_load_env(steps_to_project_root=1, dry_run=True)
    # load nothing
    assert os.getenv("SETTING") is None
    # return the path to the detected .env file
    assert env_path == setup_dotconfig_root / "proj2/.env"

def test_proj2_default_env_loading(setup_dotconfig_root, monkeypatch):
    # read .env file from the default position
    env_path = proj2_load_env(steps_to_project_root=1)
    assert os.getenv("SETTING") == "default_proj2"
    assert env_path == setup_dotconfig_root / "proj2/.env"

def test_proj2_default_env_with_stage_param_loading(setup_dotconfig_root, monkeypatch):
    # read .env file from the default position for the given stage
    env_path = proj2_load_env(steps_to_project_root=1, stage='prod')
    assert os.getenv("SETTING") == "prod_proj2"
    assert env_path == setup_dotconfig_root / "proj2/.env.prod"

    # Use only basename of a parameter as stage name
    env_path = proj2_load_env(steps_to_project_root=1, stage='./blabla/blabla/staging')
    assert os.getenv("SETTING") == "staging_proj2"
    assert env_path == setup_dotconfig_root / "proj2/.env.staging"

    env_path = proj2_load_env(steps_to_project_root=1, stage='test')
    assert os.getenv("SETTING") == "test_proj2"
    assert env_path == setup_dotconfig_root / "proj2/.env.test"

def test_proj2_default_env_with_stage_env_loading(setup_dotconfig_root, monkeypatch):
    # Read .env file from the default position for the given stage
    monkeypatch.setenv("DOTSTAGE", "prod")
    env_path = proj2_load_env(steps_to_project_root=1)
    assert os.getenv("SETTING") == "prod_proj2"
    assert env_path == setup_dotconfig_root / "proj2/.env.prod"

    # Use only basename of a parameter as stage name
    # Environment variable has a higher prioritet than the function parameter
    monkeypatch.setenv("DOTSTAGE", "./blabla/blabla/staging")
    env_path = proj2_load_env(steps_to_project_root=1, stage='prod')
    assert os.getenv("SETTING") == "staging_proj2"
    assert env_path == setup_dotconfig_root / "proj2/.env.staging"

    monkeypatch.setenv("DOTSTAGE", "test")
    env_path = proj2_load_env(steps_to_project_root=1, stage='prod')
    assert os.getenv("SETTING") == "test_proj2"
    assert env_path == setup_dotconfig_root / "proj2/.env.test"

def test_proj2_use_custom_default_env_filename_with_param(setup_dotconfig_root, monkeypatch):
    # read a custom dotenv file
    env_path = proj2_load_env(default_env_filename="custom.env")
    assert os.getenv("SETTING") == "local_custom_dotenv_proj2"
    assert env_path == tests_dir / "proj2/app/custom.env"

def test_proj1_use_custom_default_env_filename_with_param2(setup_dotconfig_root, monkeypatch):
    # read a custom dotenv file: use only the name. All path will be truncated

    env_path = proj1_load_env(default_env_filename="/bla/bla/custom.env")
    assert os.getenv("SETTING") == "custom_env_proj1"
    assert env_path == setup_dotconfig_root / "proj1/custom.env"

def test_proj2_use_custom_default_env_filename_with_param3(setup_dotconfig_root, monkeypatch):
    # read a custom dotenv file: use only the name. All path will be truncated
    # for proj2 there is no custom env-file in the path:
    with pytest.raises(FileNotFoundError):
        env_path = proj2_load_env(steps_to_project_root=1, default_env_filename="/bla/bla/custom.env")

def test_proj2_use_custom_default_env_filename_and_project_param(setup_dotconfig_root, monkeypatch):
    # read a custom dotenv file: use only the name. All path will be truncated
    env_path = proj2_load_env(project="proj1", default_env_filename="custom.env")
    assert os.getenv("SETTING") == "custom_env_proj1"
    assert env_path == setup_dotconfig_root / "proj1/custom.env"

    monkeypatch.setenv("DOTPROJECT", "proj1")
    env_path = proj2_load_env(project="proj2", default_env_filename="custom.env")
    assert os.getenv("SETTING") == "custom_env_proj1"
    assert env_path == setup_dotconfig_root / "proj1/custom.env"

    monkeypatch.setenv("DOTPROJECT", "proj1")
    env_path = proj2_load_env(project="proj2", stage='test', default_env_filename="custom.env")
    assert os.getenv("SETTING") == "custom_env_test_proj1"
    assert env_path == setup_dotconfig_root / "proj1/custom.env.test"

def test_proj1_use_custom_config_root_with_param(setup_dotconfig_root, monkeypatch):
    # read a custom dotenv file from the different config root. 
    # NOTE:  The relative path resolved using the path to proj2/manage.py as an active directory
    env_path = proj1_load_env(config_root="../other_config_root")
    assert os.getenv("SETTING") == "other_default_proj1"
    assert env_path == tests_dir / "other_config_root/proj1/.env"

def test_proj1_use_custom_config_root_with_env_var(setup_dotconfig_root, monkeypatch):
    # read a custom dotenv file from the DOTCONFIG_ROOT environment variable. 
    monkeypatch.setenv("DOTCONFIG_ROOT", "tests/other_config_root")
    env_path = proj1_load_env(config_root="wrong-path/config_root")
    assert os.getenv("SETTING") == "other_default_proj1"
    assert env_path == tests_dir / "other_config_root/proj1/.env"

def test_proj2_use_custom_config_root_and_projectname_with_param(setup_dotconfig_root, monkeypatch):
    # read a custom dotenv file from the different config root. 
    # NOTE:  The relative path resolved using the path to proj2/manage.py as an active directory
    env_path = proj2_load_env(config_root="../../other_config_root", project="other-proj")
    assert os.getenv("SETTING") == "other_default_other_proj"
    assert env_path == tests_dir / "other_config_root/other-proj/.env"

    # Use Path instead of string 
    env_path = proj2_load_env(config_root=Path("../../other_config_root"), project="other-proj")
    assert os.getenv("SETTING") == "other_default_other_proj"
    assert env_path == tests_dir / "other_config_root/other-proj/.env"

def test_proj2_use_custom_config_root_and_steps_to_projects_root(setup_dotconfig_root, monkeypatch):
    # read a custom dotenv file from the different config root. 
    # NOTE:  The relative path resolved using the path to proj2/manage.py as an active directory
    env_path = proj2_load_env(config_root="../../other_config_root", steps_to_project_root=0, project="proj2")
    assert os.getenv("SETTING") == "other_default_proj2"
    assert env_path == tests_dir / "other_config_root/proj2/.env"

    env_path = proj2_load_env(config_root="../other_config_root", steps_to_project_root=1)
    assert os.getenv("SETTING") == "other_default_proj2"
    assert env_path == tests_dir / "other_config_root/proj2/.env"

    env_path = proj2_load_env(config_root="other_config_root", steps_to_project_root=2, project="proj2")
    assert os.getenv("SETTING") == "other_default_proj2"
    assert env_path == tests_dir / "other_config_root/proj2/.env"

def test_proj2_use_custom_config_root_and_projectname_with_env_var(setup_dotconfig_root, monkeypatch):
    # read a custom dotenv file from the different config root. 

    monkeypatch.setenv("DOTCONFIG_ROOT", "tests/other_config_root")
    env_path = proj2_load_env(steps_to_project_root=1)
    assert os.getenv("SETTING") == "other_default_proj2"
    assert env_path == tests_dir / "other_config_root/proj2/.env"

    monkeypatch.setenv("DOTCONFIG_ROOT", "tests/other_config_root")
    env_path = proj2_load_env(config_root="wrong-path-to/other_config_root", project="other-proj")
    assert os.getenv("SETTING") == "other_default_other_proj"
    assert env_path == tests_dir / "other_config_root/other-proj/.env"

    monkeypatch.setenv("DOTCONFIG_ROOT", "tests/other_config_root")
    monkeypatch.setenv("DOTPROJECT", "proj1")
    env_path = proj2_load_env(config_root="wrong-path-to/other_config_root", project="other-proj")
    assert os.getenv("SETTING") == "other_default_proj1"
    assert env_path == tests_dir / "other_config_root/proj1/.env"

    monkeypatch.setenv("DOTCONFIG_ROOT", "tests/other_config_root")
    monkeypatch.setenv("DOTPROJECT", "proj1")
    monkeypatch.setenv("DOTSTAGE", "test")
    env_path = proj2_load_env(config_root="wrong-path-to/other_config_root", project="other-proj")
    assert os.getenv("SETTING") == "other_test_proj1"
    assert env_path == tests_dir / "other_config_root/proj1/.env.test"

def test_proj1_use_custom_config_root_and_custom_env_file_name(setup_dotconfig_root, monkeypatch):
    # read a custom dotenv file from the different config root. 
    # NOTE:  The relative path resolved using the path to proj2/manage.py as an active directory
    env_path = proj1_load_env(config_root="../other_config_root", default_env_filename="custom.env")
    assert os.getenv("SETTING") == "other_custom_env_default_proj1"
    assert env_path == tests_dir / "other_config_root/proj1/custom.env"

    # With stage='test':
    env_path = proj1_load_env(stage="test", config_root="../other_config_root", default_env_filename="custom.env")
    assert os.getenv("SETTING") == "other_custom_env_test_proj1"
    assert env_path == tests_dir / "other_config_root/proj1/custom.env.test"

def test_proj1_use_custom_config_root_and_custom_env_file_name_env_vars(setup_dotconfig_root, monkeypatch):
    # read a custom dotenv file from the different config root. 
    # NOTE:  The relative path resolved using the path to proj2/manage.py as an active directory
    monkeypatch.setenv("DOTCONFIG_ROOT", "tests/other_config_root")
    env_path = proj1_load_env(config_root="wrong-path-to/other_config_root", default_env_filename="custom.env")
    assert os.getenv("SETTING") == "other_custom_env_default_proj1"
    assert env_path == tests_dir / "other_config_root/proj1/custom.env"

    # With stage='test':
    monkeypatch.setenv("DOTCONFIG_ROOT", "tests/other_config_root")
    monkeypatch.setenv("DOTSTAGE", "test")
    env_path = proj1_load_env(stage="prod", config_root="wrong-path-to/other_config_root", default_env_filename="custom.env")
    assert os.getenv("SETTING") == "other_custom_env_test_proj1"
    assert env_path == tests_dir / "other_config_root/proj1/custom.env.test"

def test_verbose_env(setup_dotconfig_root, monkeypatch, capsys):
    monkeypatch.setenv("DOTCONFIG_ROOT", "tests/other_config_root")

    # Test no verbose output
    env_path = proj1_load_env()
    captured = capsys.readouterr()
    assert captured.out.strip() == ""

    # Test verbose output  1
    monkeypatch.setenv("DOTVERBOSE", "1")
    env_path = proj1_load_env()
    dotenv_path = tests_dir / "other_config_root/proj1/.env"
    captured = capsys.readouterr()
    assert captured.out.strip() == f"Use DOTENV file from {dotenv_path}"

    # Test verbose output  True
    monkeypatch.setenv("DOTVERBOSE", "True")
    env_path = proj1_load_env(config_root="wrong/other_config_root")  # use DOTCONFIG_ROOT
    dotenv_path = tests_dir / "other_config_root/proj1/.env"
    captured = capsys.readouterr()
    assert captured.out.strip() == f"Use DOTENV file from {dotenv_path}"

    # Test verbose output  TRUE
    monkeypatch.setenv("DOTVERBOSE", "TRUE")
    env_path = proj1_load_env()
    dotenv_path = tests_dir / "other_config_root/proj1/.env"
    captured = capsys.readouterr()
    assert captured.out.strip() == f"Use DOTENV file from {dotenv_path}"

    # Test verbose output  true
    monkeypatch.setenv("DOTVERBOSE", "true")
    env_path = proj1_load_env()
    dotenv_path = tests_dir / "other_config_root/proj1/.env"
    captured = capsys.readouterr()
    assert captured.out.strip() == f"Use DOTENV file from {dotenv_path}"

    # Test verbose output  tRuE
    monkeypatch.setenv("DOTVERBOSE", "tRuE")
    env_path = proj1_load_env()
    dotenv_path = tests_dir / "other_config_root/proj1/.env"
    captured = capsys.readouterr()
    assert captured.out.strip() == f"Use DOTENV file from {dotenv_path}"

    # Test verbose output  Yes
    monkeypatch.setenv("DOTVERBOSE", "Yes")
    env_path = proj1_load_env()
    dotenv_path = tests_dir / "other_config_root/proj1/.env"
    captured = capsys.readouterr()
    assert captured.out.strip() == f"Use DOTENV file from {dotenv_path}"

    # Test verbose output  ON
    monkeypatch.setenv("DOTVERBOSE", "ON")
    env_path = proj1_load_env()
    dotenv_path = tests_dir / "other_config_root/proj1/.env"
    captured = capsys.readouterr()
    assert captured.out.strip() == f"Use DOTENV file from {dotenv_path}"

    # Test verbose output  ja
    monkeypatch.setenv("DOTVERBOSE", "ja")
    env_path = proj1_load_env()
    dotenv_path = tests_dir / "other_config_root/proj1/.env"
    captured = capsys.readouterr()
    assert captured.out.strip() == f"Use DOTENV file from {dotenv_path}"


    # Test no verbose output  false
    monkeypatch.setenv("DOTVERBOSE", "false")
    env_path = proj1_load_env()
    captured = capsys.readouterr()
    assert captured.out.strip() == ""

    # Test no verbose output  any-other-text
    monkeypatch.setenv("DOTVERBOSE", "any-other-text")
    env_path = proj1_load_env()
    captured = capsys.readouterr()
    assert captured.out.strip() == ""

def test_verbose_from_env_file(setup_dotconfig_root, monkeypatch, capsys):
    monkeypatch.setenv("DOTCONFIG_ROOT", "tests/other_config_root")
    monkeypatch.setenv("DOTSTAGE", "test")

    # Test verbose output from the custom.env.test file (DOTVERBOSE=True)
    monkeypatch.delenv("DOTVERBOSE", raising=False)
    env_path = proj1_load_env(stage="test", config_root="wrond/other_config_root", default_env_filename="custom.env")
    dotenv_path = tests_dir / "other_config_root/proj1/custom.env.test"
    captured = capsys.readouterr()
    assert env_path == dotenv_path
    assert captured.out.strip() == f"Use DOTENV file from {env_path}"

    # Test verbose output from the .env.test file (DOTVERBOSE=False)
    monkeypatch.delenv("DOTVERBOSE", raising=False)
    env_path = proj1_load_env(stage="test")
    dotenv_path = tests_dir / "other_config_root/proj1/.env.test"
    captured = capsys.readouterr()
    assert env_path == dotenv_path
    assert captured.out.strip() == ""

    # The DOTVERBOSE environment variable takes precedence over DOTVERBOSE defined in a .env file:
    monkeypatch.setenv("DOTVERBOSE", "wrong-value-disable-dotverbose")
    env_path = proj1_load_env(stage="test", config_root="wrond/other_config_root", default_env_filename="custom.env")
    dotenv_path = tests_dir / "other_config_root/proj1/custom.env.test"
    captured = capsys.readouterr()
    assert captured.out.strip() == ""

    monkeypatch.setenv("DOTVERBOSE", "Ja")
    env_path = proj1_load_env(stage="test")
    captured = capsys.readouterr()
    assert captured.out.strip() == f"Use DOTENV file from {env_path}"

