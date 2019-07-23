import sys, time, selenium, pyautogui, cv2
import numpy as np

from selenium.webdriver.chrome.options import Options
from selenium import webdriver

import tools
from bot import Bot

class PageManager(object):
    def __init__ (self, game_url, path_to_extension, executable_path):
        self.game_url = game_url
        self.path_to_extension = path_to_extension
        self.executable_path = executable_path
        self.driver = None


    def start_selenium(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        options.add_experimental_option('detach', True)
        options.add_argument("--start-maximized")
        options.add_extension(self.path_to_extension)

        driver = webdriver.Chrome(executable_path=self.executable_path, options=options)
        self.driver = driver
        self.driver.get(self.game_url)

        time.sleep(3)
        self.enable_flash()


    def login(self, email, password):
        self.close_register_window()

        email_field = self.driver.find_element_by_xpath('//*[@id="welcome_username"]')
        email_field.send_keys(email)

        password_field = self.driver.find_element_by_xpath('//*[@id="welcome_password"]')
        password_field.send_keys(password)

        sing_in_button = self.driver.find_element_by_xpath('//*[@id="welcome_box_sign_in_button"]')
        sing_in_button.click()


    def close_register_window(self):
        try:
            close_button = self.driver.find_element_by_xpath('//*[@id="kongregate_lightbox_wrapper"]/div[1]/a')
            close_button.click()
            time.sleep(0.5)
        except Exception:
            pass


    def enable_flash(self):
        flash_button = self.driver.find_element_by_xpath('''//*[@id='noflash']/p[2]/a''')
        while(True):
            if flash_button.text:
                flash_button.click()
                time.sleep(0.5)
                break

        screenshot = pyautogui.screenshot()
        np_screenshot = np.array(screenshot)
        enable_flash_location = tools.get_template_center_point(source=np_screenshot,
                                                                template_filename='allow.png')
        if enable_flash_location:
            pyautogui.click(enable_flash_location)
        else:
            print('enable flash button not found')
            sys.exit(0)


    def start_bot(self):
        bot = Bot(self.driver)
        bot.start()

        # while True:
        #     input()
        #     bot.switch()
