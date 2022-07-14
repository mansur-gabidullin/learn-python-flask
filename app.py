import json

from flask import Flask, session as flask_session, render_template, redirect, url_for, request

from api import get_areas, get_vacancies_info

menu = (
    ("index", "Главная"),
    ("form", "Форма поиска"),
    ("contacts", "Контакты"),
)

# create and configure the app
app = Flask(__name__, instance_relative_config=True)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.get('/')
def index():
    return render_template('index.html', menu=menu, current_endpoint='index')


@app.get('/form')
def form():
    flask_session.clear()

    areas = get_areas()

    with open('areas.json', 'wt', encoding='utf-8') as file:
        json.dump(areas, file)

    return render_template('form.html', menu=menu, current_endpoint='form', areas=areas)


@app.post('/search')
def search():
    job_title = request.form['job_title']
    area_id = request.form['area_id']
    all_found, mean_salary_info, skills, vacancies_info = get_vacancies_info(job_title, area_id)

    model = {
        'all_found': all_found,
        'mean_salary_info': mean_salary_info,
        'skills': skills,
        'vacancies_info': vacancies_info,
    }

    with open('data.json', 'wt', encoding='utf-8') as file:
        json.dump(model, file)

    flask_session['job_title'] = job_title

    with open('areas.json', 'rt', encoding='utf-8') as file:
        areas = json.load(file)

    try:
        flask_session['area_name'] = next(area.get('name') for area in areas if area.get('id') == area_id)
    except StopIteration:
        ...

    return redirect(url_for('results'))


@app.get('/results')
def results():
    job_title = flask_session.get('job_title')
    area_name = flask_session.get('area_name')

    if not job_title or not area_name:
        return redirect(url_for('form'))

    with open('data.json', 'rt', encoding='utf-8') as file:
        model = json.load(file)

    if model is None:
        return redirect(url_for('form'))

    data = {
        'menu': menu,
        'current_endpoint': 'results',
        'model': model,
        'job_title': job_title,
        'area_name': area_name,
    }

    template = render_template('results.html', **data)

    flask_session.clear()

    return template


@app.get('/contacts')
def contacts():
    return render_template('contacts.html', menu=menu, current_endpoint='contacts')
