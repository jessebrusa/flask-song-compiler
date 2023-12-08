from flask import Flask, render_template, request, url_for, redirect, session, jsonify, flash
from flask_login import LoginManager, current_user, logout_user, login_required, UserMixin, login_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from python_resources.all_music_scraper import AllMusicScraper
from python_resources.asyncio_functions import gather_main
from python_resources.resources import  *
from python_resources.sql import *
import psycopg2 as pg2
from psycopg2.errors import UniqueViolation
from collections import namedtuple
from dotenv import load_dotenv
import os
import asyncio



load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CX = os.getenv('GOOGLE_CX')
POSTGRES_PASS = os.getenv('POSTGRES_PASS')
LAST_FM_API_KEY = os.getenv('LAST_FM_API_KEY')
MUSIC_BRAINZ_CLIENT_ID = os.getenv('MUSIC_BRAINZ_CLIENT_ID')
MUSIC_BRAINZ_CLIENT_SECRET = os.getenv('MUSIC_BRAINZ_CLIENT_SECRET')
GENIUS_ACCESS_TOKEN = os.getenv('GENIUS_ACCESS_TOKEN')
POSTGRES_URI = os.getenv('POSTGRES_URI')
pg_port_num = os.getenv('pg_port_num')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'la;sdjfaowiherojiqwke208935uijrklnwfd80ujioo23'
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URI
db = SQLAlchemy(app)
login_manager = LoginManager(app)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(128))  
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    username = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    site_admin = db.Column(db.Boolean, default=False)

    def __init__(self, first_name, last_name, username, email, password, site_admin=False):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password = password 
        self.site_admin = site_admin

    def get_id(self):
        return str(self.user_id)


@app.login_manager.user_loader
def load_user(user_id):
    if user_id is not None and user_id.isdigit():
        return User.query.get(int(user_id))
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login_page'))
    return decorated_function


@app.route('/')
def home_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    return render_template('index.html')


@app.route('/library')
@login_required
def library():
    user_id = current_user.user_id

    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            songs_sql = library_songs(user_id)
            Song = namedtuple('Song', library_table)
            cur.execute(songs_sql)
            songs = [Song(*row) for row in cur.fetchall()]


    return render_template('library.html', songs=songs)


@app.route('/catalogue')
def catalogue():
    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            if current_user.is_authenticated:
                user_id = current_user.user_id

                Song = namedtuple('Song', library_table)
                cur.execute(catalogue_songs(), (user_id, ))
                songs = [Song(*row) for row in cur.fetchall()]

            else:
                Song = namedtuple('Song', library_table)
                cur.execute(all_catalogue_songs())
                songs = [Song(*row) for row in cur.fetchall()]

    return render_template('catalogue.html', songs=songs)


@app.route('/dashboard')
@login_required
def dashboard():
    user_id = current_user.user_id

    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            cur.execute(get_favorites(user_id))
            favorite_songs_list = cur.fetchall()

            favorite_songs = []
            for song in favorite_songs_list:
                favorite_songs.append(
                        {
                        'song_id': song[0],
                        'title': song[1],
                        'artist': song[2],
                        'img': song[3]
                    }
                ) 


            cur.execute(get_party(), (user_id, ))
            parties_list = cur.fetchall()

            parties = []
            for party in parties_list:
                parties.append(
                    {
                        'party_id': party[0],
                        'name': party[1],
                        'accept': party[2],
                        'administrator': party[3]
                    }
                )


    return render_template('dashboard.html', favorite_songs=favorite_songs, parties=parties)


@app.route('/visit-dashboard/<int:user_id>')
def visit_dashboard(user_id):
    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            cur.execute(get_username(), (user_id, ))
            username = cur.fetchone()[0]

            cur.execute(get_favorites(user_id))
            favorite_songs_list = cur.fetchall()

            favorite_songs = []
            for song in favorite_songs_list:
                favorite_songs.append(
                        {
                        'song_id': song[0],
                        'title': song[1],
                        'artist': song[2],
                        'img': song[3]
                    }
                ) 


            cur.execute(get_party(), (user_id, ))
            parties_list = cur.fetchall()

            parties = []
            for party in parties_list:
                parties.append(
                    {
                        'party_id': party[0],
                        'name': party[1],
                        'accept': party[2],
                        'administrator': party[3]
                    }
                )


    return render_template('visit-dashboard.html', favorite_songs=favorite_songs, parties=parties, username=username)


