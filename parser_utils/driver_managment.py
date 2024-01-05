from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup


# возвращает настроенный driver с отключенной загрузкой изображений
def create_driver():
    chrome_options = Options()

    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 "
                                "Firefox/84.0")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('https://duckduckgo.com/')
    # print('[DRIVER INFO] Driver created successfully with disabled images.')
    return driver


# закрывает все окна и завершает сеанс driver
def kill_driver(driver):
    driver.close()
    driver.quit()
    # print('[DRIVER INFO] Driver was closed successfully.')


# изменяет url текущего открытого окна драйвера
def change_url(driver, new_url: str):
    driver.execute_script('window.location.href = arguments[0];', new_url)


# возвращает soup указанной страницы
def get_htmlsoup(driver):
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return soup

    except Exception as exc:
        print(f'[GET SOUP] Error while trying to get soup was accuired {exc}')
        return None
