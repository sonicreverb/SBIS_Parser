import parser_utils
import data_utils


def main():
    params = data_utils.get_ini_params('params.ini')
    print(f'[MAIN] Параметры парсинга:\n{params}\n')

    lowBorder = params['LowBorder']
    highBorder = params['HighBorder']

    maxParsedCompNum = params['MaxParsedNum']

    timeDelay = params['TimeDelay']

    for current_category in params['Categories']:
        for current_region in params['Regions']:
            print(f'[MAIN] Поиск компаний в категории \'{" -> ".join(current_category)}\'', end='')

            if current_region:
                print(f' в регионе {current_region}.', end=' ')
            else:
                print('.', end=' ')

            if lowBorder:
                print(f'Нижняя граница выручки - {lowBorder} млн. руб.', end=' ')

            if highBorder:
                print(f'Верхняя граница выручки - {highBorder} млн. руб.', end='')

            print()

            data = []

            try:
                data = parser_utils.start_contragents_parsing(current_category, current_region, lowBorder, highBorder,
                                                              maxParsedCompNum, timeDelay)
            except Exception as _ex:
                print(f'{_ex}\n[MAIN] Во время парсинга ссылок возникла ошибка, повторяю попытку.')
                try:
                    if len(data) == 0:
                        data = parser_utils.start_contragents_parsing(current_category, current_region, lowBorder,
                                                                      highBorder, maxParsedCompNum, timeDelay)
                    else:
                        print(f'{_ex}\n[MAIN] Во время парсинга ссылок возникла ошибка.')
                except Exception as _ex:
                    print(f'{_ex}\n[MAIN] Во время парсинга ссылок возникла ошибка.')

            finally:
                if data:
                    data_utils.write_to_excel('SBIS parser output.xlsx', data)


if __name__ == "__main__":
    try:
        main()
    except Exception as _ex:
        print(f'[MAIN] Во время выполнения программы произошла критическая ошибка!\n{_ex}')
    finally:
        input("[MAIN] Для завершения работы программы нажмите ENTER.")
