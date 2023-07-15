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

    return render_template('library.html', song_info=song_info)


if __name__ == '__main__':
    app.run(debug=True, port=5001)