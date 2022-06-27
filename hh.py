from collections import Counter
from pprint import pprint

import requests

BASE_URL = 'https://api.hh.ru'

headers = {
    'User-Agent': 'learn-python-lesson-18 (mansur.gabidullin@gmail.com)'
}

s = requests.Session()
s.headers.update(headers)

print('Выберите город:')
print('1. Москва')
print('2. Санкт-Петербург')
print('3. Казань')
print()

match input('Укажите город: '):
    case '1':
        area_id = 1
    case '2':
        area_id = 2
    case '3':
        area_id = 88
    case _:
        area_id = None
        exit(1)

job_tile = input('Укажите название вакансии: ')


def fetch_vacancies_by_job_title_and_area(job_tile, area_id, page=0, per_page=20):
    response = s.get(
        f'{BASE_URL}/vacancies',
        params={'text': f'NAME:{job_tile}', 'area': area_id, 'page': page, 'per_page': per_page}
    )

    if response.status_code < 200 or response.status_code >= 300:
        exit(1)

    return response


result = fetch_vacancies_by_job_title_and_area(job_tile, area_id).json()

items = result.get('items')
found = result.get('found')
pages = result.get('pages')

for page in range(1, pages + 1):
    result = fetch_vacancies_by_job_title_and_area(job_tile, area_id, page).json()
    items.extend(result.get('items'))

print('\n1. Сколько всего вакансий')
print(found)

print('\n2. Средняя заработная плата')

items_with_salary = list(filter(lambda v: v.get('salary') is not None, items))


def get_salary(v):
    salary = v.get('salary')
    salaries = tuple(filter(bool, [salary.get('from'), salary.get('to')]))
    return sum(salaries) / len(salaries)


print(
    f'{sum(get_salary(v) for v in items_with_salary) / len(items_with_salary) :.2f} \
    {items_with_salary[0].get("salary").get("currency")}'
)

print('\n3. Все требования к данному типу вакансий')
urls = tuple(v.get('url') for v in items)
vacancies_details = []
for url in urls:
    vacancies_details.append(s.get(url).json())

key_skills_counter = Counter()
for details in vacancies_details:
    key_skills_counter.update(set(map(lambda skill: skill.get('name').lower(), details.get('key_skills'))))

pprint(tuple(key_skills_counter.keys()))

print('\n4. В скольких вакансиях указано данное требование (сортируем по убыванию)')
vacancies_count = len(vacancies_details)
print('всего вакансий:', vacancies_count)

for skill, count in key_skills_counter.most_common():
    print(f'{skill}: {count} = {(count * 100) / vacancies_count :.2f}%')