@app.route('/group-page/<int:party_id>')
@login_required
def group_page(party_id):
    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            user_id = current_user.user_id
            cur.execute(get_party_info(), (party_id, user_id))
            party_data = cur.fetchone()

            if len(party_data) == 4:
                info = {
                    'party_id': party_data[0],
                    'name': party_data[1],
                    'description': party_data[2],
                    'administrator': party_data[3]
                }
            else:
                info = {
                    'party_id': party_data[0],
                    'name': party_data[1],
                    'administrator': party_data[2]
                }

            cur.execute(get_party_songs(), (party_id, ))
            songs_list = cur.fetchall()

            songs = []
            for song in songs_list:
                songs.append(
                    {
                        'song_id': song[0],
                        'title': song[1],
                        'artist': song[2],
                        'img_url': song[3]
                    }
                )

            cur.execute(get_party_users(), (party_id, ))
            users_list = cur.fetchall()

            users = []
            for user in users_list:
                users.append(
                    {
                        'username': user[0],
                        'administrator': user[1],
                        'user_id': user[2]
                    }
                )


    return render_template('group.html', info=info, songs=songs, users=users)


@app.route('/visit-group-page/<int:party_id>')
def visit_group_page(party_id):
    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            cur.execute(get_party_info_visit(), (party_id, ))
            party_data = cur.fetchone()
            print(party_data)
            if party_data:
                if len(party_data) == 3:
                    info = {
                        'party_id': party_data[0],
                        'name': party_data[1],
                        'description': party_data[2],
                    }
                else:
                    info = {
                        'party_id': party_data[0],
                        'name': party_data[1],
                    }
            else:
                info = None

            cur.execute(get_party_songs(), (party_id, ))
            songs_list = cur.fetchall()

            songs = []
            for song in songs_list:
                songs.append(
                    {
                        'song_id': song[0],
                        'title': song[1],
                        'artist': song[2],
                        'img_url': song[3]
                    }
                )

    return render_template('visit-group.html', info=info, songs=songs)


@app.route('/select-group/<int:song_id>')
@login_required
def select_group(song_id):
    user_id = current_user.user_id

    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            

            cur.execute(get_party(), (user_id, ))
            parties_list = cur.fetchall()

            parties = []
            for party in parties_list:
                parties.append(
                    {
                        'party_id': party[0],
                        'name': party[1],
                        'accept': party[2],
                        'administrator': party[3]
                    }
                )


            user_id = current_user.user_id
            song_page_sql = song_page_info(song_id, user_id=user_id)
            Song = namedtuple('Song', song_page_table_user)
            cur.execute(song_page_sql)
            info = [Song(*row) for row in cur.fetchall()][0]
            

    return render_template('select-group.html', parties=parties, info=info)


@app.route('/connect-group-song/<int:party_id>/<int:song_id>')
@login_required
def connect_group_song(party_id, song_id):
    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            cur.execute(insert_party_song(), (party_id, song_id))
            conn.commit()

    return redirect(url_for('group_page', party_id=party_id))


@app.route('/make-user-group-admin/<int:party_id>/<int:user_id>')
@login_required
def make_user_group_admin(party_id, user_id):
    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            cur.execute(update_user_party_admin(), (party_id, user_id))

    return redirect(url_for('group_page', party_id=party_id))


@app.route('/remove-song-from-group/<int:party_id>/<int:song_id>')
@login_required
def remove_song_from_group(party_id, song_id):
    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            user_id = current_user.user_id
            cur.execute(get_party_info(), (party_id, user_id))
            party_data = cur.fetchone()

            if len(party_data) == 4:
                info = {
                    'party_id': party_data[0],
                    'name': party_data[1],
                    'description': party_data[2],
                    'administrator': party_data[3]
                }
            else:
                info = {
                    'party_id': party_data[0],
                    'name': party_data[1],
                    'administrator': party_data[2]
                }



            if info['administrator']:
                cur.execute(delete_remove_song_group(), (party_id, song_id))
                conn.commit()


    return redirect(url_for('group_page', party_id=party_id))


