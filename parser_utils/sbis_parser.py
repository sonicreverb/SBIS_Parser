from parser_utils.driver_managment import get_htmlsoup, change_url


def get_text_or_null(element):
    if element:
        return element.get_text()
    else:
        return None


def get_data(driver, url: str):
    change_url(driver, url)

    soup = get_htmlsoup(driver)

    # Наименование
    companyName = get_text_or_null(soup.find('div', {'itemprop': 'name'}))

    # Вид деятельности
    activityType = get_text_or_null(soup.find('div', class_='cCard__OKVED-Name'))

    money_list = soup.find_all('span', class_='cCard__BlockMaskSum')

    # Оборот/выручка (млн. руб.)
    if len(money_list) >= 1:
        earnings = get_text_or_null(money_list[0])

        if len(money_list) >= 2:
            # Прибыль (млн. руб.)
            profit = get_text_or_null(money_list[1])

            if len(money_list) >= 3:
                # Стоимость
                netWorth = get_text_or_null(money_list[2])

            else:
                netWorth = ''
        else:
            profit = ''
            netWorth = ''
    else:
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
    urls = ''
    for site_url in url_list:
        urls += get_text_or_null(site_url)
        if get_text_or_null(site_url):
            urls += '\n'

    # Возраст компании (лет)
    companyAge = get_text_or_null(soup.find('div', class_='c-sbisru-CardStatus__duration'))
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
                  'RegAddress': registrationAddress, 'UrlSBIS': url}

    return resultData
