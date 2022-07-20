import os
import typing
from dotenv import load_dotenv
from al_arr_sync.anilist import AniListClient
from al_arr_sync.sonarr import SonarrClient

load_dotenv()


def main() -> int:
    al = AniListClient()
    sonarr = SonarrClient.from_env()

    username = os.environ["ANILIST_USERNAME"]
    media = al.currently_watching(username)
    
    series: typing.List[typing.Any] = []
    for entry in media:
        media_format = entry["media"]["format"]
        if media_format == "TV":
            series.append(entry)

    for show in series:
        show_name = show["media"]["title"]["english"]
        results = sonarr.lookup_series(show_name)
        try:
            sonarr.add_series(results[0])
            print(f"Successfully added series {show_name}")
        except Exception as e:
            print(e)
            continue

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
