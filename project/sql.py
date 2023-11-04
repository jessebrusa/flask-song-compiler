library_table = ['song_id', 'title', 'artist', 'img_url']


def library_songs():
    return '''SELECT 
                    song.song_id, 
                    title, artist, 
                    url.img_url 
                FROM song
                INNER JOIN url ON song.song_id = url.song_id'''


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
                WHERE song.song_id = {song_id}'''