import time
import re
from parser_utils.driver_managment import get_htmlsoup, change_url, create_driver, kill_driver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains


# принимает на вход soup element и возвращает его информативное содержимое
def get_text_or_null(element):
    if element:
        return element.get_text()
    else:
        return None


wordDegRealtionsToMil = {'млн': 1, 'тыс': 0.001, 'млрд': 1000, 'трлн': 1000000}


# возвращает словарь с данными об компании по адрессу url
def get_data(driver):  # , url: str):
    # change_url(driver, url)

    soup = get_htmlsoup(driver)

    # Наименование
    companyName = get_text_or_null(soup.find('div', {'itemprop': 'name'}))

    # Вид деятельности
    activityType = get_text_or_null(soup.find('div', class_='cCard__OKVED-Name'))

    money_list = soup.find_all('span', class_='cCard__BlockMaskSum')

    # очистка от коварных элементов
    for list_id in range(len(money_list) - 1):
        if 'cCard__BlockMaskSum cCard__BlockMaskSum-date' in str(money_list[list_id]):
            money_list.pop(list_id)

    try:
        # Оборот/выручка (млн. руб.)
        if len(money_list) >= 1:
            earnings_split = get_text_or_null(money_list[0]).split()
            earnings = float(earnings_split[0]) * wordDegRealtionsToMil.get(earnings_split[1], None)

            if len(money_list) >= 2:
                # Прибыль (млн. руб.)
                profit_split = get_text_or_null(money_list[1]).split()
                profit = float(profit_split[0]) * wordDegRealtionsToMil.get(profit_split[1], None)

                if len(money_list) >= 3:
                    # Стоимость
                    netWorth_split = get_text_or_null(money_list[2]).split()
                    netWorth = float(netWorth_split[0]) * wordDegRealtionsToMil.get(netWorth_split[1], None)

                else:
                    netWorth = ''
            else:
                profit = ''
                netWorth = ''
        else:
            earnings = ''
            profit = ''
            netWorth = ''
    except ValueError and TypeError:
        earnings = ''
        profit = ''
        netWorth = ''

    # Руководство
    director = get_text_or_null(soup.find('span', {'itemprop': 'employee'}))

    # Кол-во сотрудников
    employeesNum = get_text_or_null(soup.find('span', {'itemprop': 'numberOfEmployees'}))

    # Телефон
    phoneNum = get_text_or_null(soup.find('div', {'itemprop': 'telephone'}))

    # Email
    email = get_text_or_null(soup.find('a', {'itemprop': 'email'}))

    # Сайт в сети интернет
    url_list = soup.find_all('span', {'itemprop': 'url'})

    used_urls = []

    urls = ''
    for site_url in url_list:
        stripted_url = get_text_or_null(site_url).strip()
        if stripted_url:
            if stripted_url not in used_urls:
                urls += stripted_url + '\n'
                used_urls.append(stripted_url)

    # Возраст компании (лет)
    companyAge = get_text_or_null(soup.find('div', class_='c-sbisru-CardStatus__duration'))
    if companyAge == 'На рынке менее полугода':
        companyAge = 0.5
    elif companyAge == 'На рынке более полутора лет':
        companyAge = 1.5
    else:
        try:
            companyAge = float(re.sub(r'\D', '', companyAge))
        except ValueError:
            pass
    # Совладельцы
    founders_list = soup.find_all('div', {'itemprop': 'founder'})
    founders = ''
    for founder in founders_list:
        founders += get_text_or_null(founder)
        if get_text_or_null(founder):
            founders += '\n'

    # Регион регистрации
    registrationAddress = get_text_or_null(soup.find('div', {'itemprop': 'address'}))

    resultData = {'Name': companyName, 'ActivityType': activityType, 'Earnings': earnings, 'Profit': profit,
                  'NetWorth': netWorth, 'Director': director, 'EmployeesNum': employeesNum, 'Phone': phoneNum,
                  'Email': email, 'OfficialSites': urls, 'CompanyAge': companyAge, 'Founders': founders,
                  'RegAddress': registrationAddress, 'UrlSBIS': driver.current_url}

    return resultData


# возвращает xpath bs4 элемента

def get_full_xpath(element):
    xpath = []
    while element.parent:
        siblings = element.find_previous_siblings(element.name)
        xpath_segment = f"{element.name}[{len(siblings) + 1}]"
        xpath.insert(0, xpath_segment)
        element = element.parent

    full_xpath = '/'.join(xpath)
    return f'/{full_xpath}'


