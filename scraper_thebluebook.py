from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains

import csv
import time
import threading

def open_url(url, num_retries=5):
    try:
        driver = webdriver.Chrome()
        driver.get(url)
    except:
        if num_retries > 0:
            driver.quit()
            open_url(url, num_retries-1)
    driver.maximize_window()
    return driver

class scraper_thebluebook():
    def __init__(self, company_manufacturer, city_zipcode):
        self.url = 'http://www.thebluebook.com/'
        self.company_manufacturer = company_manufacturer
        self.city_zipcode = city_zipcode
        self.total_data = []
        self.page_number = 0
        self.start_url = ''
        self.next_url = []

    def start_scraping(self):
        self.driver = open_url(self.url)

        input1 = WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#search.default-input.companySrch.ui-autocomplete-input")))

        input2 = WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span#select2-region-select-container.select2-selection__rendered")))

        search_btn = WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.searchBtn")))

        input1.send_keys(self.company_manufacturer)

        actionChains = ActionChains(self.driver)

        actionChains \
            .click(input2) \
            .key_down(Keys.CONTROL) \
            .send_keys('a') \
            .key_up(Keys.CONTROL) \
            .send_keys(Keys.DELETE)\
            .click(input2)\
            .perform()

        input2 = WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input.select2-search__field")))

        input2.send_keys(self.city_zipcode)
        input2.send_keys(Keys.ENTER)

        search_btn.click()
        time.sleep(3)

        self.firstpage_scraping()
        self.total_threading()
        self.save_csv()

    def total_threading(self):
        self.threads = []
        self.max_threads = 5

        while self.threads or self.next_url:
            for thread in self.threads:
                if not thread.is_alive():
                    self.threads.remove(thread)

            while len(self.threads) < self.max_threads and self.next_url:
                thread = threading.Thread(target=self.thread_processing)
                thread.setDaemon(True)
                thread.start()
                self.threads.append(thread)

    def thread_processing(self):
        url = self.next_url.pop()
        print(url)

        driver = open_url(url)
        trs = WebDriverWait(driver, 50).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.single_result_wrapper")))
        for tr in trs:
            text = tr.text
            text = text.split('\n')
            if 'Connections [1]' not in text:
                company_name = text[0]
                address = text[1]
                phone_number = text[2]
            else:
                company_name = text[1]
                address = text[2]
                phone_number = text[3]

            self.total_data.append({
                'company name': company_name,
                'address': address,
                'phone number': phone_number,
            })
        driver.quit()

    def firstpage_scraping(self):
        # trs = self.driver.find_elements_by_css_selector('div.single_result_wrapper')
        trs = WebDriverWait(self.driver, 50).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.single_result_wrapper")))


        page_number = self.driver.find_elements_by_css_selector('a.dropdown-toggle.action-drop')[-1].text
        page_number = page_number.split(' of ')[1]
        self.page_number = int(page_number)
        #print(page_number)
        self.start_url = self.driver.current_url

        for i in range(2, self.page_number+1):
            self.next_url.append(self.start_url+'&page={}'.format(i))
        self.next_url.reverse()

        print(len(trs))

        for tr in trs:
            text = tr.text
            text = text.split('\n')
            if 'Connections [1]' not in text:
                company_name = text[0]
                address = text[1]
                phone_number = text[2]
            else:
                company_name = text[1]
                address = text[2]
                phone_number = text[3]

            self.total_data.append({
                'company name': company_name,
                'address': address,
                'phone number': phone_number,
            })
        self.driver.quit()


    def save_csv(self):

        filename = self.company_manufacturer + ' ' + self.city_zipcode + '.csv'
        self.output_file = open(filename, 'w', encoding='utf-8', newline='')
        self.writer = csv.writer(self.output_file)
        headers = ['Company Name', 'Address', 'Phone Number']
        self.writer.writerow(headers)

        for i, elm in enumerate(self.total_data):
            row = [
                elm['company name'],
                elm['address'],
                elm['phone number']
            ]
            self.writer.writerow(row)

        self.output_file.close()


if __name__ == '__main__':
    app = scraper_thebluebook('Electrical', 'Brooklyn NY')
    app.start_scraping()




