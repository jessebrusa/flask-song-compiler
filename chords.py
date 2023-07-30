from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

class Chords():

    def __init__(self):
        service = Service('chromedriver')
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.page_load_strategy = 'eager'
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get('https://www.ultimate-guitar.com/')
        time.sleep(1)

    def login_account(self, email, password):
        login_button = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div[1]/article/header/button[2]/span')
        login_button.click()
        time.sleep(3)

        email_input_entry = self.driver.find_element(By.XPATH, '/html/body/div[3]/article/section/div[2]/div/form/div/div[1]/input')
        email_input_entry.send_keys(email)
        time.sleep(1)

        password_input_entry = self.driver.find_element(By.XPATH, '/html/body/div[3]/article/section/div[2]/div/form/div/div[2]/div/input')
        password_input_entry.send_keys(password)
        time.sleep(1)

        submit_login_button = self.driver.find_element(By.XPATH, '/html/body/div[3]/article/section/div[2]/div/form/div/div[3]/button/span')
        submit_login_button.click()
        time.sleep(3)

    def search_song(self, song):
        input_song_entry = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/p[2]/form/div/input')
        input_song_entry.send_keys(song)
        input_song_entry.send_keys(Keys.ENTER)
        time.sleep(4)

        try:
            highest_ratings = self.driver.find_elements(By.CSS_SELECTOR, 'div[class="djFV9"]')
            rating_counter = 0
            highest_rating = 0
            rating_position = None
            for rating in highest_ratings:
                num_rating = int(rating.text.replace(',', '', 1))
                if num_rating > highest_rating:
                    rating_position = rating_counter
                    highest_rating = num_rating
                rating_counter += 1

            parent_element = highest_ratings[rating_position].find_element(By.XPATH, '../../..')
            href_value = parent_element.find_element(By.TAG_NAME, 'a').get_attribute('href')
            
            self.driver.get(href_value)
            time.sleep(4)
        except:
            self.driver.quit()


    def save_pdf(self):
        click_pdf_download_page = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div[2]/article[1]/section[1]/section/section/div/div/div[3]/div/div/button/span')
        click_pdf_download_page.click()
        time.sleep(5)

        self.driver.quit()


# GUITAR_EMAIL = 'jessebrusa@gmail.com'
# GUITAR_PASSWORD = '1JesusKing7'
# chords = Chords()
# chords.login_account(GUITAR_EMAIL, GUITAR_PASSWORD)
# chords.search_song('hotel key')