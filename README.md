# sort_music

Repository implements a script to detect an audio file using <a href="https://rapidapi.com/apidojo/api/shazam/" target="_blank">`Shazam API`</a> to identify songs and to change the properties of given file respectively -> e.g. artist, songname, album, year, etc.

This script currently only works under linux - NO WINDOWS SUPPORT!

Supported file formats are:

- `.mp3`
- `.wma`
- `.wva`
- `.mp4`

<br></br>

---

## Requirements

### Account at <a href="https://rapidapi.com/" target="_blank">`rapidAPI`</a>

> Follow <a href="https://rapidapi.com/blog/shazam-api-java-python-php-ruby-javascript-examples/" target="_blank">`this tutorial`</a> to get an account at `rapidAPI`, afterwards sign a free trail for the `shazam` API

### Apt packages

    - ffmpeg
    - mplayer

&emsp; &rightarrow; &ensp; `sudo apt-get install ffmpeg mplayer`

### Python packages

    - mutagen

&emsp; &rightarrow; &ensp; `pip install mutagen`

<br></br>

---

## Usage

2 possibilities:

1. working with a single file:

&ensp; &rightarrow; &ensp; `python rename_music.py --filename <path_to_file_to_convert>`

2. working with a folder filled with audio files:

&ensp; &rightarrow; &ensp; `python rename_music.py --foldername <path_to_folder_to_convert>`