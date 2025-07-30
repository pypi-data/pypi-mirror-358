from collections.abc import Callable
from contextlib import contextmanager
from functools import partial
import logging
import os
import platform
from typing import Optional, Tuple

import click
from requests import Response, Session
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
from urllib3.util import Retry

from artefacts.cli.i18n import localise
from artefacts.cli.helpers import (
    get_conf_from_file,
    get_artefacts_api_url,
)

# Mask warnings from urllib, typically when it retries failed API calls
urllib3logger = logging.getLogger("urllib3")
urllib3logger.setLevel(logging.ERROR)


class APIConf:
    def __init__(
        self,
        project_name: str,
        api_version: str,
        job_name: Optional[str] = None,
        session: Optional[Session] = None,
    ) -> None:
        config = get_conf_from_file()
        if project_name in config:
            profile = config[project_name]
        else:
            profile = {}
        self.api_url = get_artefacts_api_url(profile)
        self.api_key = os.environ.get("ARTEFACTS_KEY", profile.get("ApiKey", None))
        if self.api_key is None:
            batch_id = os.environ.get("AWS_BATCH_JOB_ID", None)
            job_id = os.environ.get("ARTEFACTS_JOB_ID", None)
            if batch_id is None or job_id is None:
                raise click.ClickException(
                    localise(
                        "No API KEY set. Please run `artefacts config add {project_name}`".format(
                            project_name=project_name
                        )
                    )
                )
            auth_type = "Internal"
            # Batch id for array jobs contains array index
            batch_id = batch_id.split(":")[0]
            self.headers = {"Authorization": f"{auth_type} {job_id}:{batch_id}"}
        else:
            auth_type = "ApiKey"
            self.headers = {"Authorization": f"{auth_type} {self.api_key}"}
        self.headers["User-Agent"] = (
            f"ArtefactsClient/{api_version} ({platform.platform()}/{platform.python_version()})"
        )
        if job_name:
            click.echo(
                f"[{job_name}] "
                + localise(
                    "Connecting to {api_url} using {auth_type}".format(
                        api_url=self.api_url, auth_type=auth_type
                    )
                )
            )
        else:
            click.echo(
                localise(
                    "Connecting to {api_url} using {auth_type}".format(
                        api_url=self.api_url, auth_type=auth_type
                    )
                )
            )

        #
        # Retry settings
        #
        self.session = session or Session()
        retries = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[502, 503, 504],
            allowed_methods=Retry.DEFAULT_ALLOWED_METHODS | {"POST"},
        )
        # Default connect timeout set to a small value above the default 3s for TCP
        # Default read timeout a typical value. Does not scale when too aggressive
        #    (note: read timeout is between byte sent, not the whole read)
        self.request_timeout = (3.03, 27)
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    @contextmanager
    def _api(self):
        try:
            yield self.session
        except ConnectionError as e:
            raise click.ClickException(
                localise(
                    "Unable to complete the operation: Network error.\n"
                    "This may be a problem with an Artefacts server, or your network.\n"
                    "Please try again in a moment or confirm your internet connection.\n"
                    "If the problem persists, please contact us (info@artefacts.com)!\n"
                    f"All we know: {e}"
                )
            )

    def _conn_info(self, obj: str, data: Optional[dict] = None) -> Tuple[str, dict]:
        """
        Prepare connection information for a given resource kind (`obj`).

        Returns a tuple (url, payload), where url is the endpoint for
        the resource, and payload the prepared data that needs be sent.

        Note the prepared data does not validate the content. It simply
        remove any extra data used internally to the code here.
        """
        try:
            if "url" == obj:
                return obj, None
            elif "job" == obj:
                return f"{self.api_url}/{data['project_id']}/job", data
            elif "run" == obj:
                project_id = data.pop("project_id")
                return f"{self.api_url}/{project_id}/job/{data['job_id']}/run", data
            else:
                raise Exception(
                    f"Unable to determine API URL for unknown object kind: {obj}"
                )
        except KeyError as e:
            raise Exception(f"Missing parameter for building a {obj} URL: {e}")

    def create(self, obj: str, data: dict) -> Response:
        """
        Create a resource. Typical for endpoints of the form POST /obj
        """
        url, payload = self._conn_info(obj, data)
        with self._api() as session:
            return session.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=self.request_timeout,
            )

    def read(self, obj: str, obj_id: Optional[str]) -> Response:
        """
        Read a resource content. Typical for endpoints of the form GET /obj/id
        """
        url, _ = self._conn_info(obj)
        if obj_id:
            url = f"{url}/{obj_id}"
        with self._api() as session:
            return session.get(
                url,
                headers=self.headers,
                timeout=self.request_timeout,
            )

    def update(self, obj: str, obj_id: str, data: dict) -> Response:
        """
        Update (modify) a resource content. Typical for endpoints of the form PUT /obj/id
        """
        url, payload = self._conn_info(obj, data)
        with self._api() as session:
            return session.put(
                f"{url}/{obj_id}",
                json=payload,
                headers=self.headers,
                timeout=self.request_timeout,
            )

    def upload(self, url: str, data: dict, files: list) -> Response:
        """
        Upload files.

        Note this is temporary helper, as we expect to turn files as
        first-order resource at the API level, so move to CRUD model, etc.

        This facility disables all timeouts, as uploads can be very
        long, and we'd better wait.
        """
        with self._api() as session:
            return session.post(
                url,
                data=data,
                files=files,
                timeout=None,
            )

    def direct(self, verb: str) -> Callable:
        """
        Direct access to the common session.

        Important: This exposes this object session. It is not the
        guarded session from self._api, because:
        1. This is temporary anyway to accommodate irregular API
           calls (that is, breach to CRUD/REST models).
        2. Using a context manager leads to "leaking" the session,
           without the context extras (as this returns and so exits
           the context).
        """
        return partial(
            getattr(self.session, verb),
            headers=self.headers,
            timeout=self.request_timeout,
        )
