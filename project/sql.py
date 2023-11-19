library_table = ['song_id', 'title', 'artist', 'img_url']


def library_songs(user_id):
    return f'''SELECT 
                    song.song_id, 
                    title, artist, 
                    url.img_url 
                FROM song
                INNER JOIN url ON song.song_id = url.song_id
                INNER JOIN user_song on user_song.song_id = song.song_id
                WHERE user_song.user_id = {user_id}
                ORDER BY title;'''


def catalogue_songs():
    return '''SELECT 
                    song.song_id, 
                    title, artist, 
                    url.img_url 
                FROM song
                INNER JOIN url ON song.song_id = url.song_id
                ORDER BY title;'''

song_page_table_user = ['song_id', 'title', 'artist',
                   'lyric_check', 'tab_check', 'mp3_check', 'karaoke_check',
                   'lyric_url', 'tab_url', 'mp3_url', 'karaoke_url', 'img_url', 'favorite_check']

song_page_table = ['song_id', 'title', 'artist',
                   'lyric_check', 'tab_check', 'mp3_check', 'karaoke_check',
                   'lyric_url', 'tab_url', 'mp3_url', 'karaoke_url', 'img_url']


def song_page_info(song_id, **kwargs):
    user_id = kwargs.get('user_id')
    if user_id:
        return f'''SELECT 
                        song.song_id, 
                        COALESCE(title, '') AS title, 
                        COALESCE(artist, '') AS artist, 
                        COALESCE(attempt.lyric_check, false) AS lyric_check, 
                        COALESCE(attempt.tab_check, false) AS tab_check, 
                        COALESCE(attempt.mp3_check, false) AS mp3_check, 
                        COALESCE(attempt.karaoke_check, false) AS karaoke_check,
                        COALESCE(url.lyric_url, '') AS lyric_url, 
                        COALESCE(url.tab_url, '') AS tab_url, 
                        COALESCE(url.mp3_url, '') AS mp3_url, 
                        COALESCE(url.karaoke_url, '') AS karaoke_url, 
                        COALESCE(url.img_url, '') AS img_url,
                        COALESCE(user_song.favorite, false) AS favorite_check
                    FROM song
                    INNER JOIN attempt ON song.song_id = attempt.song_id
                    INNER JOIN url ON song.song_id = url.song_id
                    INNER JOIN user_song ON user_song.song_id = song.song_id
                    WHERE song.song_id = {song_id} and user_song.user_id = {user_id};'''
    else:
        return f'''SELECT 
                        song.song_id, 
                        COALESCE(title, '') AS title, 
                        COALESCE(artist, '') AS artist, 
                        COALESCE(attempt.lyric_check, false) AS lyric_check, 
                        COALESCE(attempt.tab_check, false) AS tab_check, 
                        COALESCE(attempt.mp3_check, false) AS mp3_check, 
                        COALESCE(attempt.karaoke_check, false) AS karaoke_check,
                        COALESCE(url.lyric_url, '') AS lyric_url, 
                        COALESCE(url.tab_url, '') AS tab_url, 
                        COALESCE(url.mp3_url, '') AS mp3_url, 
                        COALESCE(url.karaoke_url, '') AS karaoke_url, 
                        COALESCE(url.img_url, '') AS img_url
                    FROM song
                    INNER JOIN attempt ON song.song_id = attempt.song_id
                    INNER JOIN url ON song.song_id = url.song_id
                    WHERE song.song_id = {song_id};'''


get_title_artist_table = ['song_id', 'title', 'artist']


def get_title_artist_query(song_id):
    return f'''
            SELECT song_id, title, artist FROM song
            WHERE song_id = {song_id};'''


def update_data(song_id, attempt, url, path):
    if "'" in path:
        path = path.replace("'", "''")
    return f'''
            UPDATE attempt SET {attempt} = True
            WHERE song_id = {song_id};

            UPDATE url SET {url} = '{path}'
            WHERE song_id = {song_id};'''


def update_fail_data(song_id, attempt):
    return f'''
            UPDATE attempt SET {attempt} = True
            WHERE song_id = {song_id}'''


get_title_table = ['song_id', 'title']


def get_title_query(song_id):
    return f'''
            SELECT song_id, title FROM song
            WHERE song_id = {song_id}'''


def query_search_terms(search):
    if "'" in search:
        search = search.replace("'", "''")
    return f'''
            SELECT song.song_id FROM searches
            INNER JOIN song_search ON searches.search_id = song_search.search_id
            INNER JOIN song ON song_search.song_id = song.song_id
            WHERE search_term ILIKE '{search}'
            GROUP BY song.song_id
            '''


