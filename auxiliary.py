import re


def remove_tags(text):
    """
    Очистка текста от HTML тегов.
    :param text:
    :return:
    """
    html_text_regex = re.compile(r'<[^>]+>')
    return html_text_regex.sub('', text)


def find_number(text):
    """
    Находит и возвращает первое число из текста как int
    :param text:
    :return:
    """
    result = re.search('[0-9]+', text)
    if result is not None:
        number_str = result.group(0)
        number = int(number_str)
    else:
        number = None
    return number


def price_range_from_text(text):
    """
    Находит и возвращает все числа из текста как список int
    :param text:
    :return:
    """
    numbers = re.findall('[0-9]+', text)
    numbers_int = [int(numb) for numb in numbers]
    numbers_int.sort()
    return numbers_int
