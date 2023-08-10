import fastapi
from routes import get_main_page, get_csv_file_statistics_search_words

app = fastapi.FastAPI()

app.include_router(get_main_page.route)
app.include_router(get_csv_file_statistics_search_words.route)
