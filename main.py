from flask import Flask, render_template, request, url_for, redirect
from img_search import get_google_img
import os


app = Flask(__name__)


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/library')
def library():
    song_list = sorted(os.listdir('./static/music'))[1:]
    return render_template('library.html', song_list=song_list)


if __name__ == '__main__':
    app.run(debug=True, port=5001)