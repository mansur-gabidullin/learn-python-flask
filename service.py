from collections import Counter

from api import fetch_vacancies_by_job_title_and_area, fetch_vacancy_details_by_id
from model import Vacancy, VacancySkill, VacancySalary
import db

menu = (
    ("index", "Главная"),
    ("form", "Форма поиска"),
    ("contacts", "Контакты"),
)


def get_areas():
    return db.select_areas()


def get_area_by_id(area_id):
    return db.select_area_by_id(area_id)


def parse_vacancies_and_save_to_db(job_title, area_id):
    result = _get_vacancies(job_title, area_id)

    if len(result) == 0:
        return []

    vacancies = []
    vacancy_skills = []
    vacancy_salaries = []

    for vacancy in result:
        vacancy_id = vacancy.get('id')
        vacancy_details = fetch_vacancy_details_by_id(vacancy_id)

        vacancy_url = vacancy.get('url')
        name = vacancy_details.get('name')
        description = vacancy_details.get('description')
        area_id = vacancy_details.get('area').get("id")
        key_skills = vacancy_details.get('key_skills')
        salary = vacancy_details.get('salary')

        vacancies.append(Vacancy(id=vacancy_id, url=vacancy_url, name=name, description=description, area_id=area_id))

        if len(key_skills) > 0:
            for skill in key_skills:
                vacancy_skills.append(VacancySkill(name=skill.get('name'), vacancy_id=vacancy_id))

        if salary:
            salaries = tuple(filter(bool, [salary.get('from'), salary.get('to')]))
            vacancy_salaries.append(VacancySalary(vacancy_id=vacancy_id, salary=sum(salaries) / len(salaries)))

    db.merge(vacancies)
    db.merge(vacancy_skills)
    db.merge(vacancy_salaries)

    return vacancies


def get_vacancies_info(vacancy_ids):
    vacancies_count = len(vacancy_ids)

    if vacancies_count == 0:
        return 0, (), (), []

    key_skills = db.select_key_skills_by_vacancy_ids(vacancy_ids)
    skills_count = len(key_skills)
    key_skills_counter = Counter()
    key_skills_counter.update(skill.name for skill in key_skills)
    skills_info = []

    if skills_count > 0:
        for skill, count in key_skills_counter.most_common():
            skills_info.append(f'{skill}: {count} = {(count * 100) / skills_count :.2f}%')

    salaries = db.select_salaries_by_vacancy_ids(vacancy_ids)
    salaries_count = len(salaries)

    # todo: учитывать что зарплата может быть в разной валюте, нужно привести всё к одной валюте
    if salaries_count > 0:
        mean_salary = sum(item.salary for item in salaries) / len(salaries)
    else:
        mean_salary = 0

    return (
        vacancies_count,
        f'{mean_salary:.2f}',
        tuple(key_skills_counter.keys()),
        skills_info
    )


def _get_vacancies(job_title, area_id):
    result = fetch_vacancies_by_job_title_and_area(job_title, area_id)

    items = result.get('items')
    found = result.get('found')
    pages = result.get('pages')

    if found == 0:
        return []

    for page in range(1, pages + 1):
        result = fetch_vacancies_by_job_title_and_area(job_title, area_id, page)
        items.extend(result.get('items'))

    return items