def insert_new_song(title, artist):
    return f'''
            INSERT INTO song(title, artist)
            Values(
                '{title.replace("'", "''")}',
                '{artist.replace("'", "''")}'
            )'''


def get_song_id(title):
    if "'" in title:
        title = title.replace("'", "''")
    return f'''
            SELECT song_id FROM song
            WHERE title = '{title}'
            '''


def insert_new_record(song_id, table):
    return f'''
            INSERT INTO {table}(song_id)
            Values(
                '{song_id}'
            )
            '''


def update_value(song_id, table, field, value):
    '''song_id, table, field, and url'''
    if "'" in value:
        value = value.replace("'", "''")
    return f'''
            UPDATE {table} SET {field} = '{value}'
            WHERE song_id = {song_id}
            '''


def delete_song(song_id):
    return f'''
            DELETE FROM url
            WHERE song_id = {song_id};

            DELETE FROM attempt
            WHERE song_id = {song_id};

            DELETE FROM song
            WHERE song_id = {song_id};
            '''


def insert_new_search_term(new_search_term):
    return f'''
            INSERT INTO searches SET search_term = '{new_search_term}'
            '''


def search_term_id(search_term):
    return f'''
            SELECT search_id FROM searches
            WHERE search_term = '{search_term}'
            '''


def insert_new_song_search(song_id, search_id):
    return f'''
            INSERT INTO song_search(song_id, search_id)
            VALUES(
                {song_id},
                {search_id}
            )
            '''


def insert_attempt(song_id):
    return f'''
            INSERT INTO attempt(song_id)
            VALUES(
                {song_id}
            )
            '''


def get_pdf(song_id):
    return f'''
            SELECT tab_url FROM url
            WHERE song_id = {song_id}
            '''


def get_search_id(search_term):
    if "'" in search_term:
        search_term = search_term.replace("'", "''")
    return f'''
            SELECT search_id FROM searches
            WHERE search_term = '{search_term}'
            '''


def get_all_search_id(song_id):
    return f'''
            SELECT searches.search_id FROM searches
            INNER JOIN song_search ON song_search.search_id = searches.search_id
            INNER JOIN song ON song.song_id = song_search.song_id
            WHERE song.song_id = {song_id}
            '''

def delete_search_id(search_id):
    return f'''
            DELETE FROM song_search
            WHERE search_id = {search_id};

            DELETE FROM searches 
            WHERE search_id = {search_id};
            '''


def insert_new_search(search_term):
    if "'" in search_term:
        search_term = search_term.replace("'", "''")
    return f'''
            INSERT INTO searches(search_term)
            VALUES(
                '{search_term}'
            )
            '''


def insert_song_search(song_id, search_id):
    return f'''
            INSERT INTO song_search(song_id, search_id)
            VALUES(
                {song_id},
                {search_id}
            )
            '''


def insert_new_user(f_name, l_name, username, email, password):
    if "'" in f_name:
        f_name = f_name.replace("'", "''")
    if "'" in l_name:
        l_name = l_name.replace("'", "''")
    if "'" in username:
        username = username.replace("'", "''")
    if "'" in email:
        email = email.replace("'", "''")
    if "'" in password:
        password = password.replace("'", "''")

    return f'''
            INSERT INTO users(first_name, last_name, username, email, password)
            VALUES(
                '{f_name}',
                '{l_name}',
                '{username}',
                '{email}',
                '{password}'
            )
            '''

def get_user(email):
    if "'" in email:
        email = email.replace("'", "''")

    return f'''
            SELECT user_id, first_name, last_name, email, password, username FROM users
            WHERE email = '{email}'
            '''



user_table = ['user_id', 'email', 'password']



def insert_user_song(user_id, song_id):
    return f'''
            INSERT INTO user_song(user_id, song_id)
            VALUES(
                {user_id},
                {song_id}
            )
            '''


def get_favorites(user_id):
    return f'''
            SELECT song.song_id, song.title, song.artist, url.img_url FROM user_song
            INNER JOIN song ON song.song_id = user_song.song_id
            INNER JOIN users ON users.user_id = user_song.user_id
            INNER JOIN url ON url.song_id = song.song_id
            WHERE favorite = true and users.user_id = {user_id}
            ORDER BY song.title
            '''


def update_add_favorite(user_id, song_id):
    return f'''
            UPDATE user_song SET favorite = true
            WHERE user_id = {user_id} AND song_id = {song_id};
            '''


def update_remove_favorite(user_id, song_id):
    return f'''
            UPDATE user_song SET favorite = false
            WHERE user_id = {user_id} AND song_id = {song_id};
            '''