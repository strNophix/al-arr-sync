import configparser
import os
import typing
from urllib.parse import urljoin

from requests import PreparedRequest
from requests import Session

from al_arr_sync.types import AnyDict


class SonarrClient:
    def __init__(
        self,
        api_url: str,
        api_key: str,
        folder_path: str,
        quality_profile: int = 4,
        language_profile: int = 1,
    ) -> None:
        self.api_url = api_url
        self.api_key = api_key
        self.folder_path = folder_path
        self.quality_profile = quality_profile
        self.language_profile = language_profile

        self.http_session = Session()

    @staticmethod
    def from_env() -> "SonarrClient":
        return SonarrClient(
            api_url=os.environ["SONARR_API_URL"],
            api_key=os.environ["SONARR_API_KEY"],
            folder_path=os.environ["SONARR_FOLDER_PATH"],
            quality_profile=int(os.environ["SONARR_QUALITY_PROFILE"]),
            language_profile=int(os.environ["SONARR_LANGUAGE_PROFILE"]),
        )

    @staticmethod
    def from_config(cfg: configparser.ConfigParser) -> "SonarrClient":
        return SonarrClient(
            api_url=cfg["sonarr"]["api_url"],
            api_key=cfg["sonarr"]["api_key"],
            folder_path=cfg["sonarr"]["folder_path"],
            quality_profile=int(cfg["sonarr"]["quality_profile"]),
            language_profile=int(cfg["sonarr"]["language_profile"]),
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
        req = self._prepare_request("/api/v3/series/lookup", params={"term": query})
        resp = self.http_session.send(req)
        return resp.json()

    def add_series(self, *series: AnyDict):
        for show in series:
            payload: AnyDict = show.copy()
            payload.update(
                {
                    "addOptions": {
                        "monitor": "future",
                        "searchForCutoffUnmetEpisodes": False,
                        "searchForMissingEpisodes": False,
                    },
                    "rootFolderPath": self.folder_path,
                    "qualityProfileId": self.quality_profile,
                    "languageProfileId": self.language_profile,
                }
            )
            req = self._prepare_request("/api/v3/series", method="POST", json=payload)
            resp = self.http_session.send(req)

            if resp.status_code != 201:
                resp_data = resp.json()
                error_codes = map(lambda x: x["errorCode"], resp_data)
                if "SeriesExistsValidator" in error_codes:
                    raise Exception(f"Series already exists: {show['title']}")

                raise Exception(f"Failed to add series: {show['title']}:\n{resp_data}")
