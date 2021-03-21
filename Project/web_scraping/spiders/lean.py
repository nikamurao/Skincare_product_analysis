#STARTING FROM PRODUCT PAGE - DOES ABOUT PRODUCT WELL BUT CANT DETECT REVIEWS CURRENTLY


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
from webdriver_manager.chrome import ChromeDriverManager

class LeanSpider(scrapy.Spider):
    name = 'lean'
    allowed_domains = ['www.sephora.com']
    url=r'https://www.sephora.com/product/fenty-skin-fenty-skin-start-r-set-P467251?icid2=products%20grid:p467251'
    start_urls = [url]

    def parse(self, response):

        chrome_path="./chromedriver"
        driver = webdriver.Chrome(
            executable_path=chrome_path)
        driver.get(response.url)
        # #options=chrome_options

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
        highlights = response.xpath("//div[@class='css-h1wajg eanm77i0']/div/img/@alt").getall() 
        stars=response.xpath("(//div[@data-comp='StarRating '])[1]/@aria-label").get()
        num_reviews=response.xpath("//span[@data-at='number_of_reviews']/text()").get()

        self.html=driver.page_source
        selector = scrapy.Selector(text=self.html, type="html") # Create HTML doc from HTML text
        about_=selector.xpath("(//h2[@data-at='about_the_product_title']/following::div)[1]/div[position()=2]/div/div//descendant-or-self::*/text()").getall()
        about = ''.join( _ for _ in about_).strip()
        print(about)


        browser= scrollDown(driver, 15)
        sleep(10)
        #See full review 
        #readmore=driver.find_element_by_xpath("//button[contains(text(), 'Read more')]")
        #readmore.click()

        findreview = driver.find_element_by_xpath("//div[@data-comp='Review StyledComponent BaseComponent ']")
        driver.execute_script("arguments[0].scrollIntoView(true)", findreview)

        #Scrape reviews 
        # expand all the read-mores 
        # main review area = '//div/[@class="css-ro1t97 e1byeus60"]'    
        #     xpaths
        #    
        #self.html=driver.page_source 
        #reviews= response.xpath("//div[@data-comp='Review StyledComponent BaseComponent ']/div")
        #count=0
        #print('--------------------------------------------->got ', reviews, type(reviews))
        reviewtext=response.xpath("//div[@data-comp='Review StyledComponent BaseComponent ']/div//div[position()=last()]/div/text()").getall()
        print('----------------------REVIEW TEXT---------------------')
        yield {'reviewtext': reviewtext}

        #reviewer_attributes= response.xpath("//div[@data-comp='Review StyledComponent BaseComponent ']/div//div[position()=last()]/div/text()").extract()
        #review_rating= response.xpath("//div[@data-comp='Review StyledComponent BaseComponent ']/div//div[@class='css-4qxrld']/@aria-label").extract()
        
        #print("---------------------------------------REVIEWS --------------------------------------")
        #for item in zip(reviewer_attributes, review_rating):
        # #    scraped_rating={
        #         'reviewer': item[0],
        #         'rating given': item[1]
        #     }
        

        imglink_main='https://www.sephora.com'

        #Store in dictionary
        product_info = {
            'brand' : brand,
            'name' : name,
            'weblink': weblink,
            'sub_category': category,
            'main_category': 'cleansers',
            'num_likes': likes,
            'price': price,
            'size': size,
            'ingredients': full_ingredients,
            'rating': stars,
            'num_reviews': num_reviews,
            'highlights': highlights,
            'review': reviewtext,
            'about': about
            }
        print('_______________________________PRODUCT ATTRIBUTES FOUND:___________________________ ')
        yield product_info
        #nxt_button_review=driver.find_element_by_xpath("//ul[@class='css-5x9b9r eanm77i0']/li[position()=last()]")    
        #while True:
        #nxt_button_review:
        #extract reviews
        

                
            #nxt_button_review.click()
        driver.quit()