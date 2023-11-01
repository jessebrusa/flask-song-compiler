from youtubesearchpython import VideosSearch
from pytube import YouTube
import os
import certifi
import requests
import azapi
import glob
import shutil


def obtain_lyrics_create_dir(input_title, GOOGLE_API_KEY, GOOGLE_CX):
    path = "./static/music/"
    API = azapi.AZlyrics('google', accuracy=0.5)
    API.title = input_title

    API.getLyrics()

    # Come back to make file exist error catch and route to song-page
    os.mkdir(f'{path}{API.title.lower()}')
    API.getLyrics(save=True, path=f'{path}{API.title.lower()}')
    os.rename(f'{path}{API.title.lower()}/{API.title} - {API.artist}.txt', 
              f'{path}{API.title.lower()}/{API.title.lower()} - {API.artist.lower()}.txt')

    img_url = get_google_img(f'{API.title} {API.artist}', GOOGLE_API_KEY, GOOGLE_CX)

    with open(f'{path}{API.title.lower()}/info.txt', 'w') as file:
        file.write(f'{API.title}\n{API.artist}\n{img_url}')

    return [API.title, API.artist]


def download_song(song_title, song_artist, path):
    query = f"{song_title} {song_artist} audio"
    videos_search = VideosSearch(query, limit=1)
    video_url = videos_search.result()['result'][0]['link']
    
    os.environ['SSL_CERT_FILE'] = certifi.where()

    youtube = YouTube(video_url)
    audio_stream = youtube.streams.filter(only_audio=True).first()
    audio_stream.download(output_path=path, filename=f'{song_title.lower()}.mp3')


def search_song_karaoke(song):
    song_info = []
    with open(f"./static/music/{song.lower()}/info.txt", "r") as file:
        song_info.append(file.read().splitlines())

    title = song_info[0][0]
    artist = song_info[0][1]
    path = f'./static/music/{song}/'

    try:
        download_song(f"{title.lower()} karaoke", artist.lower(), path)
        
    except FileExistsError:
        print('No Karaoke File Found')


def move_from_downloads(destination_folder):
    downloads_folder = '/Users/jessebrusa/Downloads'
    files = glob.glob(os.path.join(downloads_folder, '*'))
    sorted_files = sorted(files, key=os.path.getmtime, reverse=True)
    most_recent_file = sorted_files[0]

    destination_path = os.path.join(destination_folder, os.path.basename(most_recent_file))
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