@app.route('/delete-group/<int:party_id>')
@login_required
def delete_group(party_id):
    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            user_id = current_user.user_id
            cur.execute(get_party_info(), (party_id, user_id))
            party_data = cur.fetchone()

            if len(party_data) == 4:
                info = {
                    'party_id': party_data[0],
                    'name': party_data[1],
                    'description': party_data[2],
                    'administrator': party_data[3]
                }
            else:
                info = {
                    'party_id': party_data[0],
                    'name': party_data[1],
                    'administrator': party_data[2]
                }



            if info['administrator']:
                cur.execute(delete_party(), (party_id, party_id, party_id))
                conn.commit()


    return redirect(url_for('dashboard'))


@app.route('/edit-group-name/<int:party_id>', methods=['GET', 'POST'])
@login_required
def edit_group_name(party_id):
    if request.method == 'POST':
        new_name = request.form.get('group_name')

        if new_name:
            with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
                with conn.cursor() as cur:
                    cur.execute(update_group_name(), (new_name, party_id))
                    conn.commit()

        return redirect(url_for('group_page', party_id=party_id))

    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            user_id = current_user.user_id
            cur.execute(get_party_info(), (party_id, user_id))
            party_data = cur.fetchone()

            if len(party_data) == 4:
                info = {
                    'party_id': party_data[0],
                    'name': party_data[1],
                    'description': party_data[2],
                    'administrator': party_data[3]
                }
            else:
                info = {
                    'party_id': party_data[0],
                    'name': party_data[1],
                    'administrator': party_data[2]
                }


    return render_template('edit-name.html', info=info)


@app.route('/edit-description/<int:party_id>', methods=['GET', 'POST'])
@login_required
def edit_description(party_id):
    if request.method == 'POST':
        new_description = request.form.get('description_box')

        if new_description:
            with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
                with conn.cursor() as cur:
                    cur.execute(update_description(), (new_description, party_id))
                    conn.commit()

        return redirect(url_for('group_page', party_id=party_id))

    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            user_id = current_user.user_id
            cur.execute(get_party_info(), (party_id, user_id))
            party_data = cur.fetchone()

            if len(party_data) == 4:
                info = {
                    'party_id': party_data[0],
                    'name': party_data[1],
                    'description': party_data[2],
                    'administrator': party_data[3]
                }
            else:
                info = {
                    'party_id': party_data[0],
                    'name': party_data[1],
                    'administrator': party_data[2]
                }

            if info['description']:
                description = info['description']
            else:
                description = None

    return render_template('edit-description.html', description=description, info=info)


@app.route('/leave-group/<int:party_id>')
@login_required
def leave_group(party_id):
    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            user_id = current_user.user_id
            cur.execute(delete_leave_group(), (user_id, party_id))
            conn.commit()

    return redirect(url_for('dashboard'))


@app.route('/accept-group/<int:party_id>')
@login_required
def accept_group(party_id):
    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            user_id = current_user.user_id
            cur.execute(update_accept_group(), (user_id, party_id))
            conn.commit()

    return redirect(url_for('dashboard'))


@app.route('/invite-user/<int:party_id>', methods=['GET', 'POST'])
@login_required
def invite_user(party_id):
    if request.method == 'POST':
        inv_username = request.form.get('username')
        inv_admin = request.form.get('adminYesNo')
        if inv_admin == 'yes':
            inv_admin = True
        else:
            inv_admin = False

        with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
                with conn.cursor() as cur:
                    try:
                        cur.execute(get_user_id(), (inv_username,))
                        inv_user_id = cur.fetchone()[0]

                        cur.execute(add_user_group(), (party_id, inv_user_id, inv_admin))
                        conn.commit()
                    except:
                        return redirect(url_for('dashboard'))
                                      
        return redirect(url_for('group_page', party_id=party_id))

    return render_template('invite-user.html', party_id=party_id)


