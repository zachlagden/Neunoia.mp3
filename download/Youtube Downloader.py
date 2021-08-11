from colored_print import ColoredPrint
from pytube import YouTube, Playlist
from signal import signal, SIGINT
from datetime import datetime
from moviepy.editor import *

import requests, urllib.parse, json, shutil, os, time, glob, keyboard, threading, sys

os.chdir("youtube")

log = ColoredPrint()
filesize = 0

def now():
    return datetime.now()

for folder_name in ["cache", "songs", "tn", "video"]:
    if not os.path.isdir(folder_name):
        log.warn(now(), " [WARN] ", f"{folder_name} Not Detected, Creating Instead.")
        os.mkdir(folder_name)

def parse_title(title):
    return title.replace(r"\\", "").replace("/", "").replace("*", "").replace("?", "").replace(">", "").replace("<", "").replace("|", "").replace('"', "")

def exit_thread():
    global pl_exit

    while 1:
        time.sleep(0.1)
        if keyboard.is_pressed('q'):
            log.warn(now(), " [WARN] ", f"Exiting.")
            pl_exit = True
            break

while 1:
    mode = input("Mode [mp3/mp4/tn/pl/clear] ~ ")

    if mode.lower() not in ["mp3", "mp4", "tn", "pl", "clear"]:
        log.err(now(), " [ERROR] ", "Mode not found.").store()
        continue

    log.info(now(), " [INFO] ", f"Mode `{mode.lower()}` selected.").store()

    if mode.lower() not in ["pl", "clear"]:
        video_url = input("Video URL ~ ")

        url_data = urllib.parse.urlparse(video_url)
        query = urllib.parse.parse_qs(url_data.query)
        video_id = query["v"][0]

        check_r = requests.get(f"https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/watch?v="+video_id)

        try:
            r_json = json.loads(check_r.text)
        except:
            log.err(now(), " [ERROR] ", "Video not found.").store()
            continue

    if mode.lower() == "tn":
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

        r = requests.get(thumbnail_url, stream = True)

        if r.status_code == 200:
            r.raw.decode_content = True

            with open(f"tn/{r_json['title']}.jpg",'wb') as f:
                shutil.copyfileobj(r.raw, f)

            log.success(now(), " [SUCCESS] ", "Thumbnail Downloaded.").store()
        else:
            log.err(now(), " [ERROR] ", "Could Not Download Thumbnail.").store()

    elif mode.lower() == "mp3":
        yt = YouTube(video_url)

        log.info(now(), " [INFO] ", f"Downloading Video.").store()

        os.chdir("cache")

        try:
            yt.streams.get_lowest_resolution().download()
            log.success(now(), " [SUCCESS] ", "Video Downloaded.")
        except Exception as e:
            raise e
            log.err(now(), " [ERROR] ", "Could Not Download Video.")

        os.chdir("..")

        log.info(now(), " [INFO] ", f"Converting To MP3").store()

        video = VideoFileClip(os.path.join("cache", yt.streams.get_lowest_resolution().default_filename))
        video.audio.write_audiofile(os.path.join("songs", r_json['title']+".mp3"))

        log.success(now(), " [SUCCESS] ", "Video Converted.").store()
        log.warn(now(), " [WARN] ", "Clear Your Cache.").store()

    elif mode.lower() == "mp4":
        yt = YouTube(video_url)

        log.info(now(), " [INFO] ", f"Downloading Video.").store()

        os.chdir("video")

        try:
            yt.streams.get_highest_resolution().download()
            log.success(now(), " [SUCCESS] ", "Video Downloaded.")
        except:
            log.err(now(), " [ERROR] ", "Could Not Download Video.")

        os.chdir("..")

    elif mode.lower() == "pl":
        p_url = input("Playlist URL ~ ")
        playlist = Playlist(p_url)

        url_data = urllib.parse.urlparse(p_url)
        query = urllib.parse.parse_qs(url_data.query)
        list_id = query["list"][0]

        check_r = requests.get(f"https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/playlist?list="+list_id)

        try:
            r_json = json.loads(check_r.text)
            log.info(now(), " [INFO] ", f"Playlist `{r_json['title']}` Loaded.").store()
        except:
            log.err(now(), " [ERROR] ", "Playlist Not Found.").store()
            continue

        while 1:
            plmode = input("Playlist Mode [mp3/mp4/tn] ~ ")

            if plmode not in ["mp3", "mp4", "tn"]:
                log.err(now(), " [ERROR] ", "Playlist Mode Not Found.").store()
                continue

            break

        log.info(now(), " [INFO] ", f"Playlist Mode `{plmode.lower()}` selected.").store()

        download_log = []
        download_num = 0

        if plmode.lower() not in ["tn", "mp3"]:
            log.info(now(), " [INFO] ", f"Downloading Started. Press `q` to stop.").store()

            pl_exit = False
            threading.Thread(target=exit_thread).start()

            for video in playlist:
                video = YouTube(video)

                if pl_exit:
                    break

                download_num += 1

                log.info(now(), " [INFO] ", f"Downloading Video [{download_num}/{len(playlist)}].").store()

                os.chdir("cache")

                try:
                    video.streams.get_highest_resolution().download()
                    download_log.append(video.streams.get_highest_resolution().default_filename)
                    log.success(now(), " [SUCCESS] ", "Video Downloaded.")
                except Exception as e:
                    raise e
                    log.err(now(), " [ERROR] ", "Could Not Download Video.")

                os.chdir("..")

            log.success(now(), " [SUCCESS] ", f"All Videos Downloaded.").store()


        if plmode.lower() == "mp3":
            pl_exit = False
            threading.Thread(target=exit_thread).start()

            log.info(now(), " [INFO] ", f"Downloading Started. Press `q` to exit.").store()

            for video in playlist:
                video = YouTube(video)
                download_num += 1

                if pl_exit:
                    break

                log.info(now(), " [INFO] ", f"Downloading Video [{download_num}/{len(playlist)}].").store()

                os.chdir("cache")

                try:
                    video.streams.get_lowest_resolution().download()
                    download_log.append(video.streams.get_lowest_resolution().default_filename)
                    log.success(now(), " [SUCCESS] ", "Video Downloaded.")
                except Exception as e:
                    raise e
                    log.err(now(), " [ERROR] ", "Could Not Download Video.")

                os.chdir("..")

            log.success(now(), " [SUCCESS] ", f"All Videos Downloaded.").store()

            pl_exit = False
            threading.Thread(target=exit_thread).start()

            log.info(now(), " [INFO] ", f"Converting Started. Press `q` to exit.").store()

            log_num = 0
            for ytvideo in download_log:
                if pl_exit:
                    break

                log_num += 1
                log.info(now(), " [INFO] ", f"Converting Video [{log_num}/{len(download_log)}] To MP3").store()

                pyvideo = VideoFileClip(os.path.join("cache", ytvideo))
                pyvideo.audio.write_audiofile(os.path.join("songs", ytvideo.replace(".mp4", "")+".mp3"))

                log.success(now(), " [SUCCESS] ", f"Video [{log_num}/{len(download_log)}] Converted.").store()

            log.success(now(), " [SUCCESS] ", f"All Videos Converted.").store()
            log.warn(now(), " [WARN] ", "Clear Your Cache.").store()

        if plmode.lower() == "mp4":
            log.info(now(), " [INFO] ", f"Moving videos.").store()

            for video in download_log:
                shutil.move(f"cache/{video}", f"video/{video}")

            log.info(now(), " [INFO] ", f"You will find your videos in the video folder.").store()

        elif plmode.lower() == "tn":
            vidnum = 0

            pl_exit = False
            threading.Thread(target=exit_thread).start()

            log.info(now(), " [INFO] ", f"Downloading Started. Press `q` to exit.").store()

            for video in playlist:
                if pl_exit:
                    break

                vidnum += 1
                url_data = urllib.parse.urlparse(video)
                query = urllib.parse.parse_qs(url_data.query)
                video_id = query["v"][0]

                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

                check_r = requests.get(f"https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/watch?v="+video_id)

                try:
                    r_json = json.loads(check_r.text)
                except:
                    log.err(now(), " [ERROR] ", "Video not found.").store()
                    continue

                r = requests.get(thumbnail_url, stream = True)

                if r.status_code == 200:
                    r.raw.decode_content = True

                    with open(f"tn/{parse_title(r_json['title'])}.jpg",'wb') as f:
                        shutil.copyfileobj(r.raw, f)

                    log.success(now(), " [SUCCESS] ", f"Thumbnail [{vidnum}/{len(playlist)}] Downloaded.").store()
                else:
                    log.err(now(), " [ERROR] ", f"Could Not Download Thumbnail [{vidnum}/{len(playlist)}].").store()

            log.success(now(), " [SUCCESS] ", f"Thumbnails Downloaded.").store()

    elif mode.lower() == "clear":
        while 1:
            c_mode = input("Clear Mode [cache/songs/tn/video] ~ ")

            if c_mode.lower() not in ["cache", "songs", "tn", "video"]:
                log.err(now(), " [ERROR] ", "Clear Mode not found.").store()
                continue

            break

        log.info(now(), " [INFO] ", f"Clear Mode `{c_mode.lower()}` selected.").store()

        if c_mode.lower() == "cache":
            log.info(now(), " [INFO] ", f"Clearing Cache.").store()

            cachelen = len(glob.glob("cache/*.mp4"))
            delnum = 0

            for file in glob.glob("cache/*.mp4"):
                delnum += 1
                log.info(now(), " [INFO] ", f"Deleteing [{delnum}/{cachelen}] {file}").store()

                try:
                    os.remove(file)
                    log.success(now(), " [SUCCESS] ", f"Deleted Successfully.").store()
                except:
                    log.err(now(), " [ERROR] ", f"Could Not Delete File.").store()

        elif c_mode.lower() == "songs":
            log.info(now(), " [INFO] ", f"Clearing Songs.").store()

            cachelen = len(glob.glob("songs/*.mp3"))
            delnum = 0

            for file in glob.glob("songs/*.mp3"):
                delnum += 1
                log.info(now(), " [INFO] ", f"Deleteing [{delnum}/{cachelen}] {file}").store()

                try:
                    os.remove(file)
                    log.success(now(), " [SUCCESS] ", f"Deleted Successfully.").store()
                except:
                    log.err(now(), " [ERROR] ", f"Could Not Delete File.").store()

        elif c_mode.lower() == "tn":
            log.info(now(), " [INFO] ", f"Clearing Thumbnails.").store()

            cachelen = len(glob.glob("tn/*.jpg"))
            delnum = 0

            for file in glob.glob("tn/*.jpg"):
                delnum += 1
                log.info(now(), " [INFO] ", f"Deleteing [{delnum}/{cachelen}] {file}").store()

                try:
                    os.remove(file)
                    log.success(now(), " [SUCCESS] ", f"Deleted Successfully.").store()
                except:
                    log.err(now(), " [ERROR] ", f"Could Not Delete File.").store()

        elif c_mode.lower() == "video":
            log.info(now(), " [INFO] ", f"Clearing Videos.").store()

            cachelen = len(glob.glob("video/*.mp4"))
            delnum = 0

            for file in glob.glob("video/*.mp4"):
                delnum += 1
                log.info(now(), " [INFO] ", f"Deleteing [{delnum}/{cachelen}] {file}").store()

                try:
                    os.remove(file)
                    log.success(now(), " [SUCCESS] ", f"Deleted Successfully.").store()
                except:
                    log.err(now(), " [ERROR] ", f"Could Not Delete File.").store()

        log.success(now(), " [SUCCESS] ", f"Files Deleted.").store()
