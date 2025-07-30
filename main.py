import os
import time
import subprocess

from unicodedata import lookup
from var import DOWNLOAD_DIR, DB_PATH
from without_API import lookup_phone

def wait_for_csv_files(timeout=60):
    """Ожидает появления CSV файлов в папке загрузки"""
    print("⏳ Ожидаем загрузку CSV файлов...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        csv_files = [f for f in os.listdir(DOWNLOAD_DIR)
                     if f.endswith('.csv') and not f.startswith('.')]

        if csv_files:
            print(f"✅ Обнаружены CSV файлы: {', '.join(csv_files)}")
            return True

        # Проверяем наличие временных файлов загрузки
        temp_files = [f for f in os.listdir(DOWNLOAD_DIR)
                      if f.endswith(('.crdownload', '.part'))]
        if temp_files:
            print(f"🔄 Идет загрузка... ({len(temp_files)} активных загрузок)")

        time.sleep(3)

    print("❌ Таймаут: CSV файлы не появились")
    return False


def wait_for_database_creation(timeout=30):
    """Ожидает создания файла базы данных"""
    print("⏳ Ожидаем создание базы данных...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        if os.path.exists(DB_PATH):
            db_size = os.path.getsize(DB_PATH)
            if db_size > 1024:  # Проверяем что файл не пустой
                print(f"✅ База данных создана ({db_size // 1024} KB)")
                return True
            print(f"🔄 Файл БД есть, но еще пустой ({db_size} bytes)")
        time.sleep(2)

    print("❌ Таймаут: база данных не создана")
    return False


def run_script_with_checks(script_name, pre_check=None, post_check=None):
    """Запускает скрипт с проверками до и после"""
    if pre_check and not pre_check():
        return False

    try:
        print(f"\n🚀 Запуск {script_name}...")
        process = subprocess.Popen(
            ['python', script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        # Вывод логов в реальном времени
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

        if process.returncode != 0:
            print(f"\n❌ Ошибка в {script_name}:")
            print(process.stderr.read())
            return False

        if post_check and not post_check():
            return False

        return True

    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {str(e)}")
        return False


def main():

    # 1. Проверка и создание папки
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # 2. Запуск загрузчика с проверками
    print("\n" + "=" * 50)
    print("📱 СИСТЕМА ОБНОВЛЕНИЯ БАЗЫ НОМЕРОВ")
    print("=" * 50)
    if not run_script_with_checks(
            "download_csv_cod_and_numbers.py",
            post_check=wait_for_csv_files
    ):
        print("\n🔴 Прерывание: ошибка загрузки CSV")
        return

    # 3. Запуск создания БД с проверками
    if not run_script_with_checks(
            "create_db.py",
            post_check=wait_for_database_creation
    ):
        print("\n🔴 Прерывание: ошибка создания БД")
        return

    # 4. Финальная проверка
    print("\n" + "=" * 50)
    print("🔍 Проверяем результаты:")

    csv_count = len([f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.csv')])
    db_exists = os.path.exists(DB_PATH)

    print(f"• CSV файлов: {csv_count}")
    print(f"• База данных: {'найдена' if db_exists else 'отсутствует'}")

    if csv_count > 0 and db_exists:
        print(f"📊 Путь к базе: {DB_PATH}")
    else:
        print("\n⚠️ Завершено с проблемами. Проверьте логи.")

    print("=" * 50)

    # 5. Запуск проверки номера телефона
    while True:
        number = input("Введите номер телефона (или 'stop/стоп' для выхода): ").strip()

        if number.lower() in ('stop', 'стоп'):
            break

        lookup_phone(number)


if __name__ == "__main__":
    main()