@app.route('/add-favorite/<int:song_id>')
@login_required
def add_favorite(song_id):
    user_id = current_user.user_id

    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            cur.execute(update_add_favorite(user_id, song_id))
            conn.commit()

    return redirect(url_for('song_page', song_id=song_id))


@app.route('/remove-favorite/<int:song_id>')
@login_required
def remove_favorite(song_id):
    user_id = current_user.user_id

    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            cur.execute(update_remove_favorite(user_id, song_id))
            conn.commit()

    return redirect(url_for('song_page', song_id=song_id))


@app.route('/create-group', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        group_name = request.form.get('group_name')
        description = request.form.get('description_box')
  

        with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
            with conn.cursor() as cur:
                if description:
                    cur.execute(insert_create_group(group_name, description=description))
                else:
                    cur.execute(insert_create_group(group_name))

                party_id = cur.fetchone()[0]
                user_id = current_user.user_id

                cur.execute(insert_party_user_admin(), (party_id, user_id))


                conn.commit()


                return redirect(url_for('group_page', party_id=party_id))
                


    return render_template('create-group.html')


@app.route('/connect-song/<int:song_id>')
@login_required
def connect_song(song_id):
    user_id = current_user.user_id
    
    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            cur.execute(insert_user_song(), (user_id, song_id))
            conn.commit()


    return redirect(url_for('song_page', song_id=song_id))


@app.route('/song-page/<int:song_id>')
def song_page(song_id):
    conn = pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num)
    cur = conn.cursor()
    song_in_library = None
    site_admin = None

    if current_user.is_authenticated:
        user_id = current_user.user_id
        cur.execute(check_site_admin(), (user_id, ))
        site_admin = cur.fetchone()[0]

        cur.execute(user_song_library(), (user_id, song_id))
        song_in_library = cur.fetchone()

        if song_in_library:
            song_page_sql = song_page_info(song_id, user_id=user_id)
            cur.execute(song_page_sql)
            song_list = cur.fetchone()
            
            info = {
                'song_id': song_list[0],
                'title': song_list[1],
                'artist': song_list[2],
                'lyric_check': song_list[3],
                'tab_check': song_list[4],
                'mp3_check': song_list[5],
                'karaoke_check': song_list[6],
                'lyric_url': song_list[7],
                'tab_url': song_list[8],
                'mp3_url': song_list[9],
                'karaoke_url': song_list[10],
                'img_url': song_list[11],
                'favorite_check': song_list[12]
            }
        else:
            song_page_sql = song_page_info(song_id)
            cur.execute(song_page_sql)
            song_list = cur.fetchone()

            info = {
                'song_id': song_list[0],
                'title': song_list[1],
                'artist': song_list[2],
                'lyric_check': song_list[3],
                'tab_check': song_list[4],
                'mp3_check': song_list[5],
                'karaoke_check': song_list[6],
                'lyric_url': song_list[7],
                'tab_url': song_list[8],
                'mp3_url': song_list[9],
                'karaoke_url': song_list[10],
                'img_url': song_list[11]
            }
        
    else:
        song_page_sql = song_page_info(song_id)
        cur.execute(song_page_sql)
        song_list = cur.fetchone()

        info = {
            'song_id': song_list[0],
            'title': song_list[1],
            'artist': song_list[2],
            'lyric_check': song_list[3],
            'tab_check': song_list[4],
            'mp3_check': song_list[5],
            'karaoke_check': song_list[6],
            'lyric_url': song_list[7],
            'tab_url': song_list[8],
            'mp3_url': song_list[9],
            'karaoke_url': song_list[10],
            'img_url': song_list[11]
        }
    

    if info['lyric_url']:
        with open(f'{info["lyric_url"]}', 'r') as file:
            lyrics = file.read().splitlines()
    else:
        lyrics = None

    conn.close()
 
    return render_template('song-page.html', info=info, lyrics=lyrics, song_in_library=song_in_library,
                           site_admin=site_admin)


