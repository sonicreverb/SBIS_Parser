import time
import re

from parser_utils.driver_managment import get_htmlsoup, change_url, create_driver, kill_driver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as exp_conditions


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
    elif companyAge == 'На рынке более года':
        companyAge = 1
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
                              max_parsed_num: int, timeDelay: float):
    driver = create_driver()
    change_url(driver, 'https://sbis.ru/contragents?p=categories')
    result_data = []

    try:
        soup = get_htmlsoup(driver)

        if soup.find('div', class_='sbis_ru-CookieAgreement__close'):
            close_cookies_button = driver.find_element(By.CLASS_NAME, 'sbis_ru-CookieAgreement__close')
            close_cookies_button.click()

        # Kakaya-to 6esoBshin(t)a Bo3BrashaeT posJle perBogo scroll'a o6ratHo k Bepxy cTpaHucbI, poeToMy makoN scroll
        actions = ActionChains(driver)
        actions.send_keys(Keys.PAGE_DOWN)

        # ВЫБОР НЕОБХОДИМОЙ КАТЕГОРИИ
        for cat_id in range(len(categories)):
            sub_category = categories[cat_id]
            soup = get_htmlsoup(driver)

            category_element = soup.find('span', text=sub_category)
            if category_element:
                if cat_id != len(categories) - 1:
                    parent_elem = category_element.parent
                    expander_elem = parent_elem.find('div', {'data-qa': 'row-expander'})
                    expander_button = driver.find_element(By.XPATH, get_full_xpath(expander_elem))

                    actions.move_to_element(expander_button).perform()
                    expander_button.click()

                    time.sleep(3)
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
            driver_wait = WebDriverWait(driver, 10)
            driver_wait.until(exp_conditions.presence_of_element_located((By.XPATH, '//*[@id="iconExpanded"]')))

            dropdownButton = driver.find_element(By.XPATH, '//*[@id="iconExpanded"]')
            dropdownButton.click()
            time.sleep(5)

            soup = get_htmlsoup(driver)
            reg_button_match = soup.find('span', text=region)
            if reg_button_match:
                reg_button = driver.find_element(By.XPATH, get_full_xpath(reg_button_match))
                reg_button.click()
            else:
                print(f'[PARSING PROCESS] Не удалось найти регион {region}. Парсинг компаний со всех регионов.')

        # ПАРСИНГ КОНТРАГЕНТОВ
        time.sleep(5)
        soup = get_htmlsoup(driver)
        found_comapnies_num = get_text_or_null(soup.find('div', class_='sbis-Contractor-Companies__Total ws-ellipsis'))
        found_comapnies_num = int(found_comapnies_num.replace('Найдено', '').replace('компании', '')
                                  .replace('компаний', '').replace(' ', ''))
        # print(f'[PARSING PROCESS] Всего {found_comapnies_num} компаний категории \'{" -> ".join(categories)}\''
        #       f' в регионе {region}.')

        current_contragent_num = 0
        successfully_parsed_contragents = 0
        encounter_contragents_elements = []

        # flag_need_to_filter_high_border = True

        scroll_page_button = driver.find_element(By.XPATH, '//*[@id="container"]'
                                                           '/div/div/div/div/div[2]/div[1]/div/div/div/div[2]/div'
                                                           '/div[2]/div[3]/div[1]/div/div/div/div/span[3]/i')

        flag_not_reached_low_border = True

        while current_contragent_num < found_comapnies_num and successfully_parsed_contragents < max_parsed_num and \
                flag_not_reached_low_border:
            contragents_blocks = driver.find_elements(By.CLASS_NAME, 'sbis-Contragents-ContragentsList__Row')
            actions = ActionChains(driver)

            flag_unique_contragents_found = False

            for current_contragent_webelem in contragents_blocks:
                if current_contragent_webelem not in encounter_contragents_elements:
                    try:
                        actions.move_to_element(current_contragent_webelem).click()
                        current_contragent_webelem.click()
                        driver.switch_to.window(driver.window_handles[1])

                    except ElementClickInterceptedException:
                        continue

                    data = None

                    try:
                        data = get_data(driver)
                    except Exception as _ex:
                        print(f'[PARSING PROCESS] Возникла ошибка! {_ex}')
                    finally:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])

                    if data:
                        if low_border and data.get('Earnings') != '' and data.get('Earnings') < low_border:
                            print('[PARSING PROCESS] Парсинг прекращён, т.к. выручка последующих контрагентов меньше '
                                  'заданной границы')

                            flag_not_reached_low_border = False
                            break

                        # aDckuu FuJlTep BepxHeU 7paHuCbl BblPy4Ku, koTopblu mak u He 6bl peaJli3oBaH
                        if high_border and data.get('Earnings') > high_border:
                            # if flag_need_to_filter_high_border: try: last_contragent_webelem_in_blocks =
                            # contragents_blocks[len(contragents_blocks) - 1] actions.move_to_element(
                            # last_contragent_webelem_in_blocks) last_contragent_webelem_in_blocks.click()
                            # driver.switch_to.window(driver.window_handles[1])
                            #
                            #         check_last_elem_earnings_data = get_data(driver)
                            #         print(check_last_elem_earnings_data.get('Name'),
                            #               check_last_elem_earnings_data.get('Earnings'), high_border)
                            #         print(check_last_elem_earnings_data.get('Earnings') < high_border)
                            #
                            #         if check_last_elem_earnings_data.get('Earnings') < high_border:
                            #             flag_need_to_filter_high_border = False
                            #             result_data.append(check_last_elem_earnings_data)
                            #             encounter_contragents_elements.append(last_contragent_webelem_in_blocks)
                            #         else:
                            #             print('123123')
                            #             scroll_page_button.click()
                            #             scroll_page_button.click()
                            #             input('123123')  # removeme
                            #             break
                            #     except Exception as _ex:
                            #         print(_ex)
                            #     finally:
                            #         driver.close()
                            #         driver.switch_to.window(driver.window_handles[0])
                            print(f'[PARSING PROCESS] Контрагент {data.get("Name")} не проходит по верхнему фильтру'
                                  f' выручки ({data.get("Earnings")}/{high_border})')
                        else:
                            successfully_parsed_contragents += 1
                            result_data.append(data)
                            print(
                                f'[PARSING PROCESS] Информация об контрагенте \'{data.get("Name")}\' успешно получена!'
                                f'\nКол-во спаршенных контрагентов: {successfully_parsed_contragents}')

                        # successfully_parsed_contragents += 1
                        # result_data.append(data)
                        # print(
                        #     f'[PARSING PROCESS] Информация об контрагенте \'{data.get("Name")}\' успешно получена!\n'
                        #     f'Кол-во спаршенных контрагентов: {successfully_parsed_contragents}')

                    current_contragent_num += 1
                    flag_unique_contragents_found = True
                    encounter_contragents_elements.append(current_contragent_webelem)
                    time.sleep(timeDelay)
            # fix or forget...
            if not flag_unique_contragents_found:
                current_contragent_num += 10

            scroll_page_button.click()
            scroll_page_button.click()

    finally:
        print(f'[PARSING PROCESS] Парсинг завершён. Кол-во спаршенных контрагентов: {len(result_data)}')
        try:
            kill_driver(driver)
        except Exception as _ex:
            i_dont_need_to_know_what_type_of_exception_there_just_stop_highlighting_this_please = _ex
        return result_data
