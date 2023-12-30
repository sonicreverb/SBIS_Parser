import parser_utils


def main():
    driver = parser_utils.create_driver()

    test_urls = [
        'https://sbis.ru/contragents/7736050003/997250001',
        'https://sbis.ru/contragents/1644003838/164401001',
        'https://sbis.ru/contragents/7842155505/781001001',
        'https://sbis.ru/contragents/5003052454/997350001',
        'https://sbis.ru/contragents/6316031581/891101001',
        'https://sbis.ru/contragents/8904034784/997250001',
        'https://sbis.ru/contragents/7728168971/997950001'
    ]

    for test_url in test_urls:
        data = parser_utils.get_data(driver, test_url)
        print(data)

    parser_utils.kill_driver(driver)


if __name__ == "__main__":
    main()
