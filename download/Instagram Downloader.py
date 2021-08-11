from colored_print import ColoredPrint
from datetime import datetime

import os, glob, string

os.chdir("instagram")

log = ColoredPrint()

def now():
    return datetime.now()

def filename_parse(fn : str):
    return fn.replace(r"\\", "").replace("/", "").replace("*", "").replace("?", "").replace(">", "").replace("<", "").replace("|", "").replace('"', "")

if not os.path.isdir("posts"):
    log.warn(now(), " [WARN] ", f"`posts` folder not found, creating one now.")
    os.mkdir("posts")

while 1:
    profile_url = input("Username/Profile Url [or `post` for single post] ~ ")

    if profile_url.lower() != "post":
        if "instagram.com" in profile_url:
            profile_name = profile_url.replace("http://", "").replace("https://", "").replace("www.", "").replace("instagram.com", "").replace("/", "")

        else:
            profile_name = profile_url

        profile_foldername = filename_parse(profile_name)

        num = 0
        no_letters = False

        while 1:
            try:
                first_letter = profile_foldername[0]
            except:
                no_letters = True
                break
            if first_letter not in string.ascii_lowercase:
                num += 1
                continue
            else:
                break

        if not os.path.isdir(first_letter):
            log.warn(now(), " [WARN] ", f"No profile with the letter `{first_letter}`, creating `{first_letter}` folder.")
            os.mkdir(first_letter.upper())

        os.chdir(first_letter.upper())

        if not os.path.isdir(profile_foldername):
            log.warn(now(), " [WARN] ", f"`{profile_name}` Has not been downloaded before, creating download folder.")
            os.mkdir(profile_foldername)

        os.chdir(profile_foldername)

        os.system(f"instaloader profile {profile_name} --dirname-pattern={os.getcwd()}")

        log.success(now(), " [SUCCESS] ", f"`{profile_name}` Has been download.")

        log.info(now(), " [INFO] ", f"Deleteing useless files.")

        for file in glob.glob("*.xz")+glob.glob("*.txt"):
            try:
                os.remove(file)
                log.info(now(), " [INFO] ", f"Successfully Deleted {file}")
            except:
                log.warn(now(), " [INFO] ", f"Couldn't Delete {file}")

        os.chdir("..")
        os.chdir("..")


    else:
        post_url = input("Post Url/Id ~ ")
        post_id = post_url.replace("http://", "").replace("https://", "").replace("www.", "").replace("instagram.com", "").replace("/p/", "").replace("/", "")

        os.chdir("posts")

        os.system(f"instaloader -- -{post_id}")

        log.info(now(), " [INFO] ", f"Deleteing useless files.")

        os.chdir(f"-{post_id}")

        for file in glob.glob("*.xz")+glob.glob("*.txt"):
            try:
                os.remove(file)
                log.info(now(), " [INFO] ", f"Successfully Deleted {file}")
            except:
                log.warn(now(), " [INFO] ", f"Couldn't Delete {file}")

        os.chdir("..")
        os.chdir("..")
