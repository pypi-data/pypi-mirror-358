import pytest

from pathlib import Path
import webbrowser

import yaml

from artefacts.cli.app import (
    hello,
    run,
    run_remote,
    add,
)
from artefacts.cli.config import APIConf


def test_hello(cli_runner):
    project_name = "project_without_key"
    result = cli_runner.invoke(hello, [project_name])
    assert result.exit_code == 1
    assert result.output == (
        f"Error: No API KEY set. Please run `artefacts config add {project_name}`\n"
    )


def test_local_config_plain(cli_runner, mocker, api_exists, valid_project_settings):
    # Do not open a browser in test mode.
    mocker.patch("webbrowser.open")
    result = cli_runner.invoke(
        add, [valid_project_settings["full_project_name"]], input="MYAPIKEY\n"
    )
    # Ensure the script has attempted to open the browser as intended
    webbrowser.open.assert_called_once()

    # Check CLI output
    assert result.output == (
        f"Opening the project settings page: https://app.artefacts.com/{valid_project_settings['org']}/{valid_project_settings['project']}/settings\n"
        f"Please enter your API KEY for {valid_project_settings['org']}/{valid_project_settings['project']}: \n"
        f"API KEY saved for {valid_project_settings['org']}/{valid_project_settings['project']}\n"
        "Would you like to download a pregenerated artefacts.yaml file? This will overwrite any existing config file in the current directory. [y/N]: \n"
    )


def test_local_config_download_config(
    cli_runner, mocker, api_exists, valid_project_settings
):
    # Do not open a browser in test mode.
    mocker.patch("webbrowser.open")
    # Accept downloading the generated artefacts.yaml
    mocker.patch("click.confirm", return_value=True)
    # Controlled artefacts.yaml content
    valid_config = {
        "version": "0.1.0",
        "project": valid_project_settings["full_project_name"],
    }

    class ValidResponse:
        def __init__(self):
            self.content = bytes(yaml.dump(valid_config).encode("ascii"))
            self.status_code = 200

    mocker.patch("artefacts.cli.config.APIConf.read", return_value=ValidResponse())

    with cli_runner.isolated_filesystem():
        cli_runner.invoke(
            add, [valid_project_settings["full_project_name"]], input="MYAPIKEY\n"
        )
        artefacts_yaml = Path("artefacts.yaml")

        assert artefacts_yaml.exists(), (
            f"expected {artefacts_yaml.absolute()} file is missing"
        )

        # Parse the downloaded file to check basic content
        with open(artefacts_yaml) as f:
            config = yaml.load(f, Loader=yaml.Loader)

        assert config["version"] == valid_config["version"]
        assert config["project"] == valid_config["project"]


def test_local_config_failed_api_access(
    cli_runner, mocker, api_doesnt_exist, valid_project_settings
):
    # Ensure we don't collide with any existing file
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(
            add, [valid_project_settings["full_project_name"]], input="MYAPIKEY\n"
        )

        artefacts_yaml = Path("artefacts.yaml")

        assert not artefacts_yaml.exists(), (
            f"{artefacts_yaml.absolute()} file should not exit"
        )
        assert (
            f"Our apologies: The project page does not seem available at the moment. If `{valid_project_settings['org']}/{valid_project_settings['project']}` is correct, please try again later.\nIf you are using an alternative server, please also consider checking the value of ARTEFACTS_API_URL in your environment."
            in result.output
        )


def test_local_config_failed_download_config(
    cli_runner, mocker, api_exists, valid_project_settings
):
    # Do not open a browser in test mode.
    mocker.patch("webbrowser.open")
    # Accept downloading the generated artefacts.yaml
    mocker.patch("click.confirm", return_value=True)

    # Invalid artefacts.yaml content
    class InvalidResponse:
        def __init__(self):
            self.content = bytes("whatever that is not YAML".encode("ascii"))
            self.status_code = 500  # Anything but 200

    mocker.patch("artefacts.cli.config.APIConf.read", return_value=InvalidResponse())

    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(
            add, [valid_project_settings["full_project_name"]], input="MYAPIKEY\n"
        )

        # artefacts_yaml = Path("artefacts.yaml")

        # assert not artefacts_yaml.exists()
        assert (
            f"We encountered a problem in getting the generated configuration file. Please consider downloading it from the project page on the dashboard at https://app.artefacts.com/{valid_project_settings['org']}/{valid_project_settings['project']}/settings. Sorry for the inconvenience."
            in result.output
        )


