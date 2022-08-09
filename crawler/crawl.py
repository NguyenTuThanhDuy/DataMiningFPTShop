from email.headerregistry import Group
from h11 import Data
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from selenium.common.exceptions import NoSuchElementException
import os , re
from db import Database
class GroupKey(dict):
    def __init__(self):
        self = dict()
    def add(self,key,value):
        self[key] = value
class FPTBrowser():
    def __init__(self):
        opts = Options()
        opts.set_preference("dom.webnotifications.enabled", False)
        opts.set_preference("dom.push.enabled", False)
        self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(),options=opts)
        self.actions = ActionChains(self.driver)
        self.wait = WebDriverWait(self.driver,10)
    
    def check_exists_by_xpath(self,xpath):
        try:
            self.driver.find_element(By.XPATH,value=xpath)
        except NoSuchElementException:
            return False
        return True


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
    
    def get_links_from_navbar(self):
        res = []
        products = ('dien-thoai','may-tinh-bang','may-tinh-xach-tay')
        links = self.driver.find_elements(By.XPATH,value="/html/body/header/nav/div/ul/li/a")
        for link in links:
            res.append(link.get_attribute('href'))
        res = [l for l in res if l.endswith(products)]
        return res
    
    def get_phone_detail_links(self,links):
        res = []
        phone_link = [l for l in links if l.endswith('dien-thoai')]
        if len(phone_link) >= 1:
            link = phone_link[0]
        else:
            return False
        self.navigate_to_url(link)
        self.wait.until(
            EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/main/div/div[3]/div[2]/div[2]/div/div[3]/a"))
        )
        while True:
            if self.check_exists_by_xpath('/html/body/div[2]/main/div/div[3]/div[2]/div[2]/div/div[3]/a'):
                button = self.driver.find_element(By.XPATH,value='/html/body/div[2]/main/div/div[3]/div[2]/div[2]/div/div[3]/a')
                self.scroll_shim(button)
                self.wait.until(
                    EC.visibility_of_element_located((By.XPATH,'/html/body/div[2]/main/div/div[3]/div[2]/div[2]/div/div[3]/a'))
                )
                button.click()
            else:
                break
        elements = self.driver.find_elements(By.CLASS_NAME,value="cdt-product__img")
        filename = 'mobile_link.txt'
        if os.path.exists(filename):
            os.remove(filename)
        with open(filename,'w') as f:
            for element in elements:
                mobile_line = element.find_element(By.TAG_NAME,value='a').get_attribute('href')
                f.write(mobile_line+'\n')
        f.close()

    def get_detail_each_prod(self,filename):
        list_details = []
        with open(filename,'r') as f:
            links = f.readlines()
        f.close()
        not_active = 0
        for link in links:
            name = ''
            details = ''
            price = ''
            if(link.startswith('https') > 0):
                self.navigate_to_url(link)
            else:
                continue
            if not_active == 5:
                break
            if self.check_exists_by_xpath("/html/body/div[2]/main/div/div[1]/div[2]/div[1]/h1[@class='st-name']"):
                name = self.driver.find_element(By.XPATH,"/html/body/div[2]/main/div/div[1]/div[2]/div[1]/h1[@class='st-name']").text
                name = re.sub("[\(\[].*?[\)\]]", "", name)
            else:
                not_active += 1
                continue
            if self.check_exists_by_xpath("/html/body/div[2]/main/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[@class='st-price-main']"):
                price = self.driver.find_element(By.XPATH,"/html/body/div[2]/main/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[@class='st-price-main']").text
                price = re.sub("[^0-9]","",price)

            else:
                not_active += 1
                continue
            if self.check_exists_by_xpath("/html/body/div[2]/main/div/div[2]/div/div[1]/div[2]/div[1]/div/div/a"):
                self.driver.find_element(By.XPATH,value='/html/body/div[2]/main/div/div[2]/div/div[1]/div[2]/div[1]/div/div/a').click()
                self.wait.until(
                    EC.visibility_of_element_located((By.XPATH,'/html/body/div[2]/main/div/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div[3]'))
                )
                details = self.driver.find_element(By.XPATH,value='/html/body/div[2]/main/div/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div[3]').text
                details = str(details).replace('\n',' ')
                details = re.sub('\s+',' ',details)
                details = name + '\n' + price +'\n' + details
                #detail_line = str(details).splitlines()
                list_details.append(details)
            else:
                not_active += 1
                continue
        return list_details
    
    def process_detail(self,list_details):
        db = Database()
        size = len(list_details)
        for i in range(size):
            details_line = list_details[i].splitlines()
            name = details_line[0]
            price = details_line[1]
            product_detail = details_line[2]
            inv_detail = re.search("Thông tin hàng hóa(.*)Thiết kế & Trọng lượng",product_detail)
            design_weight = re.search("Thiết kế & Trọng lượng(.*)Bộ xử lý",product_detail)
            chip = re.search("Bộ xử lý(.*)RAM",product_detail)
            ram = re.search("RAM(.*)Màn hình",product_detail)
            screen = re.search("Màn hình(.*)Đồ họa",product_detail)
            graphic = re.search("Đồ họa(.*)Lưu trữ",product_detail)
            storage = re.search("Lưu trữ(.*)Camera sau",product_detail)
            camera = re.search("Camera sau(.*)Selfie",product_detail)
            sensor = re.search("Cảm biến(.*)Bảo mật",product_detail)
            connect = re.search("Giao tiếp & kết nối(.*)Thông tin pin & Sạc",product_detail)
            battery = re.search("Thông tin pin & Sạc(.*)Hệ điều hành",product_detail)
            os_version = re.search("Hệ điều hành(.*)Phụ kiện trong hộp",product_detail)
            if inv_detail:
                inv_detail_val = inv_detail.group(1).strip()
            else:
                inv_detail_val = ''
            if design_weight:
                design_weight_val = design_weight.group(1).strip()
            else:
                design_weight_val = ''
            if chip:
                chip_val = chip.group(1).strip()
            else:
                chip_val = ''
            if ram:
                ram_val = ram.group(1).strip()
            else:
                ram_val = ''
            if screen:
                screen_val = screen.group(1).strip()
            else:
                screen_val = ''
            if graphic:
                graphic_val = graphic.group(1).strip()
            else:
                graphic_val = ''
            if storage:
                storage_val = storage.group(1).strip()
            else:
                storage_val = ''
            if camera:
                camera_val = camera.group(1).strip()
            else:
                camera_val = ''
            if sensor:
                sensor_val = sensor.group(1).strip()
            else:
                sensor_val = ''
            if connect:
                connect_val = connect.group(1).strip()
            else:
                connect_val = ''
            if battery:
                battery_val = battery.group(1).strip()
            else:
                battery_val = ''
            if os_version:
                os_version_val = os_version.group(1).strip()
            else:
                os_version_val = ''
            db.execute_query('''
                INSERT INTO product(fullname, price, inventory_detail, design_weight, chip, ram, screen, graphic, internal_storage, camera, sensor, connect_type, battery, os_version)
                 values('{}',{},'{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}');
            '''.format(str(name),price,inv_detail_val,design_weight_val,chip_val,ram_val,screen_val,graphic_val,storage_val,camera_val,sensor_val,connect_val,battery_val,os_version_val))

    def closeBrowser(self):
        self.driver.close()
    

if __name__ == "__main__":
    url = "https://fptshop.com.vn/"
    #db = Database()
    fpt = FPTBrowser()
    fpt.driver.maximize_window()
    try:
        #fpt.navigate_to_url(url)
        #fpt.get_phone_detail_links(fpt.get_links_from_navbar())
        list_details = fpt.get_detail_each_prod("mobile_link.txt")
        fpt.process_detail(list_details)
    except Exception as e:
        print(e)
    finally:
        fpt.closeBrowser()