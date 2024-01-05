import configparser
import os.path


# возвращает параметры парсинга из файла конфигураций ini_filepath
def get_ini_params(ini_filepath: str):
    params = {'Categories': None, 'Regions': None, 'LowBorder': None, 'HighBorder': None, 'MaxParsedNum': 1000}

    try:
        if not os.path.exists(ini_filepath):
            raise Exception(f"Файл конфигурации \'{ini_filepath}\' не найден")

        config = configparser.ConfigParser()
        config.read(ini_filepath, encoding='utf-8')

        # Категории
        categories = config.get('Categories filter', 'Categories').split('; ')

        for cat_id in range(len(categories)):
            categories[cat_id] = categories[cat_id].split('//')

        params['Categories'] = categories

        # Регионы
        regions = config.get('Regions filter', 'Regions')
        if regions == 'None':
            regions = [None]
        else:
            regions = regions.split('; ')

        params['Regions'] = regions

        # Нижняя граница по выручке
        lowBorder = config.get('Earnings filter', 'LowBorder')
        if lowBorder == 'None':
            lowBorder = None
        else:
            lowBorder = float(lowBorder)

        params['LowBorder'] = lowBorder

        # Верхняя граница по выручке
        highBorder = config.get('Earnings filter', 'HighBorder')
        if highBorder == 'None':
            highBorder = None
        else:
            highBorder = float(highBorder)

        params['HighBorder'] = highBorder

        # Макс кол-во спаршенных контрагентов в категории
        maxParsedCompanies = config.get('Contagents num filter', 'MaxParsedCompanies')
        if maxParsedCompanies != 'None':
            try:
                int(maxParsedCompanies)
            except ValueError:
                print(f'[INI СONFIG PARSER] Ошибка! Неверное значение \'{maxParsedCompanies}\' '
                      f'параметра MaxParsedCompanies.')

    except Exception as _ex:
        print(f'[INI СONFIG PARSER] Во время чтения параметров парсинга из \'{ini_filepath}\' возникла ошибка:\n{_ex}')

    finally:
        return params
