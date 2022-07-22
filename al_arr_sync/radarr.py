import os
import configparser
import typing
from urllib.parse import urljoin

from requests import PreparedRequest
from requests import Session

from al_arr_sync.types import AnyDict


class RadarrClient:
    def __init__(
        self, api_url: str, api_key: str, folder_path: str, quality_profile: int = 4
    ) -> None:
        self.api_url = api_url
        self.api_key = api_key
        self.folder_path = folder_path
        self.quality_profile = quality_profile

        self.http_session = Session()

    @staticmethod
    def from_env() -> "RadarrClient":
        return RadarrClient(
            api_url=os.environ["SONARR_API_URL"],
            api_key=os.environ["SONARR_API_KEY"],
            folder_path=os.environ["SONARR_FOLDER_PATH"],
            quality_profile=int(os.environ["SONARR_QUALITY_PROFILE"]),
        )

    @staticmethod
    def from_config(cfg: configparser.ConfigParser) -> "RadarrClient":
        return RadarrClient(
            api_url=cfg["radarr"]["api_url"],
            api_key=cfg["radarr"]["api_key"],
            folder_path=cfg["radarr"]["folder_path"],
            quality_profile=int(cfg["radarr"]["quality_profile"]),
        )

    def _prepare_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: AnyDict = {},
        json: typing.Optional[AnyDict] = None,
    ) -> PreparedRequest:
        url = urljoin(self.api_url, endpoint)
        headers = {"X-Api-Key": self.api_key}

        req = PreparedRequest()
        req.prepare(method=method, url=url, headers=headers, params=params, json=json)
        return req

    def lookup_series(self, query: str) -> typing.List[AnyDict]:
        req = self._prepare_request("/api/v3/movie/lookup", params={"term": query})
        resp = self.http_session.send(req)
        return resp.json()

    def add_series(self, *series: AnyDict):
        for show in series:
            payload: AnyDict = show.copy()
            payload.update(
                {
                    "addOptions": {
                        "searchForMovie": True,
                        "ignoreEpisodesWithFiles": False,
                        "ignoreEpisodesWithoutFiles": False,
                    },
                    "rootFolderPath": self.folder_path,
                    "qualityProfileId": self.quality_profile,
                }
            )
            req = self._prepare_request("/api/v3/movie", method="POST", json=payload)
            resp = self.http_session.send(req)

            if resp.status_code != 201:
                resp_data = resp.json()
                error_codes = map(lambda x: x["errorCode"], resp_data)
                if "MovieExistsValidator" in error_codes:
                    raise Exception(f"Movie already exists: {show['title']}")

                raise Exception(f"Failed to add movie: {show['title']}:\n{resp_data}")