@app.route('/mp3/<int:song_id>')
def get_mp3(song_id):
    conn = pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num)
    cur = conn.cursor()

    sql = get_title_artist_query(song_id)
    Song = namedtuple('Song', get_title_artist_table)
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
    conn = pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num)
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
    conn = pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num)
    cur = conn.cursor()

    sql = get_title_artist_query(song_id)
    Song = namedtuple('Song', get_title_artist_table)
    cur.execute(sql)
    info = [Song(*row) for row in cur.fetchall()][0]


    asyncio.run(gather_main(song_id, 'no', 'no', 'yes',
                                    info.title, info.artist, 
                                    cur, conn))


    return redirect(url_for('song_page', song_id=song_id))


@app.route('/edit-title/<int:song_id>', methods=['GET', 'POST'])
@login_required
def edit_title(song_id):
    if request.method == 'POST':
        input_title = request.form.get('title')

        if input_title:
            with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
                with conn.cursor() as cur:
                    cur.execute(update_edit_title(), (input_title, song_id))
                    conn.commit()

        return redirect(url_for('song_page', song_id=song_id))

    return render_template('edit-title.html', song_id=song_id)


@app.route('/edit-artist/<int:song_id>', methods=['GET', 'POST'])
@login_required
def edit_artist(song_id):
    if request.method == 'POST':
        input_artist = request.form.get('artist')

        if input_artist:
            with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
                with conn.cursor() as cur:
                    cur.execute(update_edit_artist(), (input_artist, song_id))
                    conn.commit()

        return redirect(url_for('song_page', song_id=song_id))

    return render_template('edit-artist.html', song_id=song_id)


@app.route('/edit-img/<int:song_id>', methods=['GET', 'POST'])
@login_required
def edit_img(song_id):
    if request.method == 'POST':
        input_img = request.form.get('img_url')

        if input_img:
            with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
                with conn.cursor() as cur:
                    cur.execute(update_edit_img(), (input_img, song_id))
                    conn.commit()

        return redirect(url_for('song_page', song_id=song_id))

    return render_template('edit-img.html', song_id=song_id)


@app.route('/edit-mp3/<int:song_id>/<string:title>', methods=['GET', 'POST'])
@login_required
def edit_mp3(song_id, title):
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('song_page', song_id=song_id))
        
        file = request.files['file']

        if file.filename == '':
            return redirect(url_for('song_page', song_id=song_id))
        
        if file:
            filename = f'{title}.mp3'

            path = f'./static/mp3/{filename}'

            file.save(path)

            with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
                with conn.cursor() as cur:
                    cur.execute(update_edit_mp3(), (f'.{path}', song_id))
                    conn.commit()

        return redirect(url_for('song_page', song_id=song_id))

    return render_template('edit-mp3.html', song_id=song_id, title=title)


@app.route('/edit-karaoke/<int:song_id>/<string:title>', methods=['GET', 'POST'])
@login_required
def edit_karaoke(song_id, title):
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('song_page', song_id=song_id))
        
        file = request.files['file']

        if file.filename == '':
            return redirect(url_for('song_page', song_id=song_id))
        
        if file:
            filename = f'{title}_karaoke.mp3'

            path = f'./static/karaoke/{filename}'

            file.save(path)

            with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
                with conn.cursor() as cur:
                    cur.execute(update_edit_karaoke(), (f'.{path}', song_id))
                    conn.commit()

        return redirect(url_for('song_page', song_id=song_id))

    return render_template('edit-karaoke.html', song_id=song_id, title=title)


@app.route('/edit-tab/<int:song_id>/<string:title>', methods=['GET', 'POST'])
@login_required
def edit_tab(song_id, title):
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('song_page', song_id=song_id))
        
        file = request.files['file']

        if file.filename == '':
            return redirect(url_for('song_page', song_id=song_id))
        
        if file:
            filename = f'{title}.pdf'

            path = f'./static/tab/{filename}'

            file.save(path)

            with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
                with conn.cursor() as cur:
                    cur.execute(update_edit_tab(), (f'.{path}', song_id))
                    conn.commit()

        return redirect(url_for('song_page', song_id=song_id))

    return render_template('edit-tab.html', song_id=song_id, title=title)


