library_table = ['song_id', 'title', 'artist', 'img_url']


def library_songs():
    return '''SELECT 
                    song.song_id, 
                    title, artist, 
                    url.img_url 
                FROM song
                INNER JOIN url ON song.song_id = url.song_id;'''


song_page_table = ['song_id', 'title', 'artist', 'release_year', 'album',
                   'lyric_check', 'tab_check', 'mp3_check', 'karaoke_check',
                   'lyric_url', 'tab_url', 'mp3_url', 'karaoke_url', 'img_url']


def song_page_info(song_id):
    return f'''SELECT 
                    song.song_id, 
                    title, 
                    artist, 
                    release_year, 
                    album,
                    attempt.lyric_check, 
                    attempt.tab_check, 
                    attempt.mp3_check, 
                    attempt.karaoke_check,
                    url.lyric_url, 
                    url.tab_url, 
                    url.mp3_url, 
                    url.karaoke_url, 
                    url.img_url
                FROM song
                INNER JOIN attempt ON song.song_id = attempt.song_id
                INNER JOIN url ON song.song_id = url.song_id
                WHERE song.song_id = {song_id};'''


get_mp3_table = ['song_id', 'title', 'artist']


def get_mp3_query(song_id):
    return f'''
            SELECT song_id, title, artist FROM song
            WHERE song_id = {song_id};'''


def update_data(song_id, attempt, url, path):
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
    return f'''
            SELECT song.song_id FROM searches
            INNER JOIN song_search ON searches.search_id = song_search.search_id
            INNER JOIN song ON song_search.song_id = song.song_id
            WHERE search_term ILIKE '{search}'
            GROUP BY song.song_id
            '''

