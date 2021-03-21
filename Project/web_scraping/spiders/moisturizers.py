#Revising trial2 to HANDLE MULTIPLE REQUESTS THROUGH START_URLS- SHOULD BE THE MAIN ON
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

class MoisturizersSpider(scrapy.Spider):
    name = 'moisturizers'
    allowed_domains = ['www.sephora.com']
    # max=8
    # start_urls=[]
    # for page in range(1, max+1):
    #     url=r'https://www.sephora.com/shop/cleanser?currentPage={page}'
    #     start_urls.append(url)
    start_urls = [
        'https://www.sephora.com/shop/moisturizing-cream-oils-mists?currentPage=1',
        'https://www.sephora.com/shop/moisturizing-cream-oils-mists?currentPage=2',
        'https://www.sephora.com/shop/moisturizing-cream-oils-mists?currentPage=3',
        'https://www.sephora.com/shop/moisturizing-cream-oils-mists?currentPage=4',
        'https://www.sephora.com/shop/moisturizing-cream-oils-mists?currentPage=5',
        'https://www.sephora.com/shop/moisturizing-cream-oils-mists?currentPage=6',
        'https://www.sephora.com/shop/moisturizing-cream-oils-mists?currentPage=7',
        'https://www.sephora.com/shop/moisturizing-cream-oils-mists?currentPage=8',
        'https://www.sephora.com/shop/moisturizing-cream-oils-mists?currentPage=9',
        'https://www.sephora.com/shop/moisturizing-cream-oils-mists?currentPage=10',
        'https://www.sephora.com/shop/moisturizing-cream-oils-mists?currentPage=11',
        'https://www.sephora.com/shop/moisturizing-cream-oils-mists?currentPage=12',
        'https://www.sephora.com/shop/moisturizing-cream-oils-mists?currentPage=13'
        ]
    

    def parse(self, response):
        '''
            Scrolls through each webpage, extracting individual product links
        '''
        chrome_options=Options()
        chrome_options.add_argument("--headless")
        chrome_path="./chromedriver"
        driver = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)
        driver.set_window_size(1500, 1400)
        driver.get(response.url)

        print("_________________________REQUEST RECEIVED, NOW ON: ", response.url, "_____________________________")
        
        #Adding time lag before next action
        sleep(7)

        #Close pop-up window(s)
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
    
        browser= scrollDown(driver, 13)

        #Store page source to parse it later
        html=driver.page_source 
        #Parse items in the webpage
        item=Selector(text=html)

        driver.save_screenshot("before scraping links.png")
        print("________________________SCRAPING LINKS NOW FOR:", driver.current_url, "__________________________")

        #Gather all links in the page
        url_main='https://www.sephora.com'
        relativelinks=item.xpath(".//a[@class='css-ix8km1']/@href").getall()
        links=[url_main+x for x in relativelinks]
        print("_____________________________LINKS FOR:", driver.current_url, " BELOW____________________________")
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

    def parse_product(self, response):
        '''
            Retrieves each product link and extracts product details from separate webpages
        '''
        
        driver=response.request.meta['driver']
        print(" <-----------------NOW EXTRACTING PRODUCT DETAILS------------------->")
        print(" _______________________product page is", driver.current_url, "__________________")
    
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
        about=response.xpath("(//h2[@data-at='about_the_product_title']/following::div)[1]/div[position()=2]/div/div//descendant-or-self::*/text()").getall()
        highlights = response.xpath("//div[@class='css-h1wajg eanm77i0']/div/img/@alt").getall() 
        stars=response.xpath("(//div[@data-comp='StarRating '])[1]/@aria-label").get()
        num_reviews=response.xpath("//span[@data-at='number_of_reviews']/text()").get()

        imglink_main='https://www.sephora.com'

        #Store in dictionary
        product_info = {
            'brand' : brand,
            'name' : name,
            'about the product': about,
            'weblink': weblink,
            'sub_category': category,
            'main_category': 'moisturizers',
            'num_likes': likes,
            'img_link': imglink_main + img_link,
            'price': price,
            'size': size,
            'ingredients': full_ingredients,
            'rating': stars,
            'num_reviews': num_reviews,
            'highlights': highlights
            }
        print('_______________________________PRODUCT ATTRIBUTES FOUND:___________________________ ')
        yield product_info
    
    def spider_closed(self, spider):
        self.driver.quit()