@app.route('/edit-lyric/<int:song_id>/<string:title>', methods=['GET', 'POST'])
@login_required
def edit_lyric(song_id, title):
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('song_page', song_id=song_id))
        
        file = request.files['file']

        if file.filename == '':
            return redirect(url_for('song_page', song_id=song_id))
        
        if file:
            filename = f'{title}.txt'

            path = f'./static/lyric/{filename}'

            file.save(path)

            with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
                with conn.cursor() as cur:
                    cur.execute(update_edit_lyric(), (path, song_id))
                    conn.commit()

        return redirect(url_for('song_page', song_id=song_id))

    return render_template('edit-lyric.html', song_id=song_id, title=title)


@app.route('/find-song', methods=['GET', 'POST'])
@login_required
def find_song():
    if request.method == 'POST':
        conn = pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num)
        cur = conn.cursor()

        input_title = request.form.get('title')
        input_artist = request.form.get('artist')
        input_mp3 = request.form.get('mp3YesNo')
        input_karaoke = request.form.get('karaokeYesNo')
        input_tab = request.form.get('tabYesNo')

        user_id = current_user.user_id
#########################################################################################################
        cur.execute(query_search_terms(), (input_title, ))
        compare_searches_song_id = cur.fetchone()
#########################################################################################################

        if compare_searches_song_id:
            song_id = compare_searches_song_id[0]

            

            with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
                with conn.cursor() as cur:
                    try:
                        cur.execute(insert_user_song(), (user_id, song_id))
                        conn.commit()
                    except pg2.errors.UniqueViolation:
                        redirect_url = url_for('song_page', song_id=song_id)
                        return jsonify({'redirect': redirect_url})

            redirect_url = url_for('song_page', song_id=song_id)
            return jsonify({'redirect': redirect_url})



#########################################################################################################
                    
        else:
            try:
                if input_artist:
                    all_music = AllMusicScraper(input_title, artist=input_artist)
                    title, artist = all_music.run_scrape()

                else:
                    all_music = AllMusicScraper(input_title)
                    title, artist = all_music.run_scrape()
            except:
                redirect_url = url_for('song_not_found')
                return jsonify({'redirect': redirect_url})
    
#########################################################################################################
            if title is None:
                redirect_url = url_for('song_not_found')
                return jsonify({'redirect': redirect_url})

#########################################################################################################      
        
            cur.execute(query_search_terms(), (title, ))
            compare_searches_song_id = cur.fetchone()

#########################################################################################################           
        if compare_searches_song_id:
            new_search_term_sql = update_value(song_id, 'searches', 'search_term', input_title)
            cur.execute(new_search_term_sql)
            conn.commit()

            with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
                with conn.cursor() as cur:
                    try:
                        cur.execute(insert_user_song(user_id, song_id))
                        conn.commit()
                    except pg2.errors.UniqueViolation:
                        redirect_url = url_for('song_page', song_id=song_id)
                        return jsonify({'redirect': redirect_url})

            redirect_url = url_for('song_page', song_id=song_id)
            return jsonify({'redirect': redirect_url})


#########################################################################################################
        cur.execute(insert_new_song(), (title, artist))

        cur.execute(get_song_id(), (title, ))
        song_id = cur.fetchone()[0]

        cur.execute(insert_user_song(), (user_id, song_id))

        cur.execute(insert_new_search(), (input_title, ))

        cur.execute(search_term_id(), (input_title, ))
        input_search_id = cur.fetchone()[0]

        cur.execute(insert_song_search(), (song_id, input_search_id))
        
        cur.execute(insert_new_search(), (title, ))
    
        cur.execute(search_term_id(), (title, ))
        search_id = cur.fetchone()[0]

        cur.execute(insert_song_search(), (song_id, search_id))
    

        insert_url_sql = insert_new_record(song_id, 'url')
        cur.execute(insert_url_sql)


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
        lyrics = obtain_lyrics(title)
        if lyrics is None:
            lyrics = get_lyrics(GENIUS_ACCESS_TOKEN, title)


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
      
        asyncio.run(gather_main(song_id, input_mp3, input_karaoke, input_tab,
                                title, artist, 
                                cur, conn))
    
        conn.close()

        redirect_url = url_for('song_page', song_id=song_id)
        return jsonify({'redirect': redirect_url})
        

    return render_template('find-song.html')


