import json
import os
from pathlib import Path
from typing import Iterable, Optional

import requests

from .url import URL

SelectType = Iterable[str] | str
FilterType = str


def _parse_creds(url: str, username: str | None = None, password: str | None = None):
    parsed_url = URL.from_url(url)
    url = url or parsed_url.get_host()
    if parsed_url.credentials:
        username = username or parsed_url.credentials.username
        password = password or parsed_url.credentials.password
    return url, username, password


class Client:
    def __init__(
        self,
        url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        verify: Optional[str | Path | bool] = None,
        headers: Optional[dict] = None,
    ):
        url = url or os.getenv("DENODO_URL") or os.getenv("DENODO_HOST")
        username = username or os.getenv("DENODO_USERNAME")
        password = password or os.getenv("DENODO_PASSWORD")
        base_url, username, password = _parse_creds(url, username, password)
        if isinstance(verify, str):
            verify = Path(verify)
        # ---
        # Confirm that the certificat is present
        if isinstance(verify, Path):
            if not verify.is_file():
                # logging.warning("\n".join(str(p) for p in Path().iterdir()))
                raise Exception("Certificate not found")
            verify = str(verify)

        session = requests.Session()

        if username and password:
            session.auth = (username, password)
        if verify is not None:
            session.verify = verify

        session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )
        if headers:
            session.headers.update(headers)
        self._session: requests.Session = session
        self._base_url: str = base_url

    @property
    def session(self) -> requests.Session:
        return self._session

    @property
    def restful_url(self) -> str:
        # NOTE: This is the new RESTFul API
        # it is simpler than the previous REST API
        return f"{self._base_url}/denodo-restfulws"

    url = restful_url

    def database(self, name: str) -> "Database":
        return Database(self, name)


class Database:
    def __init__(self, client: Client, name: str):
        self._client: Client = client
        self._name: str = name

    @property
    def client(self) -> Client:
        return self._client

    @property
    def name(self) -> str:
        return self._name

    @property
    def restful_url(self) -> str:
        # NOTE: This is the new RESTFul API
        # it is simpler than the previous REST API
        return f"{self._client.url}/{self.name}"

    url = restful_url

    def view(self, name: str) -> "View":
        return View(self, name)

    def views(self) -> list[str]:
        response = self.client.session.get(
            url=self.url,
            # params=params,
        )
        data = response.json()
        views_metadata = data["views-metadata"]
        return [v["name"] for v in views_metadata]


class View:
    def __init__(self, database: Database, name: str):
        self._database: Database = database
        self._name: str = name

    @property
    def database(self) -> Database:
        return self._database

    @property
    def client(self) -> Client:
        return self._database.client

    @property
    def name(self) -> str:
        return self._name

    @property
    def restful_url(self) -> str:
        # NOTE: This is the new RESTFul API
        # it is simpler than the previous REST API
        return f"{self.database.restful_url}/views/{self.name}"

    url = restful_url

    def _extract_data(self, response) -> Optional[dict]:
        try:
            data = response.json()
            return data
        except Exception:
            return None

    def _check_response(self, response) -> dict:
        if response.status_code == 401:
            raise Exception(
                f"From Denodo (HTTP {response.status_code}): You are not authorized to access this resource."
            )
        data = self._extract_data(response)
        errors = data.get("__errors__")
        if errors:
            raise Exception(
                f"From Denodo (HTTP {response.status_code}):\n{json.dumps(errors, indent=4)}"
            )

        if response.status_code != 200:
            raise Exception(
                f"From Denodo (HTTP {response.status_code}): {response.content.decode()}"
            )
        return data

    def _query_denodo(
        self, select: Optional[str] = None, filter: Optional[str] = None
    ) -> dict:
        params = {
            "$format": "json",
        }
        if select is not None:
            params["$select"] = select
        if filter is not None:
            params["$filter"] = filter

        response = self.client.session.get(
            url=self.url,
            params=params,
        )

        # raise for status isn't providing good informations
        # response.raise_for_status()
        data = self._check_response(response)
        return data

    def get(
        self, select: Optional[SelectType] = None, filter: Optional[FilterType] = None
    ) -> list[dict]:
        if select is not None and not isinstance(select, str):
            select = ",".join(f.strip() for f in select)
        data = self._query_denodo(
            select=select,
            filter=filter,
        )
        elements = data.get("elements") or []
        return elements
