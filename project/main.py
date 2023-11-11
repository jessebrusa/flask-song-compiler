from flask import Flask, render_template, request, url_for, redirect, request, send_file, send_from_directory
from flask_caching import Cache
from ultimate_guitar_scraper import UltimateGuitarScraper
from tab_scraper import TabScraper
from all_music_scraper import AllMusicScraper
from asyncio_functions import gather_main
from resources import  *
from sql import *
import psycopg2 as pg2
from psycopg2 import pool
from collections import namedtuple
from dotenv import load_dotenv
import os
import asyncio
import threading


load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CX = os.getenv('GOOGLE_CX')
POSTGRES_PASS = os.getenv('POSTGRES_PASS')
LAST_FM_API_KEY = os.getenv('LAST_FM_API_KEY')
MUSIC_BRAINZ_CLIENT_ID = os.getenv('MUSIC_BRAINZ_CLIENT_ID')
MUSIC_BRAINZ_CLIENT_SECRET = os.getenv('MUSIC_BRAINZ_CLIENT_SECRET')
GENIUS_ACCESS_TOKEN = os.getenv('GENIUS_ACCESS_TOKEN')

# Set the maximum number of connections in the pool
max_connections = 5
connection_pool = pool.SimpleConnectionPool(
    max_connections,
    max_connections,
    database='song-compiler',
    user='postgres',
    password=POSTGRES_PASS,
    port=5433
)

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})



@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/library')
def library():
    conn = pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port='5433')
    cur = conn.cursor()

    songs_sql = library_songs()
    Song = namedtuple('Song', library_table)
    cur.execute(songs_sql)
    songs = [Song(*row) for row in cur.fetchall()]

    conn.close()

    return render_template('library.html', songs=songs)


@app.route('/song-page/<int:song_id>')
def song_page(song_id):
    conn = pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port='5433')
    cur = conn.cursor()

    song_page_sql = song_page_info(song_id)
    Song = namedtuple('Song', song_page_table)
    cur.execute(song_page_sql)
    info = [Song(*row) for row in cur.fetchall()][0]
    

    if info.lyric_url:
        with open(f'{info.lyric_url}', 'r') as file:
            lyrics = file.read().splitlines()
    else:
        lyrics = None

    conn.close()
 
    return render_template('song-page.html', info=info, lyrics=lyrics)


@app.route('/mp3/<int:song_id>')
def get_mp3(song_id):
    conn = pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port='5433')
    cur = conn.cursor()

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

    conn.close()

    return redirect(url_for('song_page', song_id=song_id))


@app.route('/karaoke/<int:song_id>')
def get_karaoke(song_id):
    conn = pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port='5433')
    cur = conn.cursor()

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

    conn.close()

    return redirect(url_for('song_page', song_id=song_id))


@app.route('/tab/<int:song_id>')
def get_tab(song_id):
    conn = pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port='5433')
    cur = conn.cursor()

    sql = get_title_query(song_id)
    Song = namedtuple('Song', get_title_table)
    cur.execute(sql)
    info = [Song(*row) for row in cur.fetchall()][0]

    path = './static/tab/'
    try:
        scraper = UltimateGuitarScraper(info.title)
        href = scraper.run_scrape()
        if href:
            scraper.run_downloader(href)

            update_sql = update_data(song_id, 'tab_check', 'tab_url', f'.{path}{info.title}.pdf')
            cur.execute(update_sql)
            conn.commit()
        else:
            update_sql = update_fail_data(song_id, 'tab_check')
            cur.execute(update_sql)
            conn.commit()
    except:
        update_sql = update_fail_data(song_id, 'tab_check')
        cur.execute(update_sql)
        conn.commit()

    conn.close

    return redirect(url_for('song_page', song_id=song_id))


@app.route('/find-song', methods=['GET', 'POST'])
def find_song():
    if request.method == 'POST':
        print('it made post')
        conn = pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port='5433')
        cur = conn.cursor()

        input_title = request.form.get('title')
        input_artist = request.form.get('artist')
        input_mp3 = request.form.get('mp3YesNo')
        input_karaoke = request.form.get('karaokeYesNo')
        input_tab = request.form.get('tabYesNo')
#########################################################################################################
        compare_searches_query = query_search_terms(input_title)
        cur.execute(compare_searches_query)
        compare_searches_song_id = cur.fetchone()
#########################################################################################################

        if compare_searches_song_id:
            print(compare_searches_song_id[0])
            song_id = compare_searches_song_id[0]
            print('caught before search')
            #Connect User to song

            return redirect(url_for('song_page', song_id=song_id))

#########################################################################################################
        
        else:
            print('getting more info')
            try:
                if input_artist:
                    all_music = AllMusicScraper(input_title, artist=input_artist)
                    title, artist = all_music.run_scrape()

                else:
                    all_music = AllMusicScraper(input_title)
                    title, artist = all_music.run_scrape()
            except:
                return render_template('song-not-found.html')
#########################################################################################################
            if title is None:
                return render_template('song-not-found.html')
#########################################################################################################      
      
            compare_searches_query = query_search_terms(title)
            cur.execute(compare_searches_query)
            compare_searches_song_id = cur.fetchone()

 #########################################################################################################           
            if compare_searches_song_id:
                print('Correct title does match a search')
                new_search_term_sql = update_value(song_id, 'searches', 'search_term', input_title)
                cur.execute(new_search_term_sql)
                conn.commit()
                #Connect User to song

                return redirect(url_for('song_page', song_id=song_id))
