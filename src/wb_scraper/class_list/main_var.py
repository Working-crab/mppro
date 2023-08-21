class Main_var():
    DB_NAME = "default"
    DB_PORT = "9000"
    DB_HOST = "localhost"
    DB_UNSERNAME = "default"
    DB_PASSWORD = ""
    DB_URL = f"""clickhouse://{DB_UNSERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"""