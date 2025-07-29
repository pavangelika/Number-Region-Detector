import requests
from bs4 import BeautifulSoup

# URL страницы с кодами
url = "https://teadmiseks.ee/ru/poleznoe/telefonnye-kody/"

def fetch_country_codes(url):
    # Делаем запрос к странице
    response = requests.get(url)
    response.raise_for_status()  # Проверяем успешность запроса

    # Парсим HTML с помощью BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Ищем таблицу с кодами
    table = soup.find("table")

    # Проверяем наличие таблицы
    if not table:
        raise ValueError("Таблица с кодами не найдена")

    # Извлекаем строки таблицы
    rows = table.find_all("tr")

    # Создаем словарь для кодов
    country_codes = {}

    # Обрабатываем каждую строку
    for row in rows[1:]:  # Пропускаем заголовок таблицы
        cols = row.find_all("td")
        if len(cols) >= 2:
            country = cols[0].text.strip()  # Название страны
            code = cols[1].text.strip()    # Код страны
            country_codes[country] = code

    return country_codes

# Получаем данные
try:
    country_codes = fetch_country_codes(url)
    # print(country_codes)  # Печатаем или сохраняем словарь

except Exception as e:
    print(f"Ошибка: {e}")
