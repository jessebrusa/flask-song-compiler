library_table = ['song_id', 'title', 'artist', 'img_url']


def library_songs(user_id):
    return f'''SELECT DISTINCT
                    song.song_id, 
                    title, artist, 
                    url.img_url 
                FROM song
                INNER JOIN url ON song.song_id = url.song_id
                INNER JOIN user_song on user_song.song_id = song.song_id
                WHERE user_song.user_id = {user_id}
                ORDER BY title;'''


def catalogue_songs():
    return '''
            SELECT 
                song.song_id, 
                song.title, 
                song.artist, 
                url.img_url
            FROM song
            INNER JOIN url ON song.song_id = url.song_id
            LEFT JOIN user_song ON song.song_id = user_song.song_id AND user_song.user_id = 1
            WHERE user_song.user_id IS NULL
            ORDER BY song.title;
        '''

def all_catalogue_songs():
    return '''
            SELECT 
                song.song_id,
                song.title,
                song.artist,
                url.img_url
            FROM song
            INNER JOIN url ON song.song_id = url.song_id
            ORDER BY song.title;
            '''

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


def user_song_library():
    return '''
            SELECT song_id FROM user_song
            WHERE user_id = %s AND song_id = %s
            '''

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


def query_search_terms():
    return '''
            SELECT song.song_id FROM searches
            INNER JOIN song_search ON searches.search_id = song_search.search_id
            INNER JOIN song ON song_search.song_id = song.song_id
            WHERE search_term ILIKE %s
            GROUP BY song.song_id;
            '''


def insert_new_song():
    return '''
            INSERT INTO song(title, artist)
            Values(
                %s,
                %s
            );
            '''


