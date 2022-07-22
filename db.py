import click
from flask.cli import with_appcontext
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from api import fetch_areas, BASE_URL
from model import Area, Base, ParentArea, VacancySkill, Vacancy, VacancySalary

DATA_BASE_FILE_NAME = 'app.sqlite'

# an Engine, which the Session will use for connection
# resources, typically in module scope
engine = create_engine(f"sqlite:///{DATA_BASE_FILE_NAME}", future=True)

# a sessionmaker(), also in the same scope as the engine
Session = sessionmaker(engine)


def init(app):
    # app.teardown_appcontext(close_db)
    app.cli.add_command(create_db_command)
    app.cli.add_command(seed_db_command)


def create_db():
    Base.metadata.create_all(engine)


@click.command('create-db')
@with_appcontext
def create_db_command():
    """Clear the existing data and create new tables."""
    click.echo('Creating the database.')
    create_db()
    click.echo('The database is created.')


def seed_db():
    click.echo('Fetch areas.')
    areas = fetch_areas()

    # create session and add objects
    with Session.begin() as session:
        for area in areas:
            area_id = area.get('id')
            name = area.get('name')
            url = f'{BASE_URL}/areas/{area_id}'
            parent_id = area.get('parent_id')

            session.add(Area(id=area_id, name=name, url=url))

            if parent_id:
                session.add(ParentArea(area_id=area_id, parent_id=parent_id))
    # inner context calls session.commit(), if there were no exceptions
    # outer context calls session.close()

    click.echo('Seed areas.')


@click.command('seed-db')
@with_appcontext
def seed_db_command():
    """Seed database tables with data from hh.ru."""
    seed_db()
    click.echo('DB seeded.')


def select_areas():
    with Session() as session:
        statement = select(Area)
        return session.scalars(statement).all()


def select_key_skills_by_vacancy_ids(vacancy_ids):
    with Session() as session:
        statement = (
            select(VacancySkill)
                .join(Vacancy, VacancySkill.vacancy_id == Vacancy.id)
                .where(VacancySkill.vacancy_id.in_(vacancy_ids))
        )
        return session.scalars(statement).all()


def select_salaries_by_vacancy_ids(vacancy_ids):
    with Session() as session:
        statement = (
            select(VacancySalary)
                .join(Vacancy, VacancySalary.vacancy_id == Vacancy.id)
                .where(VacancySalary.vacancy_id.in_(vacancy_ids))
        )
        return session.scalars(statement).all()


def select_area_by_id(area_id):
    with Session() as session:
        statement = select(Area).where(Area.id == area_id)
        return session.scalars(statement).one()


def merge(items):
    with Session.begin() as session:
        for item in items:
            session.merge(item)
        session.commit()
