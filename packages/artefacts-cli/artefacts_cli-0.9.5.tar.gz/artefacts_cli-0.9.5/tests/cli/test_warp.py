import pytest
from datetime import datetime, timezone
from uuid import uuid4


from artefacts.cli import (
    ArtefactsAPIError,
    AuthenticationError,
    generate_scenarios,
    WarpJob,
)
from artefacts.cli.app import run
from artefacts.cli.config import APIConf


def test_generate_scenarios(loaded_valid_conf):
    """
    Ensure scenarios (vague, runs too) get generated as expected when
    the configuration includes parameterised settings.
    """
    jobs = loaded_valid_conf["jobs"]
    scenarios, first = generate_scenarios(jobs["simple_job"])
    assert len(scenarios) == 2
    scenarios, first = generate_scenarios(jobs["tests"])
    assert first == 0
    assert len(scenarios) == 5
    jobs["simple_job"]["scenarios"]["defaults"] = {"params": {}}
    scenarios, first = generate_scenarios(jobs["simple_job"])
    assert len(scenarios) == 2
    scenarios, first = generate_scenarios(jobs["simple_job"], 0)
    assert len(scenarios) == 1
    scenarios, first = generate_scenarios(jobs["simple_job"], 1)
    assert len(scenarios) == 1
    scenarios, first = generate_scenarios(jobs["tests"], 1)
    assert len(scenarios) == 3
    scenarios, first = generate_scenarios(jobs["tests"], 0)
    assert len(scenarios) == 2
    # assert 1 == 2


def test_default_params_only(loaded_valid_conf):
    """
    Testing scenarios inherit default params.
    """
    jobs = loaded_valid_conf["jobs"]
    # testing with just default params
    scenarios, first = generate_scenarios(jobs["default_params_only"])
    assert len(scenarios) == 2
    assert [s["params"] for s in scenarios] == [
        {"seed": 42},
        {"seed": 43},
    ]


def test_settings_params_only(loaded_valid_conf):
    """
    Testing scenarios are well set with their direct params (not inherited
    from defaults).
    """
    jobs = loaded_valid_conf["jobs"]
    # testing with just default params
    scenarios, first = generate_scenarios(jobs["settings_params_only"])
    assert len(scenarios) == 2
    assert [s["params"] for s in scenarios] == [
        {"seed": 42},
        {"seed": 43},
    ]


def test_settings_and_default_params(loaded_valid_conf):
    """
    Testing scenarios are well configured with defaults and own params.
    """
    jobs = loaded_valid_conf["jobs"]
    # testing with both settings and default params
    scenarios, first = generate_scenarios(jobs["settings_and_default_params"])
    assert len(scenarios) == 4
    assert [s["params"] for s in scenarios] == [
        {"gravity": 1.62, "seed": 42},
        {"gravity": 1.62, "seed": 43},
        {"gravity": 0, "seed": 42},
        {"gravity": 0, "seed": 43},
    ]


def test_default_params_overwritten_by_settings(loaded_valid_conf):
    """
    Testing with settings that overwrite default params
    """
    jobs = loaded_valid_conf["jobs"]
    scenarios, first = generate_scenarios(jobs["settings_overwrite_default_params"])
    assert len(scenarios) == 2
    assert [s["params"] for s in scenarios] == [
        {"gravity": 1.62, "seed": 42},
        {"gravity": 0, "seed": 42},
    ]


def test_default_params_overwritten_by_settings2(loaded_valid_conf):
    """
    Testing with settings that overwrite default params on two scenarios
    """
    jobs = loaded_valid_conf["jobs"]
    scenarios, first = generate_scenarios(jobs["settings_overwrite_full"])
    assert len(scenarios) == 5
    assert [s["params"] for s in scenarios] == [
        {"gravity": 9.807, "seed": 42},
        {"gravity": 1.62, "seed": 42},
        {"gravity": 0, "seed": 42},
        {"gravity": 1.62, "seed": 42},
        {"gravity": 0, "seed": 42},
    ]


def test_default_params_overwritten_by_launch_argument(loaded_valid_conf):
    """
    Testing explicit launch arguments override default params.
    """
    jobs = loaded_valid_conf["jobs"]
    scenarios, _ = generate_scenarios(jobs["handles_launch_arguments"])
    assert len(scenarios) == 1
    assert scenarios[0]["launch_arguments"] == {
        "gravity": "9.807",
        "seed": "42",
        "target": "goal",
    }


