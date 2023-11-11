import asyncio
from sql import *
from resources import download_song, get_google_img, get_lyrics, download_karaoke
from ultimate_guitar_scraper import UltimateGuitarScraper
from tab_scraper import TabScraper


# async def obtain_img(title, artist, song_id, GOOGLE_API_KEY, GOOGLE_CX, cur, conn):
#     print('img')
#     if artist:
#         img_url = get_google_img(f'{title} {artist}', GOOGLE_API_KEY, GOOGLE_CX)
#     else:
#         img_url = get_google_img(title, GOOGLE_API_KEY, GOOGLE_CX)
    
#     if img_url:
#         img_url_sql = update_value(song_id, 'url', 'img_url', img_url)
#         cur.execute(img_url_sql)
#         conn.commit()
#     print('img finished')


# async def obtain_lyrics(song_id, title, artist, GENIUS_ACCESS_TOKEN, cur, conn):
#     print('lyrics')
#     try:
#         if artist:
#             lyrics = get_lyrics(GENIUS_ACCESS_TOKEN, title, artist=artist)
#         else:
#             lyrics = get_lyrics(GENIUS_ACCESS_TOKEN, title)
#     except:
#         lyrics = None

#     if lyrics:
#         with open(f'./static/lyric/{title}.txt', 'w', encoding='utf-8') as file:
#             file.write(lyrics)
        
#         lyric_attempt_sql = update_value(song_id, 'attempt', 'lyric_check', 'true')
#         cur.execute(lyric_attempt_sql)
#         conn.commit()
        
#         lyric_url_sql = update_value(song_id, 'url', 'lyric_url', f'./static/lyric/{title}.txt')
#         cur.execute(lyric_url_sql)
#         conn.commit()
    
#     else:
#         lyric_attempt_sql = update_value(song_id, 'attempt', 'lyric_check', 'true')
#         cur.execute(lyric_attempt_sql)
#         conn.commit()
#     print('lyrics finished')



async def download_mp3_async(title, artist, song_id, cur, conn):
    print('mp3')
    path = './static/mp3/'
    if download_song(title, artist, path):
        update_sql = update_data(song_id, 'mp3_check', 'mp3_url', f'.{path}{title}.mp3')
        cur.execute(update_sql)
        conn.commit()
    else:
        update_sql = update_fail_data(song_id, 'mp3_check')
        cur.execute(update_sql)
        conn.commit()
    print('mp3 finished')


async def download_karaoke_async(title, song_id, cur, conn):
    print('karaoke')
    path = './static/karaoke/'
    download_track = download_karaoke(title, path)
    if download_track:
        update_sql = update_data(song_id, 'karaoke_check', 'karaoke_url', f'.{path}{title}_karaoke.mp3')
        cur.execute(update_sql)
        conn.commit()
    else:
        update_sql = update_fail_data(song_id, 'karaoke_check')
        cur.execute(update_sql)
        conn.commit()
    print('karaoke finished')


async def download_tab_async(title, song_id, cur, conn):
    print('tab')
    path = './static/tab/'
    scraper = TabScraper(title)
    href = await scraper.run_scrape()
    if href:
        await scraper.run_downloader(href)

        update_sql = update_data(song_id, 'tab_check', 'tab_url', f'.{path}{title}.pdf')
        cur.execute(update_sql)
        conn.commit()
    else:
        update_sql = update_fail_data(song_id, 'tab_check')
        cur.execute(update_sql)
        conn.commit()
    print('tab finished')

async def gather_main(song_id, input_mp3, input_karaoke, input_tab, title, artist, 
                    #   GOOGLE_API_KEY, GOOGLE_CX, GENIUS_ACCESS_TOKEN, 
                      cur, conn):
    
    semaphore = asyncio.Semaphore(2)

    async def run_task(task):
        async with semaphore:
            await task

    await asyncio.gather(
                run_task(download_mp3_async(title, artist, song_id, cur, conn) if input_mp3 == 'yes' else asyncio.sleep(0)),
                run_task(download_karaoke_async(title, song_id, cur, conn) if input_karaoke == 'yes' else asyncio.sleep(0)),
                run_task(download_tab_async(title, song_id, cur, conn) if input_tab == 'yes' else asyncio.sleep(0)),
            )  
    

# run_task(obtain_img(title, artist, song_id, GOOGLE_API_KEY, GOOGLE_CX, cur, conn)),
# run_task(obtain_lyrics(song_id, title, artist, GENIUS_ACCESS_TOKEN, cur, conn))