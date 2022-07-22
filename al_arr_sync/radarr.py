import os
import typing
from urllib.parse import urljoin

from requests import PreparedRequest
from requests import Session

from al_arr_sync.types import AnyDict


class RadarrClient:
    def __init__(self, radarr_url: str, api_key: str) -> None:
        self.radarr_url = radarr_url
        self.api_key = api_key
        self.http_session = Session()

    @staticmethod
    def from_env() -> "RadarrClient":
        return RadarrClient(
            radarr_url=os.environ["RADARR_API_URL"],
            api_key=os.environ["RADARR_API_KEY"],
        )

    def _prepare_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: AnyDict = {},
        json: typing.Optional[AnyDict] = None,
    ) -> PreparedRequest:
        url = urljoin(self.radarr_url, endpoint)
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
                    "rootFolderPath": os.environ["RADARR_FOLDER_PATH"],
                    "qualityProfileId": int(os.environ["RADARR_QUALITY_PROFILE"]),
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