def test_job_empty_init_dryrun():
    """
    Plain basic test the WarpJob object initialises as expected on dryrun.
    """
    job = WarpJob("project", {}, "jobname", {}, dryrun=True)
    assert job.success is False
    assert job.start < datetime.now(timezone.utc).timestamp()


def test_job_empty_init(mocker, valid_project_settings):
    """
    Plain basic test the WarpJob object initialises as expected.
    """
    success = mocker.Mock()
    success.status_code = 200
    success.json.return_value = {"job_id": str(uuid4())}
    test_session = mocker.Mock()
    test_session.post.return_value = success
    job = WarpJob(
        "project",
        APIConf(
            valid_project_settings["full_project_name"],
            "test_version",
            session=test_session,
        ),
        "jobname",
        {},
    )
    assert job.success is False
    assert job.start < datetime.now(timezone.utc).timestamp()


def test_job_update(mocker, valid_project_settings):
    """
    Test on the update function of WarpJob objects.
    """
    success = mocker.Mock()
    success.status_code = 200
    success.json.return_value = {"job_id": str(uuid4())}
    test_session = mocker.Mock()
    test_session.post.return_value = success
    test_session.put.return_value = success
    job = WarpJob(
        "project",
        APIConf(
            valid_project_settings["full_project_name"],
            "test_version",
            session=test_session,
        ),
        "jobname",
        {},
    )
    assert job.update(True)


def test_job_valid_context(mocker, valid_project_settings):
    """
    Check that a custom context param is processed as expected.

    A job creation currently invokes the API at init time,
    which is supposed to send any optional `context` data.
    """
    now = datetime.now()
    time_mock = mocker.patch("datetime.datetime")
    time_mock.now.return_value = now
    success = mocker.Mock()
    success.status_code = 200
    success.json.return_value = {"job_id": str(uuid4())}
    api_conf = mocker.Mock()
    api_conf.create = mocker.Mock(return_value=success)
    WarpJob(
        "project",
        api_conf,
        "jobname",
        {},
        context={
            "description": "test",
            "commit": "testcommithash",
            "ref": "testref",
        },
    )
    api_conf.create.assert_called_with(
        "job",
        dict(
            project_id="project",
            start=round(now.timestamp()),
            status="in progress",
            params="{}",
            project="project",
            jobname="jobname",
            timeout=300,
            n_subjobs=1,
            message="test",
            commit="testcommithash",
            ref="testref",
        ),
    )


def test_job_creation_403(mocker):
    """
    Check bad authentication is handled.
    """
    error403 = mocker.Mock()
    error403.status_code = 403
    error403.json.return_value = {"message": "bad auth"}
    api_conf = mocker.Mock()
    api_conf.create = mocker.Mock(return_value=error403)
    with pytest.raises(AuthenticationError) as error:
        WarpJob(
            "project",
            api_conf,
            "jobname",
            {},
        )
        assert "bad auth" in str(error)


def test_job_creation_non_403_error(mocker):
    """
    Check non-403 errors are handled.
    """
    error401 = mocker.Mock()
    error401.status_code = 401
    api_conf = mocker.Mock()
    api_conf.create = mocker.Mock(return_value=error401)
    with pytest.raises(ArtefactsAPIError) as error:
        WarpJob(
            "project",
            api_conf,
            "jobname",
            {},
        )
        assert "401" in str(error)


@pytest.mark.ros2
def test_job_update_called_after_every_run(
    cli_runner, authorised_project_with_conf, mocker
):
    """
    Test to confirm Dashboard API is updated after each run in a job
    """
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"job_id": "test_job_id", "upload_urls": {}}
    mocker.patch("artefacts.cli.config.APIConf.create", return_value=mock_response)
    mocker.patch("artefacts.cli.config.APIConf.update", return_value=mock_response)

    # Count calls to WarpJob.update
    update_spy = mocker.spy(WarpJob, "update")

    cli_runner.invoke(run, ["tests", "--config", authorised_project_with_conf])

    # We expect 5 runs total accross 2 scenarios:
    # 2 from "basic-tests" and 3 from "param-grid"
    expected_update_calls = 5

    assert update_spy.call_count == expected_update_calls
