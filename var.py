import os

DOWNLOAD_DIR = r"C:\Numbers"
NUMERIC = "https://opendata.digital.gov.ru/registry/numeric/downloads"
XPATH_NUMERIC = '//*[@id="__layout"]/div/main//button'
BDPN = 'https://www.bdpn.online/'
XPATH_BDPN = '//section[1]/div//a[2]'
DB_PATH = os.path.join(DOWNLOAD_DIR, "numbers.duckdb")