# возвращает список ссылок компаний для парсинга
def start_contragents_parsing(categories: list, region: str, low_border: float, high_border: float,
                              max_parsed_num: int):
    driver = create_driver()
    change_url(driver, 'https://sbis.ru/contragents?p=categories')
    result_data = []

    try:
        soup = get_htmlsoup(driver)

        if soup.find('div', class_='sbis_ru-CookieAgreement__close'):
            close_cookies_button = driver.find_element(By.CLASS_NAME, 'sbis_ru-CookieAgreement__close')
            close_cookies_button.click()

        # Kakaya-to 6esoBshin(t)a Bo3BrashaeT posJle perBogo scroll'a o6ratHo k Bepxy cTpaHucbI, poeToMy makoN scroll
        driver.execute_script(f"window.scrollTo(0, 1000)")

        # ВЫБОР НЕОБХОДИМОЙ КАТЕГОРИИ
        for cat_id in range(len(categories)):
            sub_category = categories[cat_id]
            soup = get_htmlsoup(driver)
            actions = ActionChains(driver)

            category_element = soup.find('span', text=sub_category)
            if category_element:
                if cat_id != len(categories) - 1:
                    parent_elem = category_element.parent
                    expander_elem = parent_elem.find('div', {'data-qa': 'row-expander'})
                    expander_button = driver.find_element(By.XPATH, get_full_xpath(expander_elem))

                    actions.move_to_element(expander_button).perform()
                    expander_button.click()

                    time.sleep(1)
                    soup = get_htmlsoup(driver)
                    if not soup.find('span', text=categories[cat_id + 1]):
                        expander_button.click()
                        time.sleep(1)
                else:
                    category_button = driver.find_element(By.XPATH, get_full_xpath(category_element))
                    actions.move_to_element(category_button).perform()

                    category_button.click()

            else:
                print(f'[PARSING PROCESS] Ошибка! Категория \'{sub_category}\' не найдена...')
                return None

        print(f'[PARSING PROCESS] Категория \'{" -> ".join(categories)}\' успешно выбрана!')

        # ВЫБОР РЕГИОНА
        if region:
            time.sleep(3)
            dropdownButton = driver.find_element(By.XPATH, '//*[@id="iconExpanded"]')
            dropdownButton.click()
            time.sleep(1)

            soup = get_htmlsoup(driver)
            reg_button_match = soup.find('span', text=region)
            if reg_button_match:
                reg_button = driver.find_element(By.XPATH, get_full_xpath(reg_button_match))
                reg_button.click()
            else:
                print(f'[PARSING PROCESS] Не удалось найти регион {region}. Парсинг компаний со всех регионов.')

        # ПАРСИНГ КОНТРАГЕНТОВ
        time.sleep(1)
        soup = get_htmlsoup(driver)
        found_comapnies_num = get_text_or_null(soup.find('div', class_='sbis-Contractor-Companies__Total ws-ellipsis'))
        found_comapnies_num = int(found_comapnies_num.replace('Найдено', '').replace('компании', '')
                                  .replace('компаний', '').replace(' ', ''))
        # print(f'[PARSING PROCESS] Всего {found_comapnies_num} компаний категории \'{" -> ".join(categories)}\''
        #       f' в регионе {region}.')

        current_contragent_num = 0
        successfully_parsed_contragents = 0
        contragents_blocks = driver.find_elements(By.CLASS_NAME, 'sbis-Contragents-ContragentsList__Row')

        while current_contragent_num < found_comapnies_num and current_contragent_num < max_parsed_num \
                and current_contragent_num < len(contragents_blocks):
            contragents_blocks = driver.find_elements(By.CLASS_NAME, 'sbis-Contragents-ContragentsList__Row')

            try:
                contragents_blocks[current_contragent_num].click()
                driver.switch_to.window(driver.window_handles[1])
            except ElementClickInterceptedException:
                driver.execute_script(
                    f"window.scrollTo(0, {contragents_blocks[current_contragent_num - 1].location_once_scrolled_into_view.get('y')});")
                current_contragent_num += 1
                found_comapnies_num -= 1
                continue
            data = None

            try:
                data = get_data(driver)
                driver.close()
            except Exception as _ex:
                print(f'[PARSING PROCESS] Возникла ошибка! {_ex}')
            finally:
                driver.switch_to.window(driver.window_handles[0])
                driver.execute_script(
                    f"window.scrollTo(0, {contragents_blocks[current_contragent_num].location_once_scrolled_into_view.get('y')});")

            if data:
                if data.get('Earnings') != '' and data.get('Earnings') < low_border:
                    print('[PARSING PROCESS] Парсинг прекращён, т.к. выручка последующих контрагентов меньше заданной '
                          'границы')
                    break

                successfully_parsed_contragents += 1
                result_data.append(data)
                print(f'[PARSING PROCESS] Информация об контрагенте \'{data.get("Name")}\' успешно получена!\n'
                      f'Кол-во спаршенных контрагентов: {successfully_parsed_contragents}')

            current_contragent_num += 1
            # input(f'{current_contragent_num}')

    finally:
        time.sleep(3)
        kill_driver(driver)
        print(result_data)
        return result_data
