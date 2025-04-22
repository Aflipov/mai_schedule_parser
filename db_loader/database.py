from sqlalchemy import create_engine, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
import logging
# import config
import db_models as dbm # импорт моделей бд

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Настройка подключения к БД
DATABASE_URL = "sqlite:///schedule.db"  # Или ваша строка подключения к PostgreSQL, MySQL и т.д.
ECHO = True # True для вывода SQL запросов в консоль

# DATABASE_URL = config.DATABASE_URL # "sqlite:///schedule.db" or "postgresql://user:password@host:port/database"
# ECHO = config.ECHO # True для вывода SQL запросов в консоль

engine = create_engine(DATABASE_URL, echo=ECHO)

def create_db() -> None:
    """Создает базу данных и таблицы."""
    try:
        dbm.Base.metadata.create_all(engine)  # Используем Base из db_models.py
        logger.info("База данных успешно создана.")
    except Exception as e:
        logger.error(f"Ошибка при создании базы данных: {e}")

Session = sessionmaker(bind=engine)

@contextmanager
def get_session():
    """Context manager для управления сессией."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка при работе с базой данных: {e}")
        raise
    finally:
        session.close()

create_db()

# Функции для добавления данных
def add_subject(session, name: str) -> dbm.Subject:
    existing_subject = session.query(dbm.Subject).filter_by(name=name).first()
    if existing_subject:
        logger.info(f"Предмет '{name}' уже существует.")
        return existing_subject
    subject = dbm.Subject(name=name)
    session.add(subject)
    logger.info(f"Предмет '{name}' добавлен.")
    return subject

def add_teacher(session, name: str) -> dbm.Teacher:
    existing_teacher = session.query(dbm.Teacher).filter_by(name=name).first()
    if existing_teacher:
        logger.info(f"Преподаватель '{name}' уже существует.")
        return existing_teacher
    teacher = dbm.Teacher(name=name)
    session.add(teacher)
    logger.info(f"Преподаватель '{name}' добавлен.")
    return teacher

def add_classroom(session, name: str) -> dbm.Classroom:
    existing_classroom = session.query(dbm.Classroom).filter_by(name=name).first()
    if existing_classroom:
        logger.info(f"Кабинет '{name}' уже существует.")
        return existing_classroom
    classroom = dbm.Classroom(name=name)
    session.add(classroom)
    logger.info(f"Кабинет '{name}' добавлен.")
    return classroom

def add_group(session, name: str) -> dbm.Group:
    existing_group = session.query(dbm.Group).filter_by(name=name).first()
    if existing_group:
        logger.info(f"Группа '{name}' уже существует.")
        return existing_group
    group = dbm.Group(name=name)
    session.add(group)
    logger.info(f"Группа '{name}' добавлена.")
    return group

def add_lesson(session, subject: dbm.Subject, teacher: dbm.Teacher,
               classroom: dbm.Classroom, start_time: DateTime,
               end_time: DateTime, lesson_type: str,
               group: dbm.Group) -> None:
    lesson = dbm.Lesson(subject=subject, teacher=teacher, classroom=classroom, start_time=start_time, end_time=end_time, lesson_type=lesson_type, group=group)
    session.add(lesson)
    logger.info(f"Урок '{subject.name}' добавлен.")


# Функции для получения данных
def get_lessons_by_subject(session, subject_name):
    return session.query(dbm.Lesson).join(dbm.Subject).filter(dbm.Subject.name == subject_name).all()

def get_classroom_schedule(session, classroom_name, date):
    start_of_day = datetime.datetime.combine(date, datetime.time.min)
    end_of_day = datetime.datetime.combine(date, datetime.time.max)
    return session.query(dbm.Lesson).join(dbm.Classroom).filter(dbm.Classroom.name == classroom_name, dbm.Lesson.start_time.between(start_of_day, end_of_day)).all()

def get_all_lessons(session):
    return session.query(dbm.Lesson).all()

def update_lesson(session, lesson_id, data) -> None:
    lesson = session.query(dbm.Lesson).get(lesson_id)
    if lesson:
        for key, value in data.items():
            setattr(lesson, key, value)
        logger.info(f"Урок с ID '{lesson_id}' обновлен.")
    else:
        logger.warning(f"Урок с ID '{lesson_id}' не найден.")

def delete_lesson(session, lesson_id) -> None:
    lesson = session.query(dbm.Lesson).get(lesson_id)
    if lesson:
        session.delete(lesson)
        logger.info(f"Урок с ID '{lesson_id}' удален.")
    else:
        logger.warning(f"Урок с ID '{lesson_id}' не найден.")


if __name__ == '__main__':
    import datetime

    # Пример использования
    with get_session() as session:
        # Добавление данных
        history = add_subject(session, 'История')
        math = add_subject(session, 'Математика')
        ivanov = add_teacher(session, 'Иванов И.И.')
        petrov = add_teacher(session, 'Петров П.П.')
        aud_201 = add_classroom(session, 'Аудитория 201')
        comp_305 = add_classroom(session, 'Компьютерный класс 305')
        ivt_21 = add_group(session, 'ИВТ-21')
        fiit_22 = add_group(session, 'ФИИТ-22')
        
        session.commit()

        add_lesson(session, history, ivanov, aud_201, datetime.datetime(2024, 1, 29, 10, 0, 0), datetime.datetime(2024, 1, 29, 11, 30, 0), 'Лекция', ivt_21)
        add_lesson(session, math, petrov, comp_305, datetime.datetime(2024, 1, 29, 11, 30, 0), datetime.datetime(2024, 1, 29, 13, 0, 0), 'Практика', fiit_22)

        session.commit()
        
        # Получение данных
        history_lessons = get_lessons_by_subject(session, 'История')
        print("Расписание занятий по истории:")
        for lesson in history_lessons:
            print(lesson)

        classroom_schedule = get_classroom_schedule(session, 'Аудитория 201', datetime.date(2024, 1, 29))
        print("График занятости кабинета 201 на 29 января 2024:")
        for lesson in classroom_schedule:
            print(lesson)
    
    
    #Примеры добавления данных !!устаревшее

    # # Создание предметов
    # history = dbm.Subject(name='История')
    # math = dbm.Subject(name='Математика')
    # session.add_all([history, math])
    # session.commit()

    # # Создание преподавателей
    # ivanov = dbm.Teacher(name='Иванов И.И.', department='Кафедра истории')
    # petrov = dbm.Teacher(name='Петров П.П.', department='Кафедра математики')
    # session.add_all([ivanov, petrov])
    # session.commit()

    # # Создание кабинетов
    # aud_201 = dbm.Classroom(name='Аудитория 201', capacity=30, location='Корпус 1, 2 этаж')
    # comp_305 = dbm.Classroom(name='Компьютерный класс 305', capacity=20, location='Корпус 2, 3 этаж')
    # session.add_all([aud_201, comp_305])
    # session.commit()

    # # Создание групп
    # ivt_21 = dbm.Group(name='ИВТ-21')
    # фиит_22 = dbm.Group(name='ФИИТ-22')
    # session.add_all([ivt_21, фиит_22])
    # session.commit()

    # # Создание уроков
    # lesson1 = dbm.Lesson(
    #     subject_id=history.id,
    #     teacher_id=ivanov.id,
    #     classroom_id=aud_201.id,
    #     start_time=datetime.datetime(2024, 1, 29, 10, 0, 0),  # 29 января 2024, 10:00
    #     end_time=datetime.datetime(2024, 1, 29, 11, 30, 0),
    #     lesson_type='Лекция',
    #     group_id=ivt_21.id,
    #     description='Лекция по истории России'
    # )
    # lesson2 = dbm.Lesson(
    #     subject_id=math.id,
    #     teacher_id=petrov.id,
    #     classroom_id=comp_305.id,
    #     start_time=datetime.datetime(2024, 1, 29, 11, 30, 0),  # 29 января 2024, 11:30
    #     end_time=datetime.datetime(2024, 1, 29, 13, 0, 0),
    #     lesson_type='Практика',
    #     group_id=фиит_22.id,
    #     description='Практическое занятие по математическому анализу'
    # )
    # session.add_all([lesson1, lesson2])
    # session.commit()

    # #Примеры запросов

    # # Расписание занятий по истории
    # history_lessons = session.query(dbm.Lesson).join(dbm.Subject).filter(dbm.Subject.name == 'История').all()
    # print("Расписание занятий по истории:")
    # for lesson in history_lessons:
    #     print(lesson)

    # # График занятости кабинета 201 на 29 января 2024
    # classroom_schedule = session.query(dbm.Lesson).join(dbm.Classroom).filter(dbm.Classroom.name == 'Аудитория 201', dbm.Lesson.start_time.between(datetime.datetime(2024, 1, 29, 0, 0, 0), datetime.datetime(2024, 1, 29, 23, 59, 59))).all()
    # print("График занятости кабинета 201 на 29 января 2024:")
    # for lesson in classroom_schedule:
    #     print(lesson)

    # session.close()
