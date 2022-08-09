from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest, os , pickle

class LoginFacebook():
    def __init__(self):
        opts = Options()
        opts.set_preference("dom.webnotifications.enabled", False)
        opts.set_preference("dom.push.enabled", False)
        self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(),options=opts)

    def navigate_facebook(self):
        self.driver.get("https://facebook.com")

    def check_cookies(self,filename):
        if os.path.exists(filename):
            return True
        return False

    def write_cookies(self,filename):
        if os.path.exists(filename):
            os.remove(filename)
        pickle.dump( self.driver.get_cookies() , open(filename,"wb"))

    def load_cookies(self,filename):
        cookies = pickle.load(open(filename,"rb"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def wait_login_element_load(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "pass"))
        )

    def browseFacebook(self):
        self.navigate_facebook()
        filename = "cookies.pkl"
        if self.check_cookies(filename):
            self.load_cookies(filename)
            self.navigate_facebook()
        else:
            self.wait_login_element_load()

    def maximizeWindow(self):
        self.driver.maximize_window()

    def getLoginFromFile(self,filename):
        with open(filename,"r",encoding='utf-8') as f:
            lines = f.readlines()
            email = lines[0]
            pw = lines[1]
        f.close()
        return email,pw

    def actionLogin(self):
        filename = "cookies.pkl"
        if not self.check_cookies(filename):
            email , pw = self.getLoginFromFile("account.txt")
            self.driver.find_element(by=By.XPATH,value='//*[@id="email"]').send_keys(email)
            self.driver.find_element(by=By.XPATH,value='//*[@id="pass"]').send_keys(pw)
            self.driver.find_element(by=By.XPATH,value='//*[@name="login" and @type="submit"]').click()
        self.write_cookies(filename)

    def closeSession(self):
        self.driver.close()

if __name__ == "__main__":
    loginfb = LoginFacebook()
    try:
        loginfb.browseFacebook()
        loginfb.maximizeWindow()
        loginfb.actionLogin()
    except Exception as e:
        print(e)
    finally:
        pass
        #loginfb.closeSession()