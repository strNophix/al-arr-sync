import os
import typing
from urllib.parse import urljoin

from requests import PreparedRequest
from requests import Session

from al_arr_sync.types import AnyDict


class SonarrClient:
    def __init__(self, sonarr_url: str, api_key: str) -> None:
        self.sonarr_url = sonarr_url
        self.api_key = api_key
        self.http_session = Session()

    @staticmethod
    def from_env() -> "SonarrClient":
        return SonarrClient(
            sonarr_url=os.environ["SONARR_API_URL"],
            api_key=os.environ["SONARR_API_KEY"],
        )

    def _prepare_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: AnyDict = {},
        json: typing.Optional[AnyDict] = None,
    ) -> PreparedRequest:
        url = urljoin(self.sonarr_url, endpoint)
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
                    "rootFolderPath": os.environ["SONARR_FOLDER_PATH"],
                    "qualityProfileId": int(os.environ["SONARR_QUALITY_PROFILE"]),
                    "languageProfileId": int(os.environ["SONARR_LANGUAGE_PROFILE"]),
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
