import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from var import download_dir, numeric, xpath_numeric, bdpn, xpath_bdpn


# Проверка скачались ли файлы
def downloading_files_process(download_dir):
    # Получаем список всех файлов в папке загрузки
    files = os.listdir(download_dir)
    # Если есть файлы, которые еще загружаются (оканчиваются на '.crdownload' или '.part')
    print(files)
    while True:
        if any([file.endswith(".crdownload") or file.endswith(".part") for file in files]):
            # print("Файлы еще загружаются...")
            time.sleep(10)  # Ждем 10 секунд перед проверкой снова
        else:
            filtered_files = [file for file in files if '(old)' not in file]
            print(f"Файл {filtered_files[-1]} загружен")
            break


# Клик по ссылке
def click_link(download_links_btn):
    for d in download_links_btn:
        d.click()
        print('Файл загружается...')
        time.sleep(4)
        """Ждет, пока все файлы в папке загрузок будут загружены."""
        downloading_files_process(download_dir)


# Скачивание файлов по xpath
def open_link(url, xpath):
    chrome_option = webdriver.ChromeOptions()
    prefs = {"download.default_directory": download_dir}
    chrome_option.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_option)
    driver.get(url)
    time.sleep(2)
    try:
        download_links_btn = driver.find_elements(By.XPATH, xpath)
        if download_links_btn:
            click_link(download_links_btn)
        details_btn = driver.find_element(By.XPATH, '//*[@id="details-button"]')
        while True:
            details_btn.click()
            driver.find_element(By.XPATH, '//*[@id="proceed-link"]').click()
            time.sleep(5)
            download_links_btn = driver.find_elements(By.XPATH, xpath)
            click_link(download_links_btn)
    except:
        print("Oops...Try again")


def delete_old():
    files = os.listdir(download_dir)
    if len(files) > 1:
        # Удаление файлов, содержащих '(old)'
        files_to_delete = [file for file in files if '(old)' in file]
        for file in files_to_delete:
            file_path = os.path.join(download_dir, file)
            os.remove(file_path)
            print(f"Файл '{file}' удалён")


def rename_to_old():
    # Переименование оставшихся файлов с добавлением '(old)'
    files = os.listdir(download_dir)
    for file in files:
        old_path = os.path.join(download_dir, file)
        new_name = file.replace('.csv', '(old).csv')
        new_path = os.path.join(download_dir, new_name)
        os.rename(old_path, new_path)
        print(f"Файл '{file}' переименован в '{new_name}'")


def downloading_start():
    rename_to_old()
    open_link(numeric, xpath_numeric)
    # open_link(bdpn, xpath_bdpn)
    delete_old()


downloading_start()
