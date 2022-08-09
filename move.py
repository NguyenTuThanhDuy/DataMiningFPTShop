from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image

class MoveToELement():
    def __init__(self):
        opts = Options()
        opts.set_preference("dom.webnotifications.enabled", False)
        opts.set_preference("dom.push.enabled", False)
        self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(),options=opts)
        self.actions = ActionChains(self.driver)
        self.wait = WebDriverWait(self.driver,10)
    
    def scroll_shim(self, object):
        x = object.location['x']
        y = object.location['y']
        scroll_by_coord = 'window.scrollTo(%s,%s);' % (
            x,
            y
        )
        scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
        self.driver.execute_script(scroll_by_coord)
        self.driver.execute_script(scroll_nav_out_of_way)

    def navigate_to_url(self,url):
        self.driver.get(url)
    
    def wait_login_element_load(self):
        self.wait.until(
            EC.presence_of_element_located((By.XPATH,"/html/body/footer/div[1]/div/div/div[4]/div/div[1]/ul/li[2]/a"))
        )

    def maximize_browser(self):
        self.driver.maximize_window()
        self.wait

    def find_move_to_element(self):
        self.wait_login_element_load()
        element = self.driver.find_element(By.XPATH, value="/html/body/footer/div[1]/div/div/div[4]/div/div[1]/ul/li[2]/a")
        self.scroll_shim(element)
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH,"/html/body/footer/div[1]/div/div/div[4]/div/div[1]/ul/li[2]/a"))
        )
        element.click()

    def findImage(self):
        element = self.driver.find_element(By.XPATH,value="//div[@class='text-center col-xs-12']/img")
        location = element.location
        size = element.size
        self.driver.save_screenshot('fullscreen.png')

        im = Image.open('fullscreen.png') # uses PIL library to open image in memory

        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']


        im = im.crop((left, top, right, bottom)) # defines crop points
        im.save('icon.png') # saves new cropped image
        
    def closeBrowser(self):
        self.driver.close()
if __name__ == "__main__":
    move = MoveToELement()
    try:
        move.navigate_to_url("https://fptshop.com.vn/")
        move.maximize_browser()
        move.find_move_to_element()
        move.findImage()
    except Exception as e:
        print(e)
    finally:
        move.closeBrowser()