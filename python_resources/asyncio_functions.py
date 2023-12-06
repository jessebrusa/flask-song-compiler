import asyncio
from python_resources.sql import *
from python_resources.resources import download_song, download_karaoke
from python_resources.tab_scraper import TabScraper



async def download_mp3_async(title, artist, song_id, cur, conn):
    path = './static/mp3/'
    if download_song(title, artist, path):
        update_sql = update_data(song_id, 'mp3_check', 'mp3_url', f'.{path}{title}.mp3')
        cur.execute(update_sql)
        conn.commit()
    else:
        update_sql = update_fail_data(song_id, 'mp3_check')
        cur.execute(update_sql)
        conn.commit()


async def download_karaoke_async(title, song_id, cur, conn):
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


async def download_tab_async(title, song_id, cur, conn):
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