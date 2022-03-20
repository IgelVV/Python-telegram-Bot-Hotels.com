import re
from typing import Optional


def remove_tags(text: str) -> str:
    """
    Очистка текста от HTML тегов.
    :param text: срока
    :return: строка без тегов
    """
    html_text_regex = re.compile(r'<[^>]+>')
    return html_text_regex.sub('', text)


def find_number(text: str) -> Optional[int]:
    """
    Находит и возвращает первое число из текста как int
    :param text: строка
    :return: первое целое число из строки, игнорируя знаки или None
    """
    result = re.search('[0-9]+', text)
    if result is not None:
        number_str = result.group(0)
        number = int(number_str)
    else:
        number = None
    return number


def price_range_from_text(text: str) -> list[int]:
    """
    Находит и возвращает все числа из текста как список int
    :param text: строка
    :return: список положительных целых чисел
    """
    numbers = re.findall('[0-9]+', text)
    numbers_int = [int(numb) for numb in numbers]
    numbers_int.sort()
    return numbers_int
