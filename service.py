from collections import Counter

from api import get_session, fetch_vacancies_by_job_title_and_area
from db import get_areas, get_area_by_id, close_db, init_db_command, db_seed_command

menu = (
    ("index", "Главная"),
    ("form", "Форма поиска"),
    ("contacts", "Контакты"),
)


def get_vacancies_info(job_tile, area_id):
    session = get_session()

    result = fetch_vacancies_by_job_title_and_area(session, job_tile, area_id)

    items = result.get('items')
    found = result.get('found')
    pages = result.get('pages')

    if found == 0:
        return found, (), (), []

    for page in range(1, pages + 1):
        result = fetch_vacancies_by_job_title_and_area(session, job_tile, area_id, page)
        items.extend(result.get('items'))

    items_with_salary = list(filter(lambda v: v.get('salary') is not None, items))

    urls = tuple(v.get('url') for v in items)
    vacancies_details = []

    for url in urls:
        vacancies_details.append(session.get(url).json())

    key_skills_counter = Counter()

    for details in vacancies_details:
        key_skills_counter.update(set(map(lambda skill: skill.get('name').lower(), details.get('key_skills'))))

    vacancies_count = len(vacancies_details)

    vacancies_info = []
    for skill, count in key_skills_counter.most_common():
        vacancies_info.append(f'{skill}: {count} = {(count * 100) / vacancies_count :.2f}%')

    return (
        found,
        (
            f'{sum(_get_salary(v) for v in items_with_salary) / len(items_with_salary) :.2f} \
            {items_with_salary[0].get("salary").get("currency")}'
        ),
        tuple(key_skills_counter.keys()),
        vacancies_info
    )


def _get_salary(v):
    salary = v.get('salary')
    salaries = tuple(filter(bool, [salary.get('from'), salary.get('to')]))
    return sum(salaries) / len(salaries)
