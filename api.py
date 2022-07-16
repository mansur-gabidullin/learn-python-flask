from itertools import chain

import requests
from collections import Counter

BASE_URL = 'https://api.hh.ru'

headers = {
    'User-Agent': 'learn-python-lesson-18 (mansur.gabidullin@gmail.com)'
}


def fetch_areas():
    session = _get_session()
    countries = session.get(f'{BASE_URL}/areas/').json()

    def flat_areas(areas):
        return chain(
            areas,
            chain.from_iterable(
                map(
                    lambda a: flat_areas(a.get('areas')),
                    areas
                )
            )
        )

    return list(flat_areas(countries))


def get_vacancies_info(job_tile, area_id):
    session = _get_session()

    result = _fetch_vacancies_by_job_title_and_area(session, job_tile, area_id)

    items = result.get('items')
    found = result.get('found')
    pages = result.get('pages')

    if found == 0:
        return found, (), (), []

    for page in range(1, pages + 1):
        result = _fetch_vacancies_by_job_title_and_area(session, job_tile, area_id, page)
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


def _get_session():
    session = requests.Session()
    session.headers.update(headers)
    return session


def _fetch_vacancies_by_job_title_and_area(session, job_tile, area_id, page=0, per_page=20):
    return session.get(
        f'{BASE_URL}/vacancies',
        params={'text': f'NAME:{job_tile}', 'area': area_id, 'page': page, 'per_page': per_page}
    ).json()


def _get_salary(v):
    salary = v.get('salary')
    salaries = tuple(filter(bool, [salary.get('from'), salary.get('to')]))
    return sum(salaries) / len(salaries)
