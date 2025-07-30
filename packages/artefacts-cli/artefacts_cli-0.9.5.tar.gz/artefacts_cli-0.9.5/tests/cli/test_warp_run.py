import pytest

import json

from requests import Response

from artefacts.cli import ArtefactsAPIError, AuthenticationError, WarpJob, WarpRun


def test_run_with_upload_on_stop(mocker, artefacts_run):
    """
    Check that `uploads` list is registered to the API when stopping a run.
    """
    # This mock depends too much on the actual implementation, and will need
    # refactoring. For now, it tries to be "minimal". Stopping involves
    # registering run metadata and notably a list of artefacts to upload. This
    # happens currently in two steps and why this mock is weak (it needs to
    # know of this whole works).
    #
    # The first step is what we test here: Is the registration containing the
    # `uploads` entry. The second step is mocked here to ensure completion of the `stop` function.
    spy = mocker.patch.object(artefacts_run.job.api_conf, "update")

    completion_helper = Response()
    completion_helper.status_code = 200
    completion_helper.raw = json.dumps({"upload_urls": "http://test.com"})
    mocker.patch("requests.post", return_value=completion_helper)

    artefacts_run.job.dryrun = False
    artefacts_run.stop()

    assert "uploads" in spy.call_args.args[2]


def test_run_without_upload_on_stop(mocker, artefacts_run):
    """
    Check that `uploads` list is not registered to the API when stopping a run
    for a job that specifies the `noupload` option.

    This is required by the API protocol.
    """
    spy = mocker.patch.object(artefacts_run.job.api_conf, "update")

    artefacts_run.job.dryrun = False
    artefacts_run.job.noupload = True
    artefacts_run.stop()

    assert "uploads" not in spy.call_args.args[2]


def test_run_uses_scenario_name(mocker, artefacts_job):
    """
    The API protocol stipulates run creation now needs to specify a scenario
    name, passed as a `scenario_name` entry in the payload.
    """
    expected_name = "scenario test"

    _success = Response()
    _success.status_code = 200
    spy = mocker.patch.object(artefacts_job.api_conf, "create", return_value=_success)
    artefacts_job.dryrun = False
    WarpRun(job=artefacts_job, name=expected_name, params={}, run_n=0)

    assert "scenario_name" in spy.call_args.args[1]
    assert expected_name == spy.call_args.args[1]["scenario_name"]


def test_run_uses_common_scenario_name_for_all_parameterised_runs(
    mocker, artefacts_job
):
    """
    The code currently overwrites scenario parameters, notably their names, to guarantee unique names (1 scenario <=> 1 run). This happens only on run-remote at this time (see artefacts/cli/app.py around line 555).

    This test reproduces the conditions executed when run-remote changes the scenario name in the parameters. It checks that the params are as expected (unique names) yet the run object uses a common scenario name.
    """
    expected_name = "scenario test"

    _success = Response()
    _success.status_code = 200
    spy = mocker.patch.object(artefacts_job.api_conf, "create", return_value=_success)
    artefacts_job.dryrun = False

    # The check must be on at least 2 run objects to ensure the common name.
    for idx in range(2):
        WarpRun(
            job=artefacts_job,
            name=expected_name,
            params={"name": f"{expected_name}-{idx}"},
            run_n=idx,
        )
        assert "scenario_name" in spy.call_args.args[1]
        assert expected_name == spy.call_args.args[1]["scenario_name"]


def test_run_uses_scenario_name_on_stop(mocker, artefacts_run):
    """
    The API protocol stipulates run stop now needs to specify a scenario name,
    passed as a `scenario_name` entry in the payload.
    """
    expected_name = "scenario test"

    spy = mocker.patch.object(artefacts_run.job.api_conf, "update")

    artefacts_run.job.dryrun = False
    artefacts_run.job.noupload = True
    artefacts_run.scenario_name = expected_name
    artefacts_run.stop()

    assert "scenario_name" in spy.call_args.args[2]
    assert expected_name == spy.call_args.args[2]["scenario_name"]


def test_run_uses_scenario_name_on_stop_for_all_parameterised_runs(
    mocker, artefacts_job
):
    """
    This test reproduces the conditions executed when run-remote changes the scenario name in the parameters, on run creation (see test `test_run_uses_common_scenario_name_for_all_parameterised_runs`) and on run stop as addressed here.

    The checks that the stop params are as expected (unique names) yet the run object uses a common scenario name.
    """
    expected_name = "scenario test"

    artefacts_job.noupload = True
    artefacts_job.dryrun = False

    _success = Response()
    _success.status_code = 200
    mocker.patch.object(artefacts_job.api_conf, "create", return_value=_success)
    spy = mocker.patch.object(artefacts_job.api_conf, "update")

    # The check must be on at least 2 run objects to ensure the common name.
    for idx in range(2):
        run = WarpRun(
            job=artefacts_job,
            name=expected_name,
            params={"name": f"{expected_name}-{idx}"},
            run_n=idx,
        )
        run.stop()
        assert "scenario_name" in spy.call_args.args[2]
        assert expected_name == spy.call_args.args[2]["scenario_name"]


def test_run_creation_403(mocker):
    """
    Check bad authentication is handled.
    """
    success = mocker.Mock()
    success.status_code = 200
    success.json.return_value = {"job_id": "test"}
    error403 = mocker.Mock()
    error403.status_code = 403
    error403.json.return_value = {"message": "bad auth"}

    def behaviour(obj, data):
        if "job" == obj:
            return success
        elif "run" == obj:
            return error403

    api_conf = mocker.Mock()
    api_conf.create = mocker.Mock(side_effect=behaviour)
    job = WarpJob(
        "project",
        api_conf,
        "jobname",
        {},
    )
    with pytest.raises(AuthenticationError) as error:
        WarpRun(job=job, name="run", params={}, run_n=1)
        assert "bad auth" in str(error)


def test_run_creation_non_403_error(mocker):
    """
    Check non-403 errors are handled.
    """
    success = mocker.Mock()
    success.status_code = 200
    success.json.return_value = {"job_id": "test"}
    error401 = mocker.Mock()
    error401.status_code = 401

    def behaviour(obj, data):
        if "job" == obj:
            return success
        elif "run" == obj:
            return error401

    api_conf = mocker.Mock()
    api_conf.create = mocker.Mock(side_effect=behaviour)
    job = WarpJob(
        "project",
        api_conf,
        "jobname",
        {},
    )
    with pytest.raises(ArtefactsAPIError) as error:
        WarpRun(job=job, name="run", params={}, run_n=1)
        assert "401" in str(error)
