from flask import session, render_template, redirect, url_for, request
from service import menu, get_vacancies_info, get_areas, parse_vacancies_and_save_to_db, get_area_by_id


def init(app):
    @app.get('/')
    def index():
        return render_template('index.html', menu=menu, current_endpoint='index')

    @app.get('/form')
    def form():
        areas = get_areas()
        return render_template('form.html', menu=menu, current_endpoint='form', areas=areas)

    @app.post('/search')
    def search():
        job_title = request.form['job_title']
        area_id = request.form['area_id']

        vacancies = parse_vacancies_and_save_to_db(job_title, area_id)

        session['vacancy_ids'] = list(vacancy.id for vacancy in vacancies)
        session['area_id'] = area_id
        session['job_title'] = job_title

        return redirect(url_for('results'))

    @app.get('/results')
    def results():
        job_title = session.get('job_title')
        area_id = session.get('area_id')

        if not job_title:
            return redirect(url_for('form'))

        vacancy_ids = session['vacancy_ids']
        all_found, mean_salary_info, skills, skills_info = get_vacancies_info(vacancy_ids)

        model = {
            'all_found': all_found,
            'mean_salary_info': mean_salary_info,
            'skills': skills,
            'skills_count': len(skills),
            'skills_info': skills_info,
        }

        if model is None:
            return redirect(url_for('form'))

        area = get_area_by_id(area_id)

        data = {
            'menu': menu,
            'current_endpoint': 'results',
            'model': model,
            'job_title': job_title,
            'area_name': area.name,
        }

        template = render_template('results.html', **data)
        session.clear()

        return template

    @app.get('/contacts')
    def contacts():
        return render_template('contacts.html', menu=menu, current_endpoint='contacts')
