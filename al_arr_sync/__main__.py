import sys
import typing

from al_arr_sync.anilist import AniListClient
from al_arr_sync.radarr import RadarrClient
from al_arr_sync.sonarr import SonarrClient
from al_arr_sync.types import DlAutomator, MediaTracker
from al_arr_sync.config import load_config


def main(args: typing.Sequence[str]) -> int:
    cfg_path = args[0] if len(args) > 0 else "./config.ini"
    cfg = load_config(cfg_path)

    al: MediaTracker = AniListClient()
    sonarr: DlAutomator = SonarrClient.from_config(cfg)
    radarr: DlAutomator = RadarrClient.from_config(cfg)

    download_clients: typing.Dict[str, DlAutomator] = {
        "TV": sonarr,
        "MOVIE": radarr,
    }

    username = cfg["anilist"]["username"]
    media = al.currently_watching(username)

    for entry in media:
        media_format = entry["media"]["format"]
        show_name = entry["media"]["title"]["english"]

        client: typing.Optional[DlAutomator] = download_clients.get(
            media_format)
        if client is None:
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
    raise SystemExit(main(sys.argv[1:]))
