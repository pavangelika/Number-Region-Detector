import duckdb
import os
import glob
from var import DOWNLOAD_DIR, DB_PATH


def csv_to_duckdb():
    # Подключаемся к базе DuckDB
    conn = duckdb.connect(DB_PATH)

    # Получаем список CSV-файлов
    csv_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.csv"))
    if not csv_files:
        print("Не найдены CSV-файлы для обработки")
        return

    # Создаем таблицы из CSV
    for csv_file in csv_files:
        table_name = os.path.splitext(os.path.basename(csv_file))[0].replace("-", "_")

        try:
            # Сначала проверим структуру файла
            conn.execute(f"CREATE TEMP TABLE temp_table AS SELECT * FROM read_csv_auto('{csv_file}')")
            columns = conn.execute(f"DESCRIBE temp_table").fetchall()
            conn.execute("DROP TABLE temp_table")

            # print(f"\nСтруктура файла {csv_file}:")
            # for col in columns:
            #     print(f"- {col[0]}: {col[1]}")

            # Создаем основную таблицу
            conn.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS 
                SELECT * FROM read_csv_auto('{csv_file}')
            """)
            print(f"✓ Таблица {table_name} создана")

        except Exception as e:
            print(f"✕ Ошибка при обработке {csv_file}: {str(e)}")
            continue

    # Создаем объединенную таблицу с правильными именами столбцов
    try:
        conn.execute("""
            CREATE OR REPLACE TABLE all_numbers AS
            SELECT *
            FROM (
                SELECT * FROM DEF_9xx 
                UNION ALL 
                SELECT * FROM ABC_3xx
                UNION ALL 
                SELECT * FROM ABC_4xx
                UNION ALL
                SELECT * FROM ABC_8xx
            )
        """)
        print("\n✓ Объединенная таблица создана")

    except Exception as e:
        print(f"\n✕ Ошибка при создании объединенной таблицы: {str(e)}")

        # Покажем доступные таблицы и их структуру
        tables = conn.execute("SHOW TABLES").fetchall()
        # print("\nДоступные таблицы в базе:")
        # for table in tables:
        #     print(f"\nСтруктура таблицы {table[0]}:")
        #     cols = conn.execute(f"DESCRIBE {table[0]}").fetchall()
        #     for col in cols:
        #         print(f"- {col[0]}: {col[1]}")

    finally:
        conn.close()
        # print(f"\nБаза данных сохранена: {DB_PATH}")



    # Проверяем и создаем папку если нужно
# os.makedirs(DOWNLOAD_DIR, exist_ok=True)

#     # Запускаем процесс
csv_to_duckdb()