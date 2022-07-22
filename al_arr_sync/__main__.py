import os

from dotenv import load_dotenv

from al_arr_sync.anilist import AniListClient
from al_arr_sync.radarr import RadarrClient
from al_arr_sync.sonarr import SonarrClient
from al_arr_sync.types import DlAutomator

load_dotenv()


def main() -> int:
    al = AniListClient()
    sonarr: DlAutomator = SonarrClient.from_env()
    radarr: DlAutomator = RadarrClient.from_env()

    username = os.environ["ANILIST_USERNAME"]
    media = al.currently_watching(username)

    for entry in media:
        media_format = entry["media"]["format"]
        show_name = entry["media"]["title"]["english"]

        client: DlAutomator
        if media_format == "TV":
            client = sonarr
        elif media_format == "MOVIE":
            client = radarr
        else:
            continue

        results = client.lookup_series(show_name)
        if len(results) == 0:
            print(f"No results found for: {show_name}")
            continue

        try:
            client.add_series(results[0])
            print(f"Successfully added: {show_name}")
        except Exception as e:
            print(e)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
