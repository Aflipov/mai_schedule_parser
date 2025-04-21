import sys
import click
from schedule_downloader.scraper import get_html
from schedule_parser.parser import parse_schedule


def schedule_print(schedule: list):
    timetable = {
        '09:00 – 10:30': 1,
        '10:45 – 12:15': 2,
        '13:00 – 14:30': 3,
        '14:45 – 16:15': 4,
        '16:30 – 18:00': 5
    }
    
    for day in schedule:
        print(f"\n\t{day['date']}\n")
        for lesson in day['lessons_list']:
            print(f'({timetable[lesson['time']]}) {lesson['title']}')
            print(f'{lesson['time']} / {lesson['teacher']} / {lesson['location']}')
            print('\n')


@click.command()
@click.argument('group_number')
@click.argument('week_number', type=int)
def load_schedule(group_number, week_number):
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
            schedule_print(schedule)
        else:
            print("[cli.py]Не удалось распарсить расписание.")
    else:
        print("[cli.py]Не удалось загрузить расписание.")

if __name__ == '__main__':
    load_schedule()
