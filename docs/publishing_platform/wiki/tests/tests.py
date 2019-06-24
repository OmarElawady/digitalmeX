import nose
import unittest
import logging
from selenium import webdriver
import configparser


class wikis_test(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.docs_url = config["main"]["wikis_url"]

    def setUp(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.implicitly_wait(30)
        self.driver.maximize_window()
        self.driver.get(self.docs_url)

    def tearDown(self):
        self.driver.quit()

    def test001_sidbar_hide(self):
        elem = self.driver.find_elements_by_xpath("/html/body/main/aside")[0]
        self.assertTrue(elem.is_displayed())
        self.driver.get("%s/#/?sidebar=hide" % self.docs_url)
        elem = self.driver.find_elements_by_xpath("/html/body/main/aside")[0]
        self.assertFalse(elem.is_displayed())

    def test002_graprh(self):
        elem = self.driver.find_elements_by_xpath("/html/body/main/aside/div[2]/ul/li[1]/a")[0]
        self.assertTrue(elem.is_displayed())
        self.driver.get("%s/#/?sidebar=hide" % self.docs_url)
        elem = self.driver.find_elements_by_xpath("/html/body/main/aside")[0]
        self.assertFalse(elem.is_displayed())
