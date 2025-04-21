from bs4 import BeautifulSoup
import re

def parse_schedule(html_content):
    """
    Парсит HTML расписания и возвращает список словарей, где каждый словарь
    представляет собой одно занятие.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    days = soup.find(class_='step mb-5').find_all(class_='step-item')
    
    if not days:
        print('[parser.py]Тег step mb-5 или step-item не найден')
        return []

    schedule = []
    for day in days:        
        date = day.find(class_="step-content").find('span').text
        lessons = day.select("div[class='mb-4']")

        date = re.sub(r'[\n\t]', '', date)
        date = re.sub(r'[\xa0]', ' ', date)
        
        lessons_list = []
        for lesson in lessons:
            lesson_title = lesson.find('div').text
            lesson_content = [x.text for x in lesson.find('ul').find_all('li')]

            lesson_title = re.sub(r'[\n\t]', '', lesson_title)
            lesson_title = f'{lesson_title[:-2]} ({lesson_title[-2:]})'
            lesson_content = [re.sub(r'[\n\t]', '', item) for item in lesson_content]
            lesson_time = lesson_content[0]
            # lesson_teacher = lesson_content[1] if len(lesson_content) == 3 else 'Преподаватель не указан'
            lesson_teacher = ' / '.join(lesson_content[1:-1]) if len(lesson_content) > 2 else 'Преподаватель не указан'
            lesson_location = lesson_content[-1]

            lessons_list.append({
                'title': lesson_title,
                'time': lesson_time,
                'teacher': lesson_teacher,
                'location': lesson_location,
            })
        
        schedule.append({
            'date': date,
            'lessons_list': lessons_list
        })
    
    return schedule
