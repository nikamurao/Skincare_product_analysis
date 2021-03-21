# -*- coding: utf-8 -*-
#ABLE TO HANDLE MULTIPLE URL REQUESTS
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

class Trial3Spider(scrapy.Spider):
    name = 'trial3'
    allowed_domains = ['www.sephora.com']
    start_urls= ['https://www.sephora.com/shop/cleanser?currentPage=1', 'https://www.sephora.com/shop/cleanser?currentPage=2', 'https://www.sephora.com/shop/cleanser?currentPage=3']
    
    def parse(self, response):
        '''
            Scrolls through each webpage, extracting individual product links
        '''
        
        chrome_options=Options()
        chrome_options.add_argument("--headless")
        chrome_path="./chromedriver"
        driver = webdriver.Chrome(executable_path=chrome_path)
        # #options=chrome_options
        driver.set_window_size(1500, 1400)
        driver.get(response.url)

        print("________________________________________", response.url, "_____________________________")
        #for link in start_urls:
    

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
            html=driver.page_source 

            #Parse items in the webpage
            item=Selector(text=html)
            # items=resp.xpath("//div[@class='css-12egk0t']")

            driver.save_screenshot("before scraping links.png")
            print("________________________SCRAPING LINKS NOW FOR:", driver.current_url, "__________________________")

            #Gather all links in the page
            url_main='https://www.sephora.com'
            relativelinks=item.xpath(".//a[@class='css-ix8km1']/@href").getall()
            links=[url_main+x for x in relativelinks]
            print(links)

            #Pass output for further parsing 
            for link in links:
                yield SeleniumRequest(
                    url=link,
                    wait_time=5,
                    callback=self.parse_product
                )
            
            browser= scrollDown(driver, 20)
            sleep(2)

            try:
                login=driver.find_element_by_xpath("//div[@role='dialog']/button")
                login.click()
                sleep(3)
            except:
                pass

            #Find next button
            # print("_____________________GO TO NEXT PAGE________________________")
            # #error - does this on product page
            # try:
            #     next_button=driver.find_element_by_xpath("//button[@aria-label='Next']")
            #     driver.save_screenshot('before.png')
            #     sleep(4)
            #     next_button.click()
            #     sleep(7)
            #     print("before screenshot")
            #     driver.save_screenshot('last.png')
            #     next_url=driver.current_url
            #     print(next_url)

            #     yield SeleniumRequest(
            #         url=next_url,
            #         wait_time=5,
            #         screenshot=True,
            #         callback=self.parse
            #         )
            # except ElementNotInteractableException:
            #     print("ERROR OR END")
            #     #driver.quit()

    def parse_product(self, response):
        '''
            Retrieves each product link and extracts product details from separate webpages
        '''
        
        driver=response.request.meta['driver']
        print(" <-----------------NOW EXTRACTING PRODUCT DETAILS------------------->")
        print(" _______________________FOR", driver.current_url, "__________________")
    
        driver.save_screenshot("currently extracting.png")

        #Close pop-up window/s
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

        #Expand ingredients tab 
        try:
            expand_btn=driver.find_element_by_xpath("//button[@data-at='ingredients']")
            expand_btn.click()
            sleep(2)
        except:
            pass

        driver.save_screenshot("expanded button.png")


        #Exapnd about the product
        try:
            showmore=driver.find_element_by_xpath("//button[@class='css-1n34gja eanm77i0']")
            showmore.click()
            sleep(2)
        except:
            pass

        #scrolldown
        def scrollDown(driver, scrolls):
            body = driver.find_element_by_tag_name("body")
            while scrolls >=0:
                body.send_keys(Keys.PAGE_DOWN)
                scrolls -= 1
            return driver
        browser= scrollDown(driver, 15)
        sleep(2)

        #Extract details 
        brand=response.xpath("//h1[@class='css-11zrkxf e65zztl0']/a/text()").get()
        name=response.xpath("//span[@class='css-1pgnl76 e65zztl0']/text()").get()
        weblink=driver.current_url
        category=response.xpath("//li[@aria-current='page']/a/text()").get()
        likes=response.xpath("//span[@class='css-jk94q9']/text()").get()
        sleep(2)
        img_link= response.xpath("(//img[@class='css-1rovmyu eanm77i0'])[1]/@src").get()
        price=response.xpath("//b[@class='css-0']/text()").get()
        size=response.xpath("//span[@class='css-7b7t20']/text()").get()
        full_ingredients=response.xpath("(//div[@class='css-1ue8dmw eanm77i0'])[1]/descendant::text()").getall()
        
        #removed about section as cannot extract properly
        #about=response.xpath("//div[@class='css-10bjc73 eanm77i0']/div/descendant::text()").getall()

        highlights = response.xpath("//div[@class='css-h1wajg eanm77i0']/div/img/@alt").getall() 
        
        #Can't get accurate one for rating and number of reviews 
        #stars=response.xpath("(//span[@class='css-1ac1x0l eanm77i0'])[1]/text()").get() returns error
        stars=response.xpath("(//div[@data-comp='StarRating '])[1]/@aria-label").get()
        
        #OLD num_reviews=response.xpath('normalize-space(//span[@class="css-nv7myq eanm77i0"]/text())').get()
        #old_num_reviews=response.xpath("((//span[@class='css-nv7myq eanm77i0'])[1]/text())[1]").get()
        num_reviews=response.xpath("//span[@data-at='number_of_reviews']/text()").get()

        #recommendation=response.xpath("(//span[@class='css-1ac1x0l eanm77i0'])[2]/text()") - removed as not uniform
        #include about the product, reviews 

        imglink_main='https://www.sephora.com'

        #Store in dictionary
        product_info = {
            'brand' : brand,
            'name' : name,
            #'about the product': about,
            'weblink': weblink,
            'sub_category': category,
            'main_category': 'cleansers',
            'num_likes': likes,
            'img_link': imglink_main + img_link,
            'price': price,
            'size': size,
            'ingredients': full_ingredients,
            'rating': stars,
            'num_reviews': num_reviews,
            'highlights': highlights
            }

        yield product_info

    
    def spider_closed(self, spider):
        self.driver.quit()

