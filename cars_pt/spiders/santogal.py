import scrapy
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
from time import sleep
import os
import codecs


def start_driver():
    chrome_options = Options()
    LOGGER.setLevel(logging.WARNING)
    arguments = ['--lang=pt-BR', '--window-size=1920,1080',
                 '--headless', '--disable-gpu', '--no-sandbox']

    for argument in arguments:
        chrome_options.add_argument(argument)

    chrome_options.add_experimental_option('prefs', {
        'download.prompt_for_download': False,
        'profile.default_content_setting_values.notifications': 2,
        'profile.default_content_setting_values.automatic_downloads': 1,

    })
    driver = webdriver.Chrome(options=chrome_options)

    wait = WebDriverWait(
        driver,
        10,
        poll_frequency=0.5,
        ignored_exceptions=[
            NoSuchElementException,
            ElementNotVisibleException,
            ElementNotSelectableException,
        ]
    )
    return driver, wait


class SantogalCarsSpider(scrapy.Spider):
    allowed_domains = ['santogal.pt']
    name = 'santogalbot'
    start_urls = ['https://www.santogal.pt/search-page/']

    def parse(self, response):
        driver, wait = start_driver()
        driver.get(response.url)

        data = get_car_data()

        # Open Filters Header
        filter_tab = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@class='btn-icon btn-filters js-panelToggle']")))
        filter_tab.click()
        sleep(1)

        # Find Filters Dropdown Inputs
        filters = wait.until(EC.visibility_of_any_elements_located(
            (By.XPATH, "//span[@class='selection']//ul[@class='select2-selection__rendered']")))
        sleep(1)

        # Make Filter
        filters[3].click()
        sleep(1)

        try:
            make_tab_options = wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"//ul[@class='select2-results__options']/li[@aria-selected='false']/span[text()='{data[0]}']")))
            make_tab_options.click()
        except:
            print("already selected")

        # Model Filter
        filters[4].click()
        sleep(1)

        # try:
        #     #! Check labels
        #     model_tab_options = wait.until(EC.element_to_be_clickable(
        #         (By.XPATH, f"//ul[@class='select2-results__options']/li[@aria-selected='false']/span[text()='{data[1]}']")))
        #     model_tab_options.click()
        # except:
        #     print("already selected")

        driver.close()


class CarPageSpider(scrapy.Spider):
    allowed_domains = ['santogal.pt']
    name = 'cardatabot'
    start_urls = []

    def parse(self, response):
        driver, wait = start_driver()
        driver.get(response.url)

        caracteristicas_tags = driver.find_element(
            By.XPATH, "//section[@class='content_container']/h3[text()='Caraterísticas'//dt]")
        caracteristicas_values = driver.find_element(
            By.XPATH, "//section[@class='content_container']/h3[text()='Caraterísticas'//dd]")
        dict_caracteristicas = []

        for i in range(0, len(caracteristicas_tags)):
            dict_caracteristicas[caracteristicas_tags[i]
                                 ] = caracteristicas_values[i]

        mecanica_tags = driver.find_element(
            By.XPATH, "//section[@class='content_container']/h3[text()='Mecânica'//dt]")
        mecanica_values = driver.find_element(
            By.XPATH, "//section[@class='content_container']/h3[text()='Mecânica'//dd]")
        dict_mecanica = []

        for i in range(0, len(mecanica_tags)):
            dict_mecanica[mecanica_tags[i]] = mecanica_values[i]

        chassis_tags = driver.find_element(
            By.XPATH, "//section[@class='content_container']/h3[text()='Chassis'//dt]")
        chassis_values = driver.find_element(
            By.XPATH, "//section[@class='content_container']/h3[text()='Chassis'//dd]")
        dict_chassis = []

        for i in range(0, len(chassis_tags)):
            dict_chassis[chassis_tags[i]] = chassis_values[i]

        descricao = driver.find_element(
            By.XPATH, "//section[@class='content_container']/p[@class='detail']").text

        equipamentos = driver.find_elements(
            By.XPATH, "//section[@class='content_container']/h3[text()='Equipamentos']//h4[@clss='detail-subtitle']/dt")
        ops_list = []

        for desc in equipamentos:
            ops_list.append(desc)

        #! Basic Infos

        driver.close()


def get_car_data():
    car_data = []
    absolute_path = os.path.dirname(__file__)
    relative_path = "../../cardata.txt"
    domain_path = os.path.join(absolute_path, relative_path)

    for line in open(domain_path, 'r').readlines():
        car_data = line

    return car_data


def save_html(driver):
    absolute_path = os.path.dirname(__file__)
    relative_path = "../../search.html"
    domain_path = os.path.join(absolute_path, relative_path)
    file = codecs.open(domain_path, "w", "utf−8")
    page_html = driver.page_source
    file.write(page_html)
