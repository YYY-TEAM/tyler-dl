# README

This script lets you download [courses from Tyler McGinnis](https://learn.tylermcginnis.com/courses/), as permitted by the [Terms of use](https://learn.tylermcginnis.com/p/terms). You need a valid subscription.

Just provide username and password, and choose a course to download from the menue. Optionally you can choose a target directory, where your text and video files will be stored, and full HD as quality of the downloaded video (default: 720p). Downloading videos or texts can be skipped With `--skipvideo` or `--skiptext`.

### Available courses

*   Modern Javascript
*   React Fundamentals
*   Redux
*   React Router
*   React Native
*   Universal React (coming soon)

### Usage

1.  Download or clone this repository
2.  Install requirements
    `pip install -r requirements.txt`
3.  Run the script.
    `python tyler-dl.py -u YOUR_USERNAME -p YOUR_PASSWORD [-o TARGET_DIR] [--fullhd] [--skipvideo] [--skiptext]`
