from flask import Flask, render_template, request, url_for, redirect, request
from ultimate_guitar_scraper import UltimateGuitarScraper
from resources import  *
from sql import *
import psycopg2 as pg2
from collections import namedtuple
from dotenv import load_dotenv
import os


load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CX = os.getenv('GOOGLE_CX')
POSTGRES_PASS = os.getenv('POSTGRES_PASS')
LAST_FM_API_KEY = os.getenv('LAST_FM_API_KEY')



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


@app.route('/mp3/<int:song_id>')
def get_mp3(song_id):
    sql = get_mp3_query(song_id)
    Song = namedtuple('Song', get_mp3_table)
    cur.execute(sql)
    info = [Song(*row) for row in cur.fetchall()][0]


    path = './static/mp3/'
    if download_song(info.title, info.artist, path):
        update_sql = update_data(song_id, 'mp3_check', 'mp3_url', f'.{path}{info.title}.mp3')
        cur.execute(update_sql)
        conn.commit()
    else:
        update_sql = update_fail_data(song_id, 'mp3_check')
        cur.execute(update_sql)
        conn.commit()


    return redirect(url_for('song_page', song_id=song_id))


@app.route('/karaoke/<int:song_id>')
def get_karaoke(song_id):
    sql = get_title_query(song_id)
    Song = namedtuple('Song', get_title_table)
    cur.execute(sql)
    info = [Song(*row) for row in cur.fetchall()][0]

    path = './static/karaoke/'
    if download_karaoke(info.title, path):
        update_sql = update_data(song_id, 'karaoke_check', 'karaoke_url', f'.{path}{info.title}_karaoke.mp3')
        cur.execute(update_sql)
        conn.commit()
    else:
        update_sql = update_fail_data(song_id, 'karaoke_check')
        cur.execute(update_sql)
        conn.commit()

    return redirect(url_for('song_page', song_id=song_id))


@app.route('/tab/<int:song_id>')
def get_tab(song_id):
    sql = get_title_query(song_id)
    Song = namedtuple('Song', get_title_table)
    cur.execute(sql)
    info = [Song(*row) for row in cur.fetchall()][0]

    path = './static/tab/'
    try:
        scraper = UltimateGuitarScraper(info.title)
        href = scraper.run_scrape()
        scraper.run_downloader(href)

        update_sql = update_data(song_id, 'tab_check', 'tab_url', f'.{path}{info.title}.pdf')
        cur.execute(update_sql)
        conn.commit()
    except:
        update_sql = update_fail_data(song_id, 'tab_check')
        cur.execute(update_sql)
        conn.commit()

    return redirect(url_for('song_page', song_id=song_id))


@app.route('/find-song', methods=['GET', 'POST'])
def find_song():
    if request.method == 'POST':
        input_title = request.form.get('title')
        input_artist = request.form.get('artist')
        input_mp3 = request.form.get('mp3YesNo')
        input_karaoke = request.form.get('karaokeYesNo')
        input_tab = request.form.get('tabYesNo')

        print(f'title: {input_title}, artist: {input_artist}, mp3: {input_mp3},\
              karaoke: {input_karaoke}, tab: {input_tab}')
        

        if input_title:
            compare_searches_query = query_search_terms(input_title)
            cur.execute(compare_searches_query)
            compare_searches_song_id = cur.fetchone()
            if compare_searches_song_id:
                print(compare_searches_song_id[0])
                #Connect User to song
            else:
                if input_artist:
                    title, artist, img_url = obtain_lyrics_get_img(GOOGLE_API_KEY, GOOGLE_CX, input_title, artist=input_artist)
                    print(f'{title}, {artist}, {img_url}')

                else:
                    title, artist, img_url = obtain_lyrics_get_img(GOOGLE_API_KEY, GOOGLE_CX, input_title)
                    print(f'{title}, {artist}, {img_url}')

                album, release_year = get_album_release_year(LAST_FM_API_KEY, title, artist)
                print(f'album: {album}, release-year{release_year}')






        # try:
        #     song_data = obtain_lyrics_create_dir(input_title)
        #     title = song_data[0]
        #     artist = song_data[1]
        #     path = f'./static/music/{title.lower()}/'
        # except:
        #     pass


        # try:
        #     download_song(title, artist, path)
        # except:
        #     pass


        # try:
        #     chords = Chords()
        #     chords.login_account(GUITAR_EMAIL, GUITAR_PASSWORD)
        #     chords.search_song(title)
        #     chords.save_pdf()
        #     move_from_downloads(path)
        # except:
        #     pass


        # return redirect(url_for('song_page', song=title.lower()))        

    return render_template('find-song.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)