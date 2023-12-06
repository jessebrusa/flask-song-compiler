from youtubesearchpython import VideosSearch
from pytube import YouTube
import os
import certifi
import requests
import azapi
import glob
import shutil
import lyricsgenius
import re
import subprocess


def obtain_lyrics(title, **kwargs):
    artist = kwargs.get('artist')
    API = azapi.AZlyrics('google', accuracy=0.5)
    API.title = title
    if artist:
        API.artist = artist

    API.getLyrics(save=False)
    if API.lyrics:
        return API.lyrics
    else:
        return None


def download_song(title, artist, path):
    query = f"{title} {artist} audio"
    try:
        videos_search = VideosSearch(query, limit=1)
        video_url = videos_search.result()['result'][0]['link']
        
        os.environ['SSL_CERT_FILE'] = certifi.where()

        youtube = YouTube(video_url)
        audio_stream = youtube.streams.filter(only_audio=True).first()
        audio_stream.download(output_path=path, filename=f'{title}.mp3')

        return True
    
    except:
        return False


def download_karaoke(title, path):
    query = f"{title} Karaoke"
    try:
        videos_search = VideosSearch(query, limit=1)
        video_url = videos_search.result()['result'][0]['link']
        
        os.environ['SSL_CERT_FILE'] = certifi.where()

        youtube = YouTube(video_url)
        audio_stream = youtube.streams.filter(only_audio=True).first()
        audio_stream.download(output_path=path, filename=f'{title}_karaoke.mp3')

        return True
    
    except:
        return False


def move_from_downloads(destination_folder, new_filename):
    downloads_folder = '/Users/jessebrusa/Downloads'
    files = glob.glob(os.path.join(downloads_folder, '*'))
    sorted_files = sorted(files, key=os.path.getmtime, reverse=True)
    most_recent_file = sorted_files[0]

    destination_path = os.path.join(destination_folder, new_filename)
    shutil.move(most_recent_file, destination_path)


def get_google_img(query, api_key, cx):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "searchType": "image"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        if "items" in data and len(data["items"]) > 0:
            img_url = data["items"][0]["link"]
            return img_url

    return None


def get_album_release_year(API_KEY, title, artist):
    url = f'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={API_KEY}&artist={artist}&track={title}&format=json'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        track_info = data.get('track', {})
        if 'album' in track_info:
            album_info = track_info['album']
            release_year = album_info.get('releasedate')
            album_name = album_info.get('title')

            return [album_name, release_year]
        

def get_song_info(title, **kwargs):
    artist = kwargs.get('artist')
    if artist:
        search_query = f'{title} by {artist}'
    else: 
        search_query = title

    base_url = 'https://musicbrainz.org/ws/2/'

    params = {
            'query': search_query,
            'fmt': 'json',
            'limit': 1,
            'client': 'flask-song-compiler',
            'inc': 'artist-credits+releases',
            'fmt': 'json'
        }
    
    response = requests.get(f'{base_url}recording', params=params)

    if response.status_code == 200:
        data = response.json()
        if 'recordings' in data and len(data['recordings']) > 0:
            recording = data['recordings'][0]
            title = recording['title']
            artist = recording['artist-credit'][0]['artist']['name']
            if 'releases' in recording:
                release = recording['releases'][0]
                album = release['title']
                release_year = release['date'] if 'date' in release else 'Unknown Year'
                print(f"Title: {title}, Artist: {artist}, Album: {album}, Release Year: {release_year}")
                return [album, release_year]
            else:
                print(f"Title: {title}, Artist: {artist}, No album information found.")
                return ['Unknown Album', 'Unknown Year']
        else:
            print("No matching song found.")
            return ['Unknown Album', 'Unknown Year']
    else:
        print("Error: Unable to access the MusicBrainz API.")
        return ['Unknown Album', 'Unknown Year']
    

def clean_lyrics(lyrics):
    # Define a list of common metadata patterns to remove
    metadata_patterns = [
        r"\[.*?\]",  # Matches content within square brackets, e.g., [Verse 1]
        r"\(.*?\)",  # Matches content within parentheses, e.g., (Intro)
        r"\d+\s*Contributors",  # Matches numeric value followed by "Contributors"
        r"[\w\s]+ Lyrics",  # Matches "Artist Name Lyrics"
    ]

    # Define a list of specific patterns to exclude
    exclude_patterns = [
        r"\d+Embed",  # Exclude numeric value followed by "Embed"
    ]

    # Combine the metadata and exclude patterns into a regular expression
    all_patterns = metadata_patterns + exclude_patterns
    all_regex = "|".join(all_patterns)

    # Remove metadata and exclude patterns from the beginning and end of the lyrics
    cleaned_lyrics = re.sub(f".*?{all_regex}|{all_regex}.*?$", "", lyrics)

    return cleaned_lyrics.strip()


def get_lyrics(api_key, title, **kwargs):
    artist = kwargs.get('artist')

    genius = lyricsgenius.Genius(api_key)

    if artist:
        song = genius.search_song(title, artist)
    else:
        song = genius.search_song(title)

    if song:
        lyrics = clean_lyrics(song.lyrics)

        return lyrics
    else:
        return None
    