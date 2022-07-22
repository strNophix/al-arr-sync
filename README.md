# al-arr-sync
A small script for syncing your currently watching anime from AniList to Sonarr/Radarr.

## Usage
```sh
pip install git+https://git.cesium.pw/niku/al-arr-sync.git#egg=al-arr-sync

wget -O config.ini https://git.cesium.pw/niku/al-arr-sync/raw/branch/main/config.ini.example 
nano config.ini

python -m al_arr_sync
```

In case you want to use a specific config:
```sh
python -m al_arr_sync ~/home/.config/al-arr-sync/config.ini
```