def test_run(cli_runner):
    result = cli_runner.invoke(run, ["tests", "--config", "myconf.yaml"])
    assert result.exit_code == 1
    assert result.output == ("Error: Project config file myconf.yaml not found.\n")


def test_run_with_conf_invalid_jobname(cli_runner, authorised_project_with_conf):
    job_name = "invalid_job_name"
    result = cli_runner.invoke(
        run, [job_name, "--config", authorised_project_with_conf]
    )
    assert result.exit_code == 1
    assert result.output == (
        f"[{job_name}] Connecting to https://app.artefacts.com/api using ApiKey\n"
        f"[{job_name}] Starting tests\n"
        f"[{job_name}] Error: Job name not defined\n"
        "Aborted!\n"
    )


def test_run_with_conf(cli_runner, authorised_project_with_conf):
    result = cli_runner.invoke(
        run, ["simple_job", "--config", authorised_project_with_conf, "--dryrun"]
    )
    assert result.exit_code == 0
    assert result.output == (
        "[simple_job] Connecting to https://app.artefacts.com/api using ApiKey\n"
        "[simple_job] Starting tests\n"
        "[simple_job] Starting scenario 1/2: basic-tests\n"
        "[simple_job] Performing dry run\n"
        "[simple_job] Starting scenario 2/2: other-tests\n"
        "[simple_job] Performing dry run\n"
        "[simple_job] Done\n"
    )


@pytest.mark.skip(
    reason="Non-ROS unsupported in CoPaVa at this time. Non-ROS like Sapien, etc, become unrunnable then."
)
def test_run_with_mode_other(cli_runner, valid_project_settings):
    result = cli_runner.invoke(
        run,
        ["simple_job", "--config", "tests/fixtures/warp-env-param.yaml", "--dryrun"],
    )
    assert result.exit_code == 0
    assert result.output == (
        "Connecting to https://app.artefacts.com/api using ApiKey\n"
        f"Starting tests for {valid_project_settings['org']}/{valid_project_settings['project']}\n"
        "Starting scenario 1/2: basic-tests\n"
        "performing dry run\n"
        "Starting scenario 2/2: other-tests\n"
        "performing dry run\n"
        "Done\n"
    )


def test_run_remote(cli_runner):
    result = cli_runner.invoke(run_remote, ["tests", "--config", "conf.yaml"])
    assert result.exit_code == 1
    assert result.output == "Error: Project config file conf.yaml not found.\n"


def test_run_remote_with_conf_invalid_jobname(cli_runner, authorised_project_with_conf):
    result = cli_runner.invoke(
        run_remote, ["invalid_job_name", "--config", authorised_project_with_conf]
    )
    assert result.exit_code == 1
    assert result.output == (
        "Connecting to https://app.artefacts.com/api using ApiKey\n"
        f"Error: Can't find a job named 'invalid_job_name' in config '{authorised_project_with_conf}'\n"
    )


def test_APIConf(valid_project_settings):
    conf = APIConf(valid_project_settings["full_project_name"], "test_version")
    assert conf.headers["Authorization"] == "ApiKey MYAPIKEY"


def test_upload_default_dir(cli_runner, authorised_project_with_conf, mocker):
    # Note the patch applies to the object loaded in app, rather than the original in utils.
    # https://docs.python.org/3/library/unittest.mock.html#where-to-patch
    sut = mocker.patch("artefacts.cli.app.add_output_from_default")
    result = cli_runner.invoke(
        run, ["simple_job", "--config", authorised_project_with_conf, "--dryrun"]
    )
    assert result.exit_code == 0
    # Called twice in this config.
    assert sut.call_count == 2
