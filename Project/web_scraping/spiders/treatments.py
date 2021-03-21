# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import scrapy
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options 
from scrapy.selector import Selector
from selenium.webdriver.support.ui import Select
from scrapy_selenium import SeleniumRequest
from urllib.parse import urljoin
from selenium.common.exceptions import ElementNotInteractableException

class TreatmentsSpider(scrapy.Spider):
    name = 'treatments'
    #allowed_domains = ['www.sephora.com']
    #start_urls = ['https://www.sephora.com/shop/facial-treatments?currentPage=1']

    def start_requests(self):
        yield SeleniumRequest(
            url='https://www.sephora.com/shop/facial-treatments?currentPage=1',
            wait_time=3,
            screenshot=True,
            callback=self.parse
            )

    def parse(self, response):
        
        driver=response.meta['driver']

        # chrome_options=Options()
        # chrome_options.add_argument("--headless")
        # chrome_path="./chromedriver"
        # driver = webdriver.Chrome(executable_path=chrome_path)
        # #options=chrome_options
        driver.set_window_size(1500, 1400)
        
        #Open website
        #url="https://www.sephora.com/shop/cleanser"
        #driver.get(url)

        #Adding time lag before next action
        sleep(7)

        #Close pop-up window
        try:
            close=driver.find_element_by_xpath("//button[@aria-label='Continue shopping']") 
            close.click()
            sleep(3)
        except:
            pass

        try:
            login=driver.find_element_by_xpath("//div[@role='dialog']/button")
            login.click()
            sleep(3)
        except:
            pass

        #Creating a scroll-down function to see next items in the page
        def scrollDown(driver, scrolls):
            body = driver.find_element_by_tag_name("body")
            while scrolls >=0:
                body.send_keys(Keys.PAGE_DOWN)
                scrolls -= 1
            return driver
        browser= scrollDown(driver, 10)

        #Store page source to parse it later
        self.html=driver.page_source 

        #Parse items in the webpage
        resp=Selector(text=self.html)
        items=resp.xpath("//div[@class='css-12egk0t']")

        print('BEFORE SCRAPING!!!!!')

        for item in items:
            yield{
                'relative link': item.xpath(".//a[@class='css-ix8km1']/@href").get(),
                'brand': item.xpath(".//span[@class='css-182j26q']/text()").get(),
                'name': item.xpath(".//span[@class='css-pelz90']/text()").get(),
                'price range': item.xpath(".//span[@data-at='sku_item_price_list']/text()").get(),
                'review count': item.xpath(".//span[@data-comp='ReviewCount ']/text()").get(),
                'rating': item.xpath(".//div[@data-comp='StarRating ']/@aria-label").get()
            }

        browser= scrollDown(driver, 20)
        sleep(2)

        try:
            login=driver.find_element_by_xpath("//div[@role='dialog']/button")
            login.click()
            sleep(3)
        except:
            pass

        #Find next button
        try:
            next_button=driver.find_element_by_xpath("//button[@aria-label='Next']")
            driver.save_screenshot('before_nexttreatment.png')
            sleep(4)
            next_button.click()
            sleep(7)
            print("before screenshot")
            driver.save_screenshot('last_treatments.png')
            next_url=driver.current_url
            print(next_url)

            yield SeleniumRequest(
                url=next_url,
                wait_time=5,
                screenshot=True,
                callback=self.parse
                )
        except ElementNotInteractableException:
            print("ERROR OR END")
            #driver.close()
