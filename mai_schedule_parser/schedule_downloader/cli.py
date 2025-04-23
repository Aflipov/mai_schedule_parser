import sys
import click
# from mai_schedule_parser.schedule_downloader.scraper import get_html
from .scraper import get_html
from mai_schedule_parser.schedule_parser.parser import parse_schedule
from mai_schedule_parser.db_loader import db


def lesson_upload(session, lesson: dict) -> None:
    subject = db.add_subject(session, lesson['subject'])
    teacher = db.add_teacher(session, lesson['teacher'])
    classroom = db.add_classroom(session, lesson['classroom'])
    start_time = lesson['start_time']
    end_time = lesson['end_time']
    type = lesson['type']
    group = db.add_group(session, lesson['group'])
    
    session.commit()
    
    db.add_lesson(session, subject, teacher, classroom, start_time, end_time, type, group)

    session.commit()

def schedule_upload(session, schedule: list[dict]) -> None:
    # 1. Получаем минимальную и максимальную даты из расписания
    dates = set(lesson['start_time'].date() for lesson in schedule)
    start_date = min(dates)
    end_date = max(dates)
    
    group_number: str = schedule[0]['group']
    
    # 2. Удаляем старые записи для группы и диапазона дат
    group = db.add_group(session, group_number)
    db.delete_lessons_by_group_and_date_range(session, group, start_date, end_date)
    
    for lesson in schedule:
        lesson_upload(session, lesson)

def schedule_print(schedule: list[dict]) -> None:
    for lesson in schedule:
        print(f'\n[{lesson['group']}] {lesson['subject']} ({lesson['type']})')
        print(f'{lesson['start_time'].strftime('%d.%m.%Y')}  {lesson['start_time'].strftime('%H:%M')} - {lesson['end_time'].strftime('%H:%M')} | {lesson['classroom']} | {lesson['teacher']}')


@click.command()
@click.argument('group_number', default='М8О-102БВ-24')
@click.argument('week_number', type=int, default='10')
def process_schedule(group_number, week_number):
    """
    Загружает и парсит расписание для заданной группы и недели.\n
    Ожидаются аргументы вида: ["номер группы" "номер недели(1-18)"]\n
    Пример: [М8О-102БВ-24 11]
    """

    if not (1 <= week_number <= 18):
        click.echo('Принимаются значения аргумента WEEK_NUMBER только от 1 до 18 включительно.', err=True)
        sys.exit(1)

    html = get_html(group_number, week_number)
    if html:
        schedule = parse_schedule(html)
        if schedule:
            with db.get_session() as session:
                schedule_upload(session, schedule)
                schedule_print(schedule)
        else:
            print("[cli.py]Не удалось распарсить расписание.")
    else:
        print("[cli.py]Не удалось загрузить расписание.")
