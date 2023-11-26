from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
from urllib.parse import urljoin, urlparse
from colored_print import ColoredPrint
from pytube import YouTube, Playlist
from datetime import datetime
from moviepy.editor import *

import spotipy, json, os, glob, time, threading

log = ColoredPrint()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="client id", client_secret="client secret")) # set urs here

def now():
    return datetime.now()

os.chdir("spotify")

for folder_name in ["songs", "cache"]:
    if not os.path.isdir(folder_name):
        log.warn(now(), " [WARN] ", f"{folder_name} Not Detected, Creating Instead.")
        os.mkdir(folder_name)

os.chdir("cache")

def download(query):
    try:
        search = VideosSearch(query, limit = 1)

        url = f"https://www.youtube.com/watch?v={search.result()['result'][0]['id']}"

        yt = YouTube(url)
        yt.streams.get_lowest_resolution().download()

        video = VideoFileClip(yt.streams.get_lowest_resolution().default_filename)
        video.audio.write_audiofile(os.path.join("..", "songs", yt.streams.get_lowest_resolution().default_filename.replace(".mp4", "")+".mp3"), verbose=False, logger=None)
    except:
        pass


def clear_cache():
    log.info(now(), " [INFO] ", f"Auto Clearing Cache.")
    cachelen = len(glob.glob("cache/*.mp4"))
    delnum = 0
    for file in glob.glob("cache/*.mp4"):
        delnum += 1
        log.info(now(), " [INFO] ", f"Deleteing [{delnum}/{cachelen}] {file}")

        try:
            os.remove(file)
            log.success(now(), " [SUCCESS] ", f"Deleted Successfully.")
        except:
            log.err(now(), " [ERROR] ", f"Could Not Delete File.")

clear_cache()

while 1:
    url = input("Playlist/Track Url ~ ")
    url = urljoin(url, urlparse(url).path)

    if "/playlist/" in url:
        log.info(now(), " [INFO] ", "Playlist Detected.")

        try:
            json_data = json.loads(json.dumps(sp.playlist(url)))
            log.success(now(), " [SUCCESS] ", "Playlist Loaded.")
        except:
            log.err(now(), " [ERROR] ", "Playlist Could Not Be Loaded.")
            continue

        mode = "playlist"

    elif "/track/" in url:
        log.info(now(), " [INFO] ", "Track Detected.")

        try:
            json_data = json.loads(json.dumps(sp.track(url)))
            log.success(now(), " [SUCCESS] ", "Track Loaded.")
        except:
            log.err(now(), " [ERROR] ", "Track Could Not Be Loaded.")
            continue

        mode = "track"

    if mode == "track":
        query = f'{json_data["name"]} - {json_data["artists"][0]["name"]}'

        search = VideosSearch(query, limit = 1)

        url = f"https://www.youtube.com/watch?v={search.result()['result'][0]['id']}"

        yt = YouTube(url)

        log.info(now(), " [INFO] ", f"Started Downloading {query}")

        try:
            yt.streams.get_lowest_resolution().download()
        except:
            pass

        log.info(now(), " [INFO] ", f"Started Converting {query}")

        video = VideoFileClip(yt.streams.get_lowest_resolution().default_filename)
        video.audio.write_audiofile(os.path.join("..", "songs", yt.streams.get_lowest_resolution().default_filename.replace(".mp4", "")+".mp3"), verbose=False, logger=None)

    elif mode == "playlist":
        log.info(now(), " [INFO] ", f"Starting Download.")

        for song in json_data["tracks"]["items"]:
            query = f'{song["track"]["name"]} - {song["track"]["artists"][0]["name"]}'

            threading.Thread(target=download, args=(query,)).start()

        log.info(now(), " [INFO] ", f"Download Started, you can use the program during the download.")
