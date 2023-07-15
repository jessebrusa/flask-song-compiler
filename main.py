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

    # lyric_path = f"{path}{folder_items[1]}"
    # with open(lyric_path, 'r') as file:
    #     lyrics = file.read()

    if '.pdf' in folder_items[-1]:
        pdf_path = f"{path}{folder_items[-1]}"

    if f'{title}.mp3' in folder_items:
        mp3_path = f'{path}{title}.mp3'


    return render_template('song-page.html', title=title,
                           artist=artist, img_url=img_url)


if __name__ == '__main__':
    app.run(debug=True, port=5001)