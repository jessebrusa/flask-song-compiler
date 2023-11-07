from youtubesearchpython import VideosSearch
from pytube import YouTube
import os
import certifi
import requests
import azapi
import glob
import shutil


def obtain_lyrics_get_img(GOOGLE_API_KEY, GOOGLE_CX, title, **kwargs):
    artist = kwargs.get('artist')
    path = "./static/lyric/"
    API = azapi.AZlyrics('google', accuracy=0.5)
    API.title = title
    if artist:
        API.artist = artist
    

    API.getLyrics(save=True, path=path)

    os.rename(f'{path}/{API.title} - {API.artist}.txt', 
              f'{path}/{API.title}.txt')

    img_url = get_google_img(f'{API.title} {API.artist}', GOOGLE_API_KEY, GOOGLE_CX)

    return [API.title, API.artist, img_url]


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