from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# import os.path
# import zipfile


# считывает из файла proxy.txt параметры прокси
# def get_proxy_creds():
#     result = {'host': '', 'port': '', 'login': '', 'password': ''}
#     if os.path.exists('proxy.txt'):
#         with open('proxy.txt', 'r') as file:
#             array_of_lines = file.readlines()
#         result['host'] = array_of_lines[0].strip()
#         result['port'] = array_of_lines[1].strip()
#         result['login'] = array_of_lines[2].strip()
#         result['password'] = array_of_lines[3].strip()
#
#         print(f'[SET PROXY] Данные прокси успешно получены '
#               f'({result["host"]}:{result["port"]} login - {result["login"]} password - {result["password"]})')
#         return result
#     else:
#         print('[SET PROXY] Не удалось найти файл с настройками прокси \'proxy.txt\'')
#         return None
#
#
# manifest_json = """
# {
#     "version": "1.0.0",
#     "manifest_version": 2,
#     "name": "Chrome Proxy",
#     "permissions": [
#         "proxy",
#         "tabs",
#         "unlimitedStorage",
#         "storage",
#         "<all_urls>",
#         "webRequest",
#         "webRequestBlocking"
#     ],
#     "background": {
#         "scripts": ["background.js"]
#     },
#     "minimum_chrome_version":"22.0.0"
# }
# """
#
#
# # возвращает настроенный driver с отключенной загрузкой изображений и proxy
# def create_driver():
#     chrome_options = Options()
#
#     try:
#         proxy_data = get_proxy_creds()
#     except Exception as _ex:
#         print(f'[SET PROXY] Не удалось получить параметры прокси. Ошибка ({_ex})')
#         proxy_data = False
#
#     if proxy_data:
#         proxy_host = proxy_data.get('host')
#         proxy_port = proxy_data.get('port')
#         proxy_username = proxy_data.get('login')
#         proxy_password = proxy_data.get('password')
#
#         background_js = """
#                 var config = {
#                         mode: "fixed_servers",
#                         rules: {
#                         singleProxy: {
#                             scheme: "http",
#                             host: "%s",
#                             port: parseInt(%s)
#                         },
#                         bypassList: ["localhost"]
#                         }
#                     };
#
#                 chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
#
#                 function callbackFn(details) {
#                     return {
#                         authCredentials: {
#                             username: "%s",
#                             password: "%s"
#                         }
#                     };
#                 }
#
#                 chrome.webRequest.onAuthRequired.addListener(
#                             callbackFn,
#                             {urls: ["<all_urls>"]},
#                             ['blocking']
#                 );
#                 """ % (proxy_host, proxy_port, proxy_username, proxy_password)
#         pluginfile = 'proxy_auth_plugin.zip'
#
#         with zipfile.ZipFile(pluginfile, 'w') as zp:
#             zp.writestr("manifest.json", manifest_json)
#             zp.writestr("background.js", background_js)
#         chrome_options.add_extension(pluginfile)
#
#     prefs = {"profile.managed_default_content_settings.images": 2}
#     chrome_options.add_experimental_option("prefs", prefs)
#     chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 "
#                                 "Firefox/84.0")
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
#
#     # print('[DRIVER INFO] Driver created successfully with images disabled.\n')
#     return driver


# # возвращает настроенный driver с отключенной загрузкой изображений (OLD VER WITHOUT PROXIES)
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
