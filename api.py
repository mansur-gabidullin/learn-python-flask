from itertools import chain

import requests

BASE_URL = 'https://api.hh.ru'

headers = {
    'User-Agent': 'learn-python-lesson-18 (mansur.gabidullin@gmail.com)'
}


def fetch_areas():
    session = get_session()
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


def get_session():
    session = requests.Session()
    session.headers.update(headers)
    return session


def fetch_vacancies_by_job_title_and_area(session, job_tile, area_id, page=0, per_page=20):
    return session.get(
        f'{BASE_URL}/vacancies',
        params={'text': f'NAME:{job_tile}', 'area': area_id, 'page': page, 'per_page': per_page}
    ).json()
