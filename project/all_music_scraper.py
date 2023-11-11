import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import textdistance


class AllMusicScraper:
    def __init__(self, title, **kwargs):
        self.artist = kwargs.get('artist')
        self.title = title
        if self.artist:
            self.search_url = f"https://www.allmusic.com/search/all/{self.title} {self.artist}"
        else:
            self.search_url = f"https://www.allmusic.com/search/all/{self.title}"
        

    async def scrape_title_artist(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(self.search_url, wait_until='domcontentloaded')
            
            await page.wait_for_selector('div.song')

            html = await page.content()

            soup = BeautifulSoup(html, 'html.parser')

            await browser.close()

            title_element = soup.find('div', class_='title').find('a')
            correct_title = title_element.text.strip('"')


            if self.artist:
                performers_element = soup.find('div', class_='performers').find('a')
                correct_performers = performers_element.text
                if 'by ' in correct_performers:
                        correct_performers = correct_performers.strip()[3:]

                artist_element = soup.find('div', class_='artist').find('a')
                correct_artist = artist_element.text
                if 'by ' in correct_artist:
                        correct_artist = correct_artist.strip()[3:]
            
                performer_similiarity = textdistance.levenshtein.normalized_similarity(self.artist, correct_performers)
                artist_similiarity = textdistance.levenshtein.normalized_similarity(self.artist, correct_artist)
            
                if performer_similiarity > artist_similiarity:
                    return [correct_title, correct_performers]
                else:
                    return [correct_title, correct_artist]
            else:
                performers_elements = soup.find_all('div', class_='performers')
                if performers_elements:
                    correct_performers = performers_elements[0].text
                    if 'by ' in correct_performers:
                        correct_performers = correct_performers.strip()[3:]

                artist_elements = soup.find_all('div', class_='artist')
                if artist_elements:
                    correct_artist = artist_elements[0].text
                    if 'by ' in correct_artist:
                        correct_artist = correct_artist.strip()[3:]

                if performers_elements and artist_elements:
                    if performers_elements[0].find('a') == artist_elements[0].find('a'):
                        return [correct_title, correct_performers]
                    else:
                        return [correct_title, correct_artist]
                elif performers_elements:
                    return [correct_title, correct_performers]
                elif artist_elements:
                    return [correct_title, correct_artist]
                else:
                    return None


    def run_scrape(self):
        return asyncio.run(self.scrape_title_artist())