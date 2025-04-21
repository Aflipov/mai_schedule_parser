import urllib.parse
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import urllib
import re


def url_gen(group_number):
    return 'https://mai.ru/education/studies/schedule/index.php?group=' + urllib.parse.quote(group_number)


url = url_gen('М8О-102БВ-24')

session = HTMLSession()
session.get(url)  # получаем кукиз для входа
r = session.get(url, allow_redirects=False)  # парсим
session.close()

print(f'Статус запроса: {r.status_code}')
print('HTML получен, начало скрапинга...\n')


soup = BeautifulSoup(r.html.html, 'html.parser')
days = soup.find(class_='step mb-5').find_all(class_='step-item')
for day in days:
    day_title = day.find(class_="step-content").find('span').text
    paras = day.select("div[class='mb-4']")

    day_title = re.sub(r'[\n\t]', '', day_title)
    day_title = re.sub(r'[\xa0]', ' ', day_title)

    print(f'\n\t{day_title}\n')

    for para in paras:
        para_title = para.find('div').text
        para_time_teacher_location = [x.text for x in para.find('ul').find_all('li')]

        para_title = re.sub(r'[\n\t]', '', para_title)
        para_title = f'{para_title[:-2]} {para_title[-2:]}'
        para_time_teacher_location = [
            re.sub(r'[\n\t]', '', item) for item in para_time_teacher_location]

        print(para_title)
        print(*para_time_teacher_location, sep=' | ')
        print('\n')