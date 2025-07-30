import duckdb
import requests
from var import DB_PATH

def format_phone_number(phone_number: str) -> (str, str):
    """
    Форматирует номер телефона в формат "кодномер" (например, "9324271011").
    Удаляет префиксы "+..." (где ... от 1 до 3 цифр) или "8", если они есть.
    Возвращает отформатированный номер и страну.
    """
    phone_number = phone_number.strip()
    country = "Неизвестная страна"
    if len(phone_number) == 10 and phone_number.startswith("9"):
        country = "Россия"
    elif phone_number.startswith("8") or phone_number.startswith("79"):
        country = "Россия"
        phone_number = phone_number[1:]  # Удаляем "8"
    elif phone_number.startswith("+"):
        for country_name, code in country_codes.items():
            if phone_number.startswith(code):
                country = country_name
                phone_number = phone_number[len(code):]  # Удаляем код страны
                break
    return phone_number, country


def lookup_phone(phone):
    # Форматирование номера телефона
    phone_number, country = format_phone_number(phone)

    # Проверка длины номера
    if len(phone_number) <= 3:
        print("Неверный номер телефона")
    elif country == "Россия":
        # Разделение phone_number на kod и number
        kod = phone_number[:3]  # Первые три цифры — это код
        try:
            number = int(phone_number[3:])  # Остальная часть — это номер
        except ValueError:
            print("Номер телефона должен быть числом")

        # Подключение к базе данных
        try:
            con = duckdb.connect(DB_PATH)
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {str(e)}")

        # SQL-запрос к базе данных
        try:
            query = f"""
            SELECT "АВС/ DEF" as kod, От::INTEGER as "from", До::INTEGER as "to", Оператор, Регион
            FROM numbers.main.all_numbers
            WHERE kod = '{kod}' AND {number} >= "from" AND {number} <= "to"
            """
            result = con.sql(query).fetchall()
        except Exception as e:
            con.close()
            print(f"Ошибка выполнения SQL-запроса: {str(e)}")
        finally:
            con.close()

        # Проверка результата
        if not result:
            print("Информация по указанному номеру не найдена")

        # Формирование ответа
        row = result[0]
        region = row[4]
        if "|" in region in region:
            region = region.split("|")[0]  # Оставляем только часть до символа "|"

        if "*" in region in region:
            region = region.split("*")[0]  # Оставляем только часть до символа "|"

        response = {
            "phone": phone,
            # "kod": row[0],
            # "number": number,
            # "full_number": int(kod + str(number)),
            # "Оператор": row[3],
            "Страна": country,
            "Регион": row[4],
            # "Территория ГАР": row[6],
            # "ИНН": row[7],
        }

        print(response)
        return response


    else:
        response = {
            "phone": phone,
            "country": country
        }
        print(response)
        return response


if __name__ == "__main__":
    # Этот блок выполняется только при прямом запуске скрипта,
    # но не при импорте
    def search_phone():
        while True:
            number = input("Введите номер телефона (или 'stop/стоп' для выхода): ").strip()
            if number.lower() in ('stop', 'стоп'):
                break
            lookup_phone(number)


    search_phone()
