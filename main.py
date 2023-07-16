from flask import Flask, render_template, request, url_for, redirect
from img_search import get_google_img
import os


app = Flask(__name__)


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

    title = song_info[0][0]
    artist = song_info[0][1]
    img_url = song_info[0][2]

    path = f'./static/music/{song}/'
    folder_items = os.listdir(path)

    if f'{title.title()} - {artist}.txt' in folder_items:
        lyric_item = f'{title} - {artist}.txt'
        print(lyric_item)

        with open(f'./static/music/{song}/{lyric_item}', 'r') as file:
            lyrics = file.readlines()
            lyrics = [lyric.strip('\n') for lyric in lyrics]

    if f'{song.title()}.mp3' in folder_items:
        mp3_path = f'.{path}{song.title()}.mp3'

    for filename in folder_items:
     if filename.lower().endswith('.pdf'):
        pdf_path = f".{path}{filename}"

    return render_template('song-page.html', title=title,
                           artist=artist, img_url=img_url,
                           lyrics=lyrics, mp3_path=mp3_path,
                           pdf_path=pdf_path)


if __name__ == '__main__':
    app.run(debug=True, port=5001)