def get_song_id():
    return '''
            SELECT song_id FROM song
            WHERE title = %s;
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


def delete_song_db():
    return '''
            DELETE FROM user_song
            WHERE song_id = %s;

            DELETE FROM url
            WHERE song_id = %s;

            DELETE FROM attempt
            WHERE song_id = %s;

            DELETE FROM party_song
            WHERE song_id = %s;

            DELETE FROM song
            WHERE song_id = %s;
            '''


def insert_new_search_term(new_search_term):
    return f'''
            INSERT INTO searches SET search_term = '{new_search_term}'
            '''


def search_term_id():
    return '''
            SELECT search_id FROM searches
            WHERE search_term = %s;
            '''


def insert_new_song_search():
    return '''
            INSERT INTO song_search(song_id, search_id)
            VALUES(
                %s,
                %s
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


def get_all_search_id():
    return '''
            SELECT searches.search_id FROM searches
            INNER JOIN song_search ON song_search.search_id = searches.search_id
            INNER JOIN song ON song.song_id = song_search.song_id
            WHERE song.song_id = %s;
            '''

def delete_search_id():
    return '''
            DELETE FROM song_search
            WHERE search_id = (%s);

            DELETE FROM searches 
            WHERE search_id = (%s);
            '''


def delete_party_song():
    return '''
            DELETE FROM party_song
            WHERE song_id = %s;
            '''


def insert_new_search():
    return '''
            INSERT INTO searches(search_term)
            VALUES(
                %s
            );
            '''


def insert_song_search():
    return '''
            INSERT INTO song_search(song_id, search_id)
            VALUES(
                %s,
                %s
            )
            '''


def insert_new_user():
    query = """
    INSERT INTO users (first_name, last_name, username, email, password)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING user_id;
    """
    return query

def get_user():
    return '''
            SELECT user_id, first_name, last_name, email, password, username, site_admin FROM users
            WHERE email = %s
            '''


def check_site_admin():
    return '''
            SELECT site_admin FROM users
            WHERE user_id = %s;
            '''


user_table = ['user_id', 'email', 'password']



def insert_user_song():
    return '''
            INSERT INTO user_song(user_id, song_id)
            VALUES(
                %s,
                %s
            );
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


def insert_create_group(name, **kwargs):
    description = kwargs.get('description')
    if "'" in name:
        name = name.replace("'", "''")
    if description:
        if "'" in description:
            description = description.replace("'", "''")
    if description:
        return f'''
                INSERT INTO party(name, description)
                VALUES(
                    '{name}',
                    '{description}'
                )
                RETURNING party_id;
                '''
    else:
        return f'''
                INSERT INTO party(name)
                VALUES(
                    '{name}'
                )
                RETURNING party_id;
                '''
    

def insert_party_user_admin():
    return '''
            INSERT INTO party_user(party_id, user_id, accept, administrator)
            VALUES (%s, %s, true, true);
            '''

def get_party():
    return '''
            SELECT party_user.party_id, party.name, party_user.accept, party_user.administrator FROM party_user
            INNER JOIN party ON party.party_id = party_user.party_id
            WHERE party_user.user_id = %s;
            '''


def get_party_info():
    return '''
            SELECT party.party_id, party.name, party.description, party_user.administrator
            FROM party
            INNER JOIN party_user ON party_user.party_id = party.party_id
            WHERE party.party_id = %s AND party_user.user_id = %s;
            '''


def get_party_info_visit():
    return '''
            SELECT party_id, name, description
            FROM party
            WHERE party.party_id = %s;           
            '''


def get_party_songs():
    return '''
            SELECT 
                song.song_id,
                song.title,
                song.artist,
                url.img_url
            FROM party
            INNER JOIN party_song ON party_song.party_id = party.party_id
            INNER JOIN song ON song.song_id = party_song.song_id
            INNER JOIN url ON song.song_id = url.song_id
            WHERE party.party_id = %s
            ORDER BY song.title;
            '''


def insert_party_song():
    return f'''
            INSERT INTO party_song(party_id, song_id)
            VALUES(
                %s,
                %s
            );
            '''


def delete_party():
    return '''
            DELETE FROM party_user
            WHERE party_id = %s;

            DELETE FROM party_song
            WHERE party_id = %s;

            DELETE FROM party
            WHERE party_id = %s;
            '''


def update_description():
    return '''
            UPDATE party SET description = %s
            WHERE party_id = %s
            '''


def update_group_name():
    return '''
            UPDATE party SET name = %s
            WHERE party_id = %s
            '''


def delete_leave_group():
    return '''
            DELETE FROM party_user
            WHERE user_id = %s AND party_id = %s;
            '''


def add_user_group():
    return '''
            INSERT INTO party_user(party_id, user_id, administrator)
            VALUES(%s, %s, %s);
            '''


def get_user_id():
    return '''
            SELECT user_id FROM users
            WHERE username ILIKE %s;
            '''


def update_accept_group():
    return '''
            UPDATE party_user SET accept = true
            WHERE user_id = %s AND party_id = %s;
            '''


def delete_remove_song_group():
    return '''
            DELETE FROM party_song
            WHERE party_id = %s AND song_id = %s;
            '''


def get_party_users():
    return '''
            SELECT users.username, party_user.administrator, users.user_id FROM party_user
            INNER JOIN users ON users.user_id = party_user.user_id
            WHERE party_id = %s;
            '''


def update_user_party_admin():
    return '''
            UPDATE party_user SET administrator = true
            WHERE party_id = %s AND user_id = %s;
            '''


def get_username():
    return '''
            SELECT username FROM users
            WHERE user_id = %s;
            '''


def remove_user_song():
    return '''
            DELETE FROM user_song
            WHERE user_id = %s AND song_id = %s;
            '''


def update_edit_title():
    return '''
            UPDATE song SET title = %s
            WHERE song_id = %s;
            '''


def update_edit_artist():
    return '''
            UPDATE song SET artist = %s
            WHERE song_id = %s;
            '''


def update_edit_img():
    return '''
            UPDATE url SET img_url = %s
            WHERE song_id = %s;
            '''


def update_edit_mp3():
    return '''
            UPDATE url SET mp3_url = %s
            WHERE song_id = %s;
            '''


def update_edit_karaoke():
    return '''
            UPDATE url SET karaoke_url = %s
            WHERE song_id = %s;
            '''


def update_edit_tab():
    return '''
            UPDATE url SET tab_url = %s
            WHERE song_id = %s;
            '''

def update_edit_lyric():
    return '''
            UPDATE url SET lyric_url = %s
            WHERE song_id = %s;
            '''