#########################################################################################################
            sql_new_song = insert_new_song(title, artist)
            cur.execute(sql_new_song)
            conn.commit()
            
            song_id_sql = get_song_id(title)
            cur.execute(song_id_sql)
            song_id = cur.fetchone()[0]

            insert_url_sql = insert_new_record(song_id, 'url')
            cur.execute(insert_url_sql)
            conn.commit()

            insert_attempt_sql = insert_new_record(song_id, 'attempt')
            cur.execute(insert_attempt_sql)
            conn.commit()
            
#########################################################################################################

            if artist:
                img_url = get_google_img(f'{title} {artist}', GOOGLE_API_KEY, GOOGLE_CX)
            else:
                img_url = get_google_img(title, GOOGLE_API_KEY, GOOGLE_CX)
            
            if img_url:
                img_url_sql = update_value(song_id, 'url', 'img_url', img_url)
                cur.execute(img_url_sql)
                conn.commit()

#########################################################################################################            
            try:
                if artist:
                    lyrics = get_lyrics(GENIUS_ACCESS_TOKEN, title, artist=artist)
                    if lyrics is None:
                        lyrics = obtain_lyrics(title, artist=artist)
                else:
                    lyrics = get_lyrics(GENIUS_ACCESS_TOKEN, title)
                    if lyrics is None:
                        lyrics = obtain_lyrics(title, artist=artist)
            except:
                lyrics = None

            if lyrics:
                with open(f'./static/lyric/{title}.txt', 'w', encoding='utf-8') as file:
                    file.write(lyrics)
                
                lyric_attempt_sql = update_value(song_id, 'attempt', 'lyric_check', 'true')
                cur.execute(lyric_attempt_sql)
                conn.commit()
                
                lyric_url_sql = update_value(song_id, 'url', 'lyric_url', f'./static/lyric/{title}.txt')
                cur.execute(lyric_url_sql)
                conn.commit()
            
            else:
                lyric_attempt_sql = update_value(song_id, 'attempt', 'lyric_check', 'true')
                cur.execute(lyric_attempt_sql)
                conn.commit()
#########################################################################################################
            # loop = asyncio.get_event_loop()
            # loop.run_until_complete(gather_main(song_id, input_mp3, input_karaoke, input_tab,
            #                         title, artist, cur, conn))
            # asyncio.run(gather_main(song_id, input_mp3, input_karaoke, input_tab,
            #                         title, artist, cur, conn))

            # asyncio_thread = threading.Thread(target=gather_main(song_id, input_mp3, input_karaoke, input_tab,
            #                         title, artist, cur, conn))
            # asyncio_thread.start()
            # asyncio_thread.join()

            print('beginning gather main')
            asyncio.run(gather_main(song_id, input_mp3, input_karaoke, input_tab,
                                    title, artist, 
                                    # GOOGLE_API_KEY, GOOGLE_CX, GENIUS_ACCESS_TOKEN, 
                                    cur, conn))





#             if input_mp3 == 'yes':
#                 path = './static/mp3/'
#                 if download_song(title, artist, path):
#                     update_sql = update_data(song_id, 'mp3_check', 'mp3_url', f'.{path}{title}.mp3')
#                     cur.execute(update_sql)
#                     conn.commit()
#                 else:
#                     update_sql = update_fail_data(song_id, 'mp3_check')
#                     cur.execute(update_sql)
#                     conn.commit()

# #########################################################################################################
            
#             if input_karaoke == 'yes':
#                 path = './static/karaoke/'
#                 if download_karaoke(title, path):
#                     update_sql = update_data(song_id, 'karaoke_check', 'karaoke_url', f'.{path}{title}_karaoke.mp3')
#                     cur.execute(update_sql)
#                     conn.commit()
#                 else:
#                     update_sql = update_fail_data(song_id, 'karaoke_check')
#                     cur.execute(update_sql)
#                     conn.commit()

# #########################################################################################################
            
#             if input_tab == 'yes':
#                 path = './static/tab/'
#                 try:
#                     scraper = UltimateGuitarScraper(title)
#                     href = scraper.run_scrape()
#                     if href:
#                         scraper.run_downloader(href)

#                         update_sql = update_data(song_id, 'tab_check', 'tab_url', f'.{path}{title}.pdf')
#                         cur.execute(update_sql)
#                         conn.commit()
#                     else:
#                         update_sql = update_fail_data(song_id, 'tab_check')
#                         cur.execute(update_sql)
#                         conn.commit()
#                 except:
#                     update_sql = update_fail_data(song_id, 'tab_check')
#                     cur.execute(update_sql)
#                     conn.commit()
            
            conn.close()

            return redirect(url_for('song_page', song_id=song_id))
   

    return render_template('find-song.html')


@app.route('/delete-song/<int:song_id>')
def delete_song_page(song_id):
    conn = pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port='5433')
    cur = conn.cursor()

    delete_sql = delete_song(song_id)
    cur.execute(delete_sql)
    conn.commit()
    conn.close()

    return redirect(url_for('library'))


@app.route('/loading')
def loading_page():
    return render_template('loading.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)