@app.route('/remove-song/<int:song_id>')
def remove_song(song_id):
    user_id = current_user.user_id
    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            cur.execute(remove_user_song(), (user_id, song_id))
            conn.commit()
    return redirect(url_for('library'))


@app.route('/delete-song/<int:song_id>')
@login_required
def delete_song(song_id):
    with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
        with conn.cursor() as cur:
            song_page_sql = song_page_info(song_id)
            cur.execute(song_page_sql)
            song_list = cur.fetchone()

            info = {
                'song_id': song_list[0],
                'title': song_list[1],
                'artist': song_list[2],
                'lyric_check': song_list[3],
                'tab_check': song_list[4],
                'mp3_check': song_list[5],
                'karaoke_check': song_list[6],
                'lyric_url': song_list[7],
                'tab_url': song_list[8],
                'mp3_url': song_list[9],
                'karaoke_url': song_list[10],
                'img_url': song_list[11]
            }

            try:
                if info['mp3_url']:
                    os.remove(info['mp3_url'][1:])
            except FileNotFoundError:
                print('Mp3 file not found')
            except Exception as e:
                print(f'An error occurred {e}')

            try:
                if info['karaoke_url']:
                    os.remove(info['karaoke_url'][1:])
            except FileNotFoundError:
                print('Karaoke file not found')
            except Exception as e:
                print(f'An error occurred {e}')

            try:
                if info['lyric_url']:
                    os.remove(info['lyric_url'])
            except FileNotFoundError:
                print('Lyric file not found')
            except Exception as e:
                print(f'An error occurred {e}')

            try:
                if info['tab_url']:
                    os.remove(info['tab_url'][1:])
            except FileNotFoundError:
                print('Tab file not found')
            except Exception as e:
                print(f'An error occurred {e}')


            cur.execute(get_all_search_id(), (song_id, ))
            all_search_id = cur.fetchall()

            for search_id in all_search_id:
                cur.execute(delete_search_id(), (search_id, search_id))

            cur.execute(delete_party_song(), (song_id, ))

            cur.execute(delete_song_db(), (song_id, song_id, song_id, 
                                        song_id, song_id))

            conn.commit()


    return redirect(url_for('library'))


@app.route('/song-not-found')
def song_not_found():
    return render_template('song-not-found.html')


@app.route('/loading')
def loading_page():
    return render_template('loading.html')


@app.route('/register-page', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        username = request.form.get('username').lower()
        email = request.form.get('email')
        password = request.form.get('password')

        pass_hash = generate_password_hash(password)

        try:
            with pg2.connect(database='song-compiler', user='postgres', password=POSTGRES_PASS, port=pg_port_num) as conn:
                with conn.cursor() as cur:
                    cur.execute(insert_new_user(), (f_name, l_name, username, email, pass_hash,))
                    user_id = cur.fetchone()[0]
                    conn.commit()

                    user_object = User.query.filter_by(user_id=user_id).first()
                    login_user(user_object)

                    if current_user.is_authenticated: 
                        return redirect(url_for('dashboard'))  
                    else:
                        flash('There was an issue logging in. Please try again.')
                        return redirect(url_for('login_page'))  
                    
        except UniqueViolation as e:
            error_message = str(e)
            print(error_message)
            if 'email' in error_message:
                print('Email already exists.')
                flash('Email already exists.')
                return render_template('register.html')
            elif 'username' in error_message:
                flash('Username already exists.')
                return render_template('register.html')

    return render_template('register.html')


@app.route('/login-page', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        password_input = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password_input):
                login_user(user)
                if current_user.is_authenticated:
                    flash('Logged in successfully.')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid password.')
        else:
            flash('Invalid email.')
    return render_template('login.html')   


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('home_page'))


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')