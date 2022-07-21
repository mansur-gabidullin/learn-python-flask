from sqlalchemy import Integer, Column, String, ForeignKey, Text, Numeric
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Area(Base):
    __tablename__ = 'area'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255), nullable=False)
    url = Column(String(length=255), unique=True, nullable=False)


class ParentArea(Base):
    __tablename__ = 'parent_area'
    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey("area.id"), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("area.id"), nullable=False)


class Vacancy(Base):
    __tablename__ = 'vacancy'

    id = Column(Integer, primary_key=True)
    url = Column(String(length=255), unique=True, nullable=False)
    name = Column(String(length=255), nullable=False)
    description = Column(Text, nullable=False)
    area_id = Column(Integer, ForeignKey("area.id"), nullable=False)


class VacancySkill(Base):
    __tablename__ = 'vacancy_skill'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255), nullable=False)
    vacancy_id = Column(Integer, ForeignKey("vacancy.id"), nullable=False)


class VacancySalary(Base):
    __tablename__ = 'vacancy_salary'

    id = Column(Integer, primary_key=True)
    salary = Column(Numeric(precision=2), nullable=False)
    vacancy_id = Column(Integer, ForeignKey("vacancy.id"), nullable=False)
