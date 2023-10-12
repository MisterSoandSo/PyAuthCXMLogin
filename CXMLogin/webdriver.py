from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

class Webdriver(object):
    def __init__(self, browser='Chrome',email = None, password = None):
        if browser == 'Chrome':
            self.browser = self._headless_chrome()
        else:
            self.browser = self._headless_firefox()
        self.email = email
        self.password = password

    def _headless_chrome(self):
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_argument('--headless')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        return webdriver.Chrome(options=options)

    def _headless_firefox(self):
        from selenium.webdriver.firefox.options import Options
        options = Options()
        options.headless = True
        return webdriver.Firefox(options=options)

    def _get_url(self, url) -> None:
        self.browser.get(url)

    def _non_2FA_login(self, redirect=None) -> str:
        # MS Live HTML div IDs
        EMAILFIELD = (By.ID, "i0116")
        PASSWORDFIELD = (By.ID, "i0118")
        NEXTBUTTON = (By.ID, "idSIButton9")

        try:
            WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable(EMAILFIELD)).send_keys(self.email)
            WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable(NEXTBUTTON)).click()
            WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable(PASSWORDFIELD)).send_keys(self.password)
            WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable(NEXTBUTTON)).click()
            WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable(NEXTBUTTON)).click()
            WebDriverWait(self.browser, 10).until(EC.url_contains(redirect))
            return self.browser.current_url
        except Exception as e:
            print(f"An error occurred: {str(e)}")

