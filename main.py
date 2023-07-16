from flask import Flask, render_template, request, url_for, redirect
from img_search import get_google_img
from youtubesearchpython import VideosSearch
from pytube import YouTube
import certifi
import os


app = Flask(__name__)


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
        # list_items_folder(path)
        print('No Karaoke File Found')


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/library')
def library():
    song_folders = sorted(os.listdir('./static/music'))[1:]

    song_info = []
    for song_folder in song_folders:
        with open(f"./static/music/{song_folder}/info.txt", "r") as file:
            song_info.append(file.read().splitlines())
    for num in range(len(song_info)):
        song_info[num].append(song_folders[num])

    return render_template('library.html', song_info=song_info)


@app.route('/data/<song>')
def song_page(song):
    song_info = []
    with open(f"./static/music/{song}/info.txt", "r") as file:
        song_info.append(file.read().splitlines())

    title = song_info[0][0].lower()
    artist = song_info[0][1].lower()
    img_url = song_info[0][2]

    path = f'./static/music/{song}/'
    folder_items = os.listdir(path)

    if f'{title} - {artist}.txt' in folder_items:
        lyric_item = f'{title} - {artist}.txt'

        with open(f'./static/music/{song}/{lyric_item}', 'r') as file:
            lyrics = file.readlines()
            lyrics = [lyric.strip('\n') for lyric in lyrics]

    if f'{song.lower()}.mp3' in folder_items:
        mp3_path = f'.{path}{song.title()}.mp3'

    print(f'{song.lower()} karaoke.mp3')

    if f'{song.lower()} karaoke.mp3' in folder_items:
        karaoke_path = f'.{path}{song.title()} Karaoke.mp3'
        print(f'\n{karaoke_path}\n')
    else:
        karaoke_path = None

    for filename in folder_items:
     if filename.lower().endswith('.pdf'):
        pdf_path = f".{path}{filename}"

    title = title.title()
    artist = artist.title()

    return render_template('song-page.html', title=title,
                           artist=artist, img_url=img_url,
                           lyrics=lyrics, mp3_path=mp3_path,
                           pdf_path=pdf_path, karaoke_path=karaoke_path,
                           song=song)


@app.route('/karaoke/<song>')
def get_karaoke(song):
    search_song_karaoke(song)
    return redirect(url_for('song_page', song=song))


if __name__ == '__main__':
    app.run(debug=True, port=5001)