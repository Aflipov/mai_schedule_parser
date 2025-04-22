from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Subject(Base):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    lessons = relationship("Lesson", back_populates="subject") # Связь с уроками

    def __repr__(self):
        return f"<Subject(name='{self.name}')>"


class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    # department = Column(String, nullable=True)
    lessons = relationship("Lesson", back_populates="teacher") # Связь с уроками

    def __repr__(self):
        return f"<Teacher(name='{self.name}')>"

class Classroom(Base):
    __tablename__ = 'classrooms'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    # capacity = Column(Integer, nullable=True)
    # location = Column(String, nullable=True)
    lessons = relationship("Lesson", back_populates="classroom") # Связь с уроками

    def __repr__(self):
        return f"<Classroom(name='{self.name}')>"


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    lessons = relationship("Lesson", back_populates="group") # Связь с уроками (одна группа для одного урока)

    def __repr__(self):
        return f"<Group(name='{self.name}')>"


class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    classroom_id = Column(Integer, ForeignKey('classrooms.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    lesson_type = Column(String, nullable=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=True)  # Урок только для одной группы
    # description = Column(String, nullable=True)

    subject = relationship("Subject", back_populates="lessons") # Связь с предметом
    teacher = relationship("Teacher", back_populates="lessons") # Связь с преподавателем
    classroom = relationship("Classroom", back_populates="lessons") # Связь с кабинетом
    group = relationship("Group", back_populates="lessons") # Связь с группой (одна группа для одного урока)

    def __repr__(self):
        return f"<Lesson(subject='{self.subject.name}', start_time='{self.start_time}')>"