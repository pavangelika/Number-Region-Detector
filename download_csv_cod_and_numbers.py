import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from var import DOWNLOAD_DIR, NUMERIC, XPATH_NUMERIC, BDPN, XPATH_BDPN


def ensure_directory_exists(path):
    """Создает директорию, если она не существует"""
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Директория {path} создана или уже существует")
    except Exception as e:
        print(f"Ошибка при создании директории {path}: {e}")
        raise


def downloading_files_process(DOWNLOAD_DIR):
    """Ожидает завершения всех загрузок"""
    while True:
        try:
            files = os.listdir(DOWNLOAD_DIR)
            # Игнорируем скрытые и временные файлы
            downloading = [f for f in files if f.endswith(('.crdownload', '.part')) and not f.startswith('.')]

            if not downloading:
                new_files = [f for f in files if '(old)' not in f and not f.startswith('.')]
                if new_files:
                    print(f"Загрузка завершена. Новые файлы: {new_files}")
                    return

            # print(f"Ожидание завершения загрузки... В процессе: {downloading}")
            time.sleep(5)
        except Exception as e:
            print(f"Ошибка при проверке файлов: {e}")
            time.sleep(5)


def click_download_links(driver, xpath, DOWNLOAD_DIR):
    """Нажимает все найденные кнопки загрузки"""
    try:
        elements = driver.find_elements(By.XPATH, xpath)
        if not elements:
            print("Не найдены элементы для загрузки")
            return False

        for element in elements:
            try:
                element.click()
                # print("Начата загрузка файла...")
                downloading_files_process(DOWNLOAD_DIR)
            except Exception as e:
                print(f"Ошибка при клике: {e}")
        return True
    except Exception as e:
        print(f"Ошибка при поиске элементов: {e}")
        return False


def handle_ssl_warning(driver):
    """Пытается обработать SSL предупреждение"""
    try:
        details_btn = driver.find_element(By.XPATH, '//*[@id="details-button"]')
        details_btn.click()
        proceed_link = driver.find_element(By.XPATH, '//*[@id="proceed-link"]')
        proceed_link.click()
        time.sleep(2)
        return True
    except:
        return False


def download_from_url(url, xpath, DOWNLOAD_DIR):
    """Основная функция загрузки с одного URL"""
    print(f"\nНачало загрузки с {url}")

    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False
    })
    options.add_argument('--headless') # скрытый режим

    try:
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(2)

        # Первая попытка загрузки
        if not click_download_links(driver, xpath, DOWNLOAD_DIR):
            # Если не получилось, пробуем обработать SSL предупреждение
            if handle_ssl_warning(driver):
                click_download_links(driver, xpath, DOWNLOAD_DIR)

    except Exception as e:
        print(f"Критическая ошибка: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass


def rename_existing_files(DOWNLOAD_DIR):
    """Добавляет (old) к существующим файлам"""
    try:
        files = [f for f in os.listdir(DOWNLOAD_DIR) if not f.startswith('.')]
        for file in files:
            if '(old)' not in file:
                old_path = os.path.join(DOWNLOAD_DIR, file)
                new_name = f"{os.path.splitext(file)[0]}(old){os.path.splitext(file)[1]}"
                new_path = os.path.join(DOWNLOAD_DIR, new_name)

                try:
                    os.rename(old_path, new_path)
                    print(f"Переименован: {file} → {new_name}")
                except Exception as e:
                    print(f"Ошибка при переименовании {file}: {e}")
    except Exception as e:
        print(f"Ошибка при переименовании файлов: {e}")


def delete_old_files(DOWNLOAD_DIR):
    """Удаляет файлы с пометкой (old)"""
    try:
        files = [f for f in os.listdir(DOWNLOAD_DIR) if not f.startswith('.')]
        for file in files:
            if '(old)' in file:
                try:
                    os.remove(os.path.join(DOWNLOAD_DIR, file))
                    print(f"Удален старый файл: {file}")
                except Exception as e:
                    print(f"Ошибка при удалении {file}: {e}")
    except Exception as e:
        print(f"Ошибка при удалении старых файлов: {e}")


def downloading_start():
    """Основная функция запуска процесса загрузки"""
    print("Начало процесса обновления базы...")
     # 1. Подготовка директории
    try:
        ensure_directory_exists(DOWNLOAD_DIR)
    except:
        print("Невозможно продолжить без рабочей директории")
        return
    # 2. Архивирование старых файлов
    rename_existing_files(DOWNLOAD_DIR)

    # 3. Загрузка новых данных
    download_from_url(NUMERIC, XPATH_NUMERIC, DOWNLOAD_DIR)
    # download_from_url(BDPN, XPATH_BDPN, DOWNLOAD_DIR)  # Раскомментировать при необходимости

    # 4. Очистка старых файлов
    delete_old_files(DOWNLOAD_DIR)
    print("Процесс обновления завершён успешно!")


downloading_start()
