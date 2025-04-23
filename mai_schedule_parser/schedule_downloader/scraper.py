import urllib.parse
from requests_html import HTMLSession
import urllib
import os
import cachetools

CACHE_DIR = "cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

cache = cachetools.TTLCache(maxsize=128, ttl=300) # Кэшируем на 5 минут

def url_gen(group_number, week_number):
    return f'https://mai.ru/education/studies/schedule/index.php?group={urllib.parse.quote(group_number)}&week={week_number}'

def get_html(group_number, week_number):
    url = url_gen(group_number, week_number)

    try:
        if group_number in cache:
            print(f"[scraper.py]Загрузка из кэша: {group_number}")
            return cache[group_number]

        session = HTMLSession()
        session.get(url)  # получаем кукиз для входа
        r = session.get(url, allow_redirects=False)  # парсим
        html = r.html.html  # Получаем HTML в виде строки
        
        session.close()

        if r.status_code != 200:
            raise Exception(f"Ошибка при загрузке страницы: {r.status_code}")

        print(f"[scraper.py]Загрузка с сайта: {group_number}")
        cache[group_number] = html
        return html
    except Exception as e:
        print(f"[scraper.py]Ошибка при загрузке HTML: {e}")
        return None
