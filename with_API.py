from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import duckdb
from code_country import country_codes

# Создание экземпляра FastAPI
app = FastAPI()

# Путь к базе данных
DB_PATH = "D:\\!Numbers\\numbers.db"

# Модель для запроса
class PhoneRequest(BaseModel):
    phone_number: str  # Полный номер телефона в формате "кодномер" (например, "+79324271011")

def format_phone_number(phone_number: str) -> (str, str):
    """
    Форматирует номер телефона в формат "кодномер".
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

@app.post("/lookup-phone/")
async def lookup_phone(data: PhoneRequest):
    # Форматирование номера телефона
    phone_number, country = format_phone_number(data.phone_number)

    # Проверка на минимальную длину номера
    if len(phone_number) <=3:
        raise HTTPException(status_code=400, detail="Неверный номер телефона")

    # Если страна Россия, проверяем номер в базе
    if country == "Россия":
        # Разделение phone_number на код и номер
        kod = phone_number[:3]  # Первые три цифры — это код
        try:
            number = int(phone_number[3:])  # Остальная часть — это номер
        except ValueError:
            raise HTTPException(status_code=400, detail="Номер телефона должен быть числом")

        # Подключение к базе данных
        try:
            with duckdb.connect(DB_PATH) as con:
                query = """
                SELECT "АВС/ DEF" as kod, От::INTEGER as "from", До::INTEGER as "to", Емкость, Оператор, Регион, "Территория ГАР", ИНН
                FROM numbers.main.phones
                WHERE kod = ? AND ? >= "from" AND ? <= "to"
                """
                result = con.execute(query, (kod, number, number)).fetchall()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка работы с базой данных: {str(e)}")

        # Проверка результата
        if not result:
            raise HTTPException(status_code=404, detail="Информация по указанному номеру не найдена")

        # Формирование ответа
        row = result[0]
        region = row[5]
        if "|" in region:
            region = region.split("|")[0]  # Оставляем только часть до символа "|"
        response = {
            "phone": data.phone_number,
            "kod": row[0],
            "number": number,
            "full_number": int(phone_number),
            "country": country,
            "Оператор": row[4],
            "Регион": region,
            "Территория ГАР": row[6],
            "ИНН": row[7],
        }

        return response

    # Если страна не Россия, просто возвращаем информацию о стране
    else:
        return {
            "phone": data.phone_number,
            "country": country
        }
