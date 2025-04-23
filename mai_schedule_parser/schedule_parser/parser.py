from bs4 import BeautifulSoup
import datetime
import re

def parse_schedule(html_content) -> list[dict]:
    """
    Парсит HTML расписания и возвращает список словарей, где каждый словарь
    представляет собой одно занятие.
    """
    
    eng_months = {
        'января': 1,
        'февраля': 2,
        'марта': 3,
        'апреля': 4,
        'мая': 5,
        'ибня': 6,
        'июля': 7,
        'августа': 8,
        'сентября': 9,
        'октября': 10,
        'ноября': 11,
        'декабря': 12
    }
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    group = soup.find(itemprop='headline').text
    group = re.sub(r'[\n\t]', '', group)

    days = soup.find(class_='step mb-5').find_all(class_='step-item')
    
    if not days:
        print('[parser.py]Тег step mb-5 или step-item не найден')
        return []

    schedule: list[dict] = []
    for day in days:        
        date = day.find(class_="step-content").find('span').text
        lessons = day.select("div[class='mb-4']")

        date = re.sub(r'[\n\t]', '', date)
        date = re.sub(r'[\xa0]', ' ', date)[4:].split()
        
        for lesson in lessons:
            lesson_title = lesson.find('div').text
            lesson_content = [x.text for x in lesson.find('ul').find_all('li')]
            lesson_content = [re.sub(r'[\n\t]', '', item) for item in lesson_content]

            lesson_title = re.sub(r'[\n\t]', '', lesson_title)
            lesson_subject = lesson_title[:-2]
            lesson_type = lesson_title[-2:]
            lesson_start_time = datetime.datetime.strptime(f'2025 {eng_months[date[1]]} {date[0]} {lesson_content[0][:5]}', '%Y %m %d %H:%M')
            lesson_end_time = datetime.datetime.strptime(f'2025 {eng_months[date[1]]} {date[0]} {lesson_content[0][8:]}', '%Y %m %d %H:%M')
            lesson_teacher = ' | '.join(lesson_content[1:-1]) if len(lesson_content) > 2 else 'Преподаватель не указан'
            lesson_classroom = lesson_content[-1]

            schedule.append({
                'subject': lesson_subject,
                'teacher': lesson_teacher,
                'classroom': lesson_classroom,
                'start_time': lesson_start_time,
                'end_time': lesson_end_time,
                'type': lesson_type,
                'group': group
            })
    
    return schedule
