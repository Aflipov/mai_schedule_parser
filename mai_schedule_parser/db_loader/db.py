from sqlalchemy import create_engine, DateTime, Date, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
import datetime
import logging
from mai_schedule_parser import config
from . import db_models as dbm # импорт моделей бд

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DATABASE_URL = config.DATABASE_URL
ECHO = config.ECHO

engine = create_engine(DATABASE_URL, echo=ECHO)

def create_db() -> None:
    """Создает базу данных и таблицы."""
    try:
        dbm.Base.metadata.create_all(engine)
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
    try:
        session.commit() # Commit сразу после добавления урока
        logger.info(f"Урок '{subject.name}' добавлен.")
    except IntegrityError as e:
        session.rollback() # Откатываем транзакцию
        logger.warning(f"Урок '{subject.name}' уже существует: {e}")


def add_or_update_lesson(session, subject: dbm.Subject, teacher: dbm.Teacher,
                       classroom: dbm.Classroom, start_time: DateTime,
                       end_time: DateTime, lesson_type: str,
                       group: dbm.Group) -> dbm.Lesson: # Возвращаем Lesson
    """Добавляет урок, если он не существует, или обновляет, если существует."""
    lesson = dbm.Lesson(subject=subject, teacher=teacher, classroom=classroom, start_time=start_time, end_time=end_time, lesson_type=lesson_type, group=group)
    session.add(lesson)
    try:
        session.commit()
        logger.info(f"Урок '{subject.name}' добавлен.")
        return lesson # Возвращаем добавленный/обновленный урок
    except IntegrityError as e:
        session.rollback()
        # Урок с такой группой и временем уже существует, нужно обновить
        existing_lesson = session.query(dbm.Lesson).filter(
            dbm.Lesson.group_id == group.id,
            dbm.Lesson.start_time == start_time
        ).first()
        if existing_lesson:
            logger.info(f"Урок для группы '{group.name}' в {start_time} уже существует. Обновляем данные.")
            existing_lesson.subject = subject
            existing_lesson.teacher = teacher
            existing_lesson.classroom = classroom
            existing_lesson.end_time = end_time
            existing_lesson.lesson_type = lesson_type
            session.commit()
            return existing_lesson # Возвращаем обновленный урок
        else:
            logger.error(f"Неожиданная ошибка при добавлении/обновлении урока: {e}")
            return None  # Возвращаем None в случае ошибки


def delete_lessons_by_group_and_date_range(session, group: dbm.Group, start_date: Date, end_date: Date) -> None:
    """Удаляет уроки для указанной группы в заданном диапазоне дат."""
    
    lessons_to_delete = session.query(dbm.Lesson).filter(
        dbm.Lesson.group_id == group.id,
        func.date(dbm.Lesson.start_time) >= start_date,  # Use func.date()
        func.date(dbm.Lesson.start_time) <= end_date   # Use func.date()
    ).all()
    
    for lesson in lessons_to_delete:
        logger.info(f"Удаляем урок: {lesson}")
        session.delete(lesson)
    try:
        session.commit()
        logger.info(f"Уроки для группы '{group.name}' в диапазоне с '{start_date}' по '{end_date}' удалены.")
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка при удалении уроков: {e}")


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


# if __name__ == '__main__':
#     import datetime

#     # Пример использования
#     with get_session() as session:
#         # Добавление данных
#         history = add_subject(session, 'История')
#         math = add_subject(session, 'Математика')
#         ivanov = add_teacher(session, 'Иванов И.И.')
#         petrov = add_teacher(session, 'Петров П.П.')
#         aud_201 = add_classroom(session, 'Аудитория 201')
#         comp_305 = add_classroom(session, 'Компьютерный класс 305')
#         ivt_21 = add_group(session, 'ИВТ-21')
#         fiit_22 = add_group(session, 'ФИИТ-22')
        
#         session.commit()

#         add_lesson(session, history, ivanov, aud_201, datetime.datetime(2024, 1, 29, 10, 0, 0), datetime.datetime(2024, 1, 29, 11, 30, 0), 'Лекция', ivt_21)
#         add_lesson(session, math, petrov, comp_305, datetime.datetime(2024, 1, 29, 11, 30, 0), datetime.datetime(2024, 1, 29, 13, 0, 0), 'Практика', fiit_22)

#         session.commit()
        
#         # Получение данных
#         history_lessons = get_lessons_by_subject(session, 'История')
#         print("Расписание занятий по истории:")
#         for lesson in history_lessons:
#             print(lesson)

#         classroom_schedule = get_classroom_schedule(session, 'Аудитория 201', datetime.date(2024, 1, 29))
#         print("График занятости кабинета 201 на 29 января 2024:")
#         for lesson in classroom_schedule:
#             print(lesson)
    