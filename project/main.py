from flask import Flask, render_template, request, url_for, redirect, request
from pytube import YouTube
from chords import Chords
from resources import  obtain_lyrics_create_dir, download_song, search_song_karaoke, \
move_from_downloads, get_google_img
import psycopg2 as pg2
import shutil
import os


GUITAR_EMAIL = 'jessebrusa@gmail.com'
GUITAR_PASSWORD = '1JesusKing7'
GOOGLE_API_KEY = "AIzaSyBtuoL2-dL71kSmh6sPsrLSSpgn1thUYJg"
GOOGLE_CX = "15d5cf5fb6e3c484c"


app = Flask(__name__)
conn = pg2.connect(database='song_compiler_db', user='postgres', password='p48dT7k78n$G756JrcS%', port='5433')
cur = conn.cursor()

@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/library')
def library():
    song_folders = sorted(os.listdir('./static/music'))[1:]

    song_info = []
    for song_folder in song_folders:
        try:
            with open(f"./static/music/{song_folder}/info.txt", "r") as file:
                song_info.append(file.read().splitlines())
        except:
            pass
    for num in range(len(song_info)):
        song_info[num].append(song_folders[num])

    return render_template('library.html', song_info=song_info)


@app.route('/data/<song>')
def song_page(song):
    song_info = []
    with open(f"./static/music/{song}/info.txt", "r") as file:
        song_info.append(file.read().splitlines())

    original_title = song_info[0][0]
    title = song_info[0][0].lower()
    artist = song_info[0][1].lower()
    img_url = song_info[0][2]

    path = f'./static/music/{title}/'
    folder_items = os.listdir(path)

    if f'{title} - {artist}.txt' in folder_items:
        lyric_item = f'{title} - {artist}.txt'

        with open(f'./static/music/{title}/{lyric_item}', 'r') as file:
            lyrics = file.readlines()
            lyrics = [lyric.strip('\n') for lyric in lyrics]
    else:
        lyrics = None


    if f'{title}.mp3' in folder_items:
        mp3_path = f'.{path}{title}.mp3'
    else:
        mp3_path = None


    if f'{title} karaoke.mp3' in folder_items:
        karaoke_path = f'.{path}{title} karaoke.mp3'
    else:
        karaoke_path = None

    for filename in folder_items:
        if filename.lower().endswith('.pdf'):
            pdf_path = f".{path}{filename}"
            break
        else:
            pdf_path = None

    title = title.title()
    artist = artist.title()
 
    return render_template('song-page.html', title=original_title,
                           artist=artist, img_url=img_url,
                           lyrics=lyrics, mp3_path=mp3_path,
                           pdf_path=pdf_path, karaoke_path=karaoke_path,
                           song=song)


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
    app.run(debug=True, port=5000)