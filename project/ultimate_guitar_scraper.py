import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import os



class UltimateGuitarScraper:
    def __init__(self, title):
        self.title = title
        self.url = f'https://www.ultimate-guitar.com/search.php?search_type=title&value={title}'


    async def scrape_link(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            try:
                await page.goto(self.url, wait_until='domcontentloaded')
                
                await page.wait_for_selector('div.djFV9', timeout=5)

                html = await page.content()
            except asyncio.TimeoutError:
                return None

            with open('scrape-for-link.html', 'w', encoding='utf-8') as file:
                file.write(html)

            soup = BeautifulSoup(html, 'html.parser')

            highest_ratings = soup.find_all('div', class_='djFV9')

            rating_counter = 0
            highest_rating = 0
            rating_position = None
            for rating in highest_ratings:
                num_rating = int(rating.text.replace(',', '', 1))
                if num_rating > highest_rating:
                    rating_position = rating_counter
                    highest_rating = num_rating
                rating_counter += 1

            specific_div = highest_ratings[rating_position]
            for i in range(3):
                specific_div = specific_div.find_parent('div')

            a_element = specific_div.find('a')
            if a_element:
                href_value = a_element.get('href')

            await browser.close()
            return href_value


    async def download_pdf(self, href):
        async with async_playwright() as p:
            current_directory = os.getcwd()
            download_path = os.path.join(current_directory, 'static/tab/')

            browser = await p.chromium.launch(downloads_path=download_path)
            page = await browser.new_page()
            custom_headers = {
                'Accept': 'application/pdf',  
            }
            await page.set_extra_http_headers(custom_headers)

            await page.goto(href, wait_until='domcontentloaded')

            await asyncio.sleep(1)

            await page.pdf(path=f'static/tab/{self.title}.pdf', scale=0.8)
            print('its downloaded')

            await browser.close()


    def run_scrape(self):
        return asyncio.run(self.scrape_link())
    

    def run_downloader(self, href):
        return asyncio.run(self.download_pdf(href))