'''
Script using shazam API - https://rapidapi.com/apidojo/api/shazam/ - to identify songs and to change the properties of given file respectively -> e.g. artist, songname, album, year, etc.
'''

## Imports
import os, subprocess, requests, base64, argparse
from pydub import AudioSegment
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, COMM
from tqdm import tqdm

def xxx2mp3(filename:str) -> str:
    '''
    converts a file that is not in .mp3 format into mp3 format
    Parameter:
        - filename: name of file [String]
    Returns:
        - filename: name of new file - same as before but with .mp3 ending [String]
    '''
    ## get format of provided file
    _format = filename.split(".")[-1]
    ## check if we have this stupid little ass bitch of 'wma' file
    if _format == "wma":
        ## convert file into .wav format using mplayer - has to be installed using 'sudo apt-get install mplayer'
        os.system(f"mplayer -ao pcm '{filename}'")
        ## remove old .wma file, format now wav
        os.remove(filename)
        _format = "wav"
        ## file now called audiodumpy.wav - set by mplayer
        filename = 'audiodump.wav'
    ## read the 'not' mp3 file
    false_format = AudioSegment.from_file(filename, format=_format)
    ## remove old 'not' mp3 file
    os.remove(filename)
    ## export file as mp3, reset name of filename to end with mp3
    false_format.export(f'{filename.split(".")[-2]}.mp3', format="mp3")
    filename = f'{filename.split(".")[-2]}.mp3'
    return filename

def parse_infos(response:dict) -> ([str], str, str, str, str, str):
    '''
    parse the infos from given response of API
    Parameter:
        - response: response of API in JSON [Dictionary]
    Returns:
        - Tuple containing [Tuple]:
            - artists: list of artists [List(String)]
            - song: name of song [String]
            - genre: genre of song [String]
            - album: name of album [String]
            - year: year of publishing song [String]
            - label: label that published song [String]
    '''
    ## possible combinations that indicate a feature
    features = ["feat", "feature", "Feature", "Feat", "FEATURE", "FEAT", "FEATURING", "featuring", "feat.", "FEAT.", "Feat.", "ft.", "FT.", "Ft.", "ft", "Ft", "FT"]
    ## all track infos
    trackinfos = response["track"]
    ## get artists
    artist = trackinfos["subtitle"]
    artists = [artist] if len(set(artist.split(" ")) & set(features)) == 0 else [a.strip() for a in artist.split(list(set(artist.split(" ")) & set(features))[0])]
    ## get songname, genre, album, year and label name
    song = trackinfos["title"]
    genre = trackinfos["genres"]["primary"]
    album = trackinfos["sections"][0]["metadata"][0]["text"]
    year = trackinfos["sections"][0]["metadata"][2]["text"]
    label = trackinfos["sections"][0]["metadata"][1]["text"]
    return (artists, song, genre, album, year, label)

def change_properties(filename:str, response:dict) -> None:
    '''
    changes the properties of given file by respective detected properties
    Paramater:
        - filename: name of file [String]
        - response: response of API in JSON [Dictionary]
    Returns:
        - None
    '''
    artists, song, genre, album, year, label = parse_infos(response)
    ## read mp3 file
    audio = EasyID3(filename)
    ## go through all valid keys, reset everything, except tracknumber
    for key in EasyID3.valid_keys.keys():
        try:
            if key == "tracknumber":
                continue
            audio[key] = ""
        except:
            pass
    ## set all detected new properties
    audio['title'] = song
    audio['artist'] = artists
    audio['albumartist'] = artists[0]
    audio['album'] = album
    audio['organization'] = label
    audio['date'] = year
    audio['genre'] = genre
    ## save file
    audio.save()
    ## re-read file
    audio = ID3(filename)
    ## search for all properties that start with 'COMM', indicate a comment. We want to get rid of those
    for key, val in audio.items():
        if key.startswith("COMM"):
            audio.pop(key)
    ## ##re-safe file, change name to format "(first-)artist - songname"
    audio.save()
    os.rename(filename, f'{artists[0]} - {song}.mp3')

def pipeline(api_key:str, files:[str]) -> None:
    '''
    runs whole pipeline of this script
    Parameters:
        - api_key: personal key for API [String]
        - filename: name of files to work with [List(String)]
    Returns:
        - None
    '''
    ## personal header for API
    headers = {
        'content-type': "text/plain",
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "shazam.p.rapidapi.com"
        }
    url = "https://shazam.p.rapidapi.com/songs/detect"
    ## start and end time in seconds for recognition
    start, end = 12, 18
    ## temporary file - needed for conversion to work with provided API
    _file = 'tmp.raw'
    ## go through files
    for f in tqdm(files):
        if "'" in f:
            old_f = f
            f = f.replace("'", "")
            os.rename(old_f, f)
        ## command to crop that window out of given file that shall be used for identifying -> API cannot work with whole file data (and it also doesn't make much sense because crops >6s not needed) - convert to raw file with bitrate 44100 and mono audio
        command = f'ffmpeg -hide_banner -loglevel quiet -i "{f}" -ac 1 -b:a 44100 -ss {start} -to {end} -f s16le {_file}'
        ## crop respective sample from file
        os.system(command)
        ## read data from file
        file_data = open(_file, "rb").read()
        ## encode data to base64string - needed by API
        pload = base64.b64encode(file_data)
        ## ask for response from API
        response = requests.request("POST", url, data=pload, headers=headers)
        ## check if API finds a matching song
        try:
            _ = response.json()["track"]
        except:
            print(f"Sorry, API couldn't recognize the provided song from file: {f}")
            os.remove(_file)
            continue
        ## check if provided file is already in mp3 or has to be converted
        if not _file.endswith("mp3"):
            f = xxx2mp3(f)
        ## change detected properties
        change_properties(f, response.json())
        ## remove temporary file
        os.remove(_file)
        
if __name__ == "__main__":    
    ## init argument parser
    parser = argparse.ArgumentParser(description = "realtime pipeline to predict VLAN network traffic")
    parser.add_argument('--filename', help = 'name of file to identify [String, default = ""]', type = str, default = "")
    parser.add_argument('--foldername', help = 'name of folder containing all files to identify [String, default = ""]', type = str, default = "")
    args = parser.parse_args()
    ## load personal API key
    api_key = open("api_key.txt", "r").read()
    ## check parsed arguments
    if args.filename != "":
        files = [args.filename] 
    elif args.foldername != "":
        os.chdir(args.foldername)
        files = [f for f in os.listdir() if f[-3:] in ['mp3', 'wma', 'wva', 'mp4']]
    else:
        raise NotImplemented("cannot work without provided file or folder")
    pipeline(api_key, files)