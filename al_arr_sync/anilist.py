import typing

from requests import Session

from al_arr_sync.types import AnyDict


USER_WATCHING_QUERY = """
query ($userName: String) {
  MediaListCollection(userName: $userName, type:ANIME, status:CURRENT) {
    lists {
      entries {
        media {
          title {
            english
          }
          format
        }
      }
    }
  }
}
"""


class AniListClient:
    def __init__(self) -> None:
        self.graphql_api_url = "https://graphql.anilist.co/"
        self.http_session = Session()

    def currently_watching(self, username: str) -> typing.List[AnyDict]:
        resp = self.http_session.post(
            self.graphql_api_url,
            json={"query": USER_WATCHING_QUERY, "variables": {"userName": username}},
        )
        resp_data: AnyDict = resp.json()
        if errors := resp_data.get("errors"):
            raise Exception(errors)

        media = [
            entry
            for lst in resp_data["data"]["MediaListCollection"]["lists"]
            for entry in lst["entries"]
        ]

        return media
