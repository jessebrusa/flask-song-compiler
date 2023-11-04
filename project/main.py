from flask import Flask, render_template, request, url_for, redirect, request
from chords import Chords
from resources import  obtain_lyrics_create_dir, download_song, search_song_karaoke, \
move_from_downloads, get_google_img
from sql import library_table, library_songs, song_page_table, song_page_info
import psycopg2 as pg2
from collections import namedtuple
from dotenv import load_dotenv
import os


load_dotenv()
GUITAR_EMAIL = os.getenv('GUITAR_EMAIL')
GUITAR_PASSWORD = os.getenv('GUITAR_PASSWORD')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CX = os.getenv('GOOGLE_CX')
POSTGRES_PASS = os.getenv('POSTGRES_PASS')



app = Flask(__name__)
conn = pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port='5433')
cur = conn.cursor()


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/library')
def library():
    songs_sql = library_songs()
    Song = namedtuple('Song', library_table)
    cur.execute(songs_sql)
    songs = [Song(*row) for row in cur.fetchall()]

    return render_template('library.html', songs=songs)


@app.route('/song-page/<int:song_id>')
def song_page(song_id):
    song_page_sql = song_page_info(song_id)
    Song = namedtuple('Song', song_page_table)
    cur.execute(song_page_sql)
    info = [Song(*row) for row in cur.fetchall()][0]
    
    if info.lyric_url:
        with open(f'{info.lyric_url}', 'r') as file:
            lyrics = file.read().splitlines()
    else:
        lyrics = None

 
    return render_template('song-page.html', info=info, lyrics=lyrics)


@app.route('/karaoke/<string:song>')
def get_karaoke(song):
    search_song_karaoke(song)
    return redirect(url_for('song_page', song=song))


@app.route('/find-song', methods=['GET', 'POST'])
def find_song():
    if request.method == 'POST':
        input_title = request.form.get('title')


        try:
            song_data = obtain_lyrics_create_dir(input_title)
            title = song_data[0]
            artist = song_data[1]
            path = f'./static/music/{title.lower()}/'
        except:
            pass


        try:
            download_song(title, artist, path)
        except:
            pass


        try:
            chords = Chords()
            chords.login_account(GUITAR_EMAIL, GUITAR_PASSWORD)
            chords.search_song(title)
            chords.save_pdf()
            move_from_downloads(path)
        except:
            pass


        return redirect(url_for('song_page', song=title.lower()))        

    return render_template('find-song.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)