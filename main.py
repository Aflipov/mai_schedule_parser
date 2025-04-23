import sys
sys.path.append('..')
from mai_schedule_parser.schedule_downloader.cli import process_schedule

if __name__ == '__main__':
    process_schedule()  # Вызываем функцию CLI для загрузки расписания
