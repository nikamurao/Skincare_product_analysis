#STARTING FROM PRODUCT PAGE - DOES ABOUT PRODUCT WELL BUT CANT DETECT REVIEWS CURRENTLY
#PROBLEM IS THAT IT CAN"T SEE THE REWVIEWS PAGE DUE TO LAZY LOAD!!!! 
# 
# 
# - inserted additional sleep so reviews now detected; can be fetched as a group but cant be looped on - see airbnb data - think its because of Selector

import scrapy
import selenium
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

class Lean2Spider(scrapy.Spider):
    name = 'lean2'
    allowed_domains = ['www.sephora.com']
    url=r'https://www.sephora.com/product/fenty-skin-fenty-skin-start-r-set-P467251?icid2=products%20grid:p467251'
    start_urls = [url]

    def parse(self, response):

        chrome_path="./chromedriver"
        driver = webdriver.Chrome(executable_path=chrome_path)
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


        sleep(10)

        #Creating a scroll-down function to see next items in the page
        def scrollDown(driver, scrolls):
            body = driver.find_element_by_tag_name("body")
            while scrolls >=0:
                body.send_keys(Keys.PAGE_DOWN)
                scrolls -= 1
            return driver
        browser= scrollDown(driver, 10)

        resp = scrapy.Selector(text=driver.page_source) # Create HTML doc from HTML text

        brand=resp.xpath("//h1[@class='css-11zrkxf e65zztl0']/a/text()").get()
        name=resp.xpath("//span[@class='css-1pgnl76 e65zztl0']/text()").get()
        weblink=driver.current_url
        category=resp.xpath("//li[@aria-current='page']/a/text()").get()
        likes=resp.xpath("//span[@class='css-jk94q9']/text()").get()
        sleep(2)
        img_link= resp.xpath("(//img[@class='css-1rovmyu eanm77i0'])[1]/@src").get()
        price=resp.xpath("//b[@class='css-0']/text()").get()
        size=resp.xpath("//span[@class='css-7b7t20']/text()").get()
        full_ingredients=resp.xpath("(//div[@class='css-1ue8dmw eanm77i0'])[1]/descendant::text()").getall()
        highlights = resp.xpath("//div[@class='css-h1wajg eanm77i0']/div/img/@alt").getall() 
        stars=resp.xpath("(//div[@data-comp='StarRating '])[1]/@aria-label").get()
        num_reviews=resp.xpath("//span[@data-at='number_of_reviews']/text()").get()
        about=resp.xpath("(//h2[@data-at='about_the_product_title']/following::div)[1]/div[position()=2]/div/div//descendant-or-self::*/text()").getall()
        #about = ''.join( _ for _ in about_).strip()

        browser= scrollDown(driver, 15)
        sleep(10)
        #See full review 
        #readmore=driver.find_element_by_xpath("//button[contains(text(), 'Read more')]")
        #readmore.click()

        #findreview = driver.find_element_by_xpath("//div[@data-comp='Review StyledComponent BaseComponent ']")
        #driver.execute_script("arguments[0].scrollIntoView(true)", findreview)


        #Scrape reviews 
        # expand all the read-mores 
        # main review area = '//div/[@class="css-ro1t97 e1byeus60"]'    
        #     xpaths
        #    
        #self.html=driver.page_source 
        #reviews= response.xpath("//div[@data-comp='Review StyledComponent BaseComponent ']/div")
        #count=0
        #print('--------------------------------------------->got ', reviews, type(reviews))
        #reviewtext=resclewp.xpath("//div[@data-comp='Review StyledComponent BaseComponent ']").getall()
        print('----------------------REVIEW TEXT---------------------')
        
        
        #Copy-pasted from Airbnb for infinite scroll-didnt really do anything
        last_height = driver.execute_script("return document.body.scrollHeight")
        SCROLL_PAUSE_TIME = 7
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(SCROLL_PAUSE_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            sleep(1.2)
        
        #Some worked but extremely incosistent! - cant findn it out yet
        reviewtext=resp.xpath("//p[contains(text(), 'Viewing')]/following-sibling::div/div//div[@class='css-x1yqyp eanm77i0']/text()").getall()
        reviewtext1=resp.xpath("//div[@data-comp='Review StyledComponent BaseComponent ']/div//div[position()=last()]/div/text()").getall()  #WORKING!!!!
        #reviewtext1=response.xpath("//div[@data-comp='Review StyledComponent BaseComponent ']/div")
        reviewtext_old=response.xpath("//div[@data-comp='Review StyledComponent BaseComponent ']/div").getall() #looks like response doesnt work here
        reviewtext_old1=resp.xpath("//div[@data-comp='Review StyledComponent BaseComponent ']/div")
        #reviewtext1= Selector()
        review_select=resp.xpath("//p[contains(text(), 'Viewing')]/following-sibling::div/div")
        review_select2=response.xpath("//p[contains(text(), 'Viewing')]/following-sibling::div/div")
        reviewtext3=resp.xpath("//div[@class='css-x1yqyp eanm77i0']/text()").getall()

        #Nothing is working now 
        yield{
            '1': reviewtext,
            '2': reviewtext1,
            '3': reviewtext3,
            'old': reviewtext_old,
            'old1': reviewtext_old1
        }

        #p=resp.xpath("//div/descendant-or-self::*/text()").getall() - WOPRK
        for item in reviewtext_old1:
            print({
                'text': item.xpath("//div[@class='css-x1yqyp eanm77i0']/text()").extract(),
                'attributes': item.xpath("//a/div/span[position()=2]/text()").extract(),
                'title': item.xpath("//div/child:::h3/text()").extract(),
                'rating': item.xpath("//div[@data-comp='StarRating ']/@aria-label").extract()}
            )

        #trying to see if loop will work - WORKS 
        #highlights=resp.xpath("//div[@class='css-aiipho eanm77i0']")
        #for h in highlights:
        #    print(h.xpath(".//img/@alt").get())
       


        
        # for review in reviewtext:
        #     yield {
        #         'reviewer_attributes': review.xpath(".//div//div[position()=last()]/div/text()").get(),
        #         'review_rating': review.xpath(".//div//div[@class='css-4qxrld']/@aria-label").get(),
        #         }

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
        #print('_______________________________PRODUCT ATTRIBUTES FOUND:___________________________ ')
        #yield product_info
        #nxt_button_review=driver.find_element_by_xpath("//ul[@class='css-5x9b9r eanm77i0']/li[position()=last()]")    
        #while True:
        #nxt_button_review:
        #extract reviews
        

                #Scrape reviews 
        # expand all the read-mores 
        # main review area = '//div/[@class="css-ro1t97 e1byeus60"]'    
        #     xpaths
        #     reviewer_attributes=.xpath("//span[@class='css-2h4ti5 eanm77i0']/text()").get()
        #     review_rating=.xpath("//span[@class='css-1vmt2jw eanm77i0']/div/@aria-label")
        #     nxt_button_review=.find_element_by_xpath("//button[@aria-label='Next']")
        # #check 
        #     while nxt_button_review:
        #         extract          
        #         nxt_button_review.click()

                
            #nxt_button_review.click()
        driver.quit()