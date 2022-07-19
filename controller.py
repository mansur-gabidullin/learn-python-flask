import json

from flask import session as flask_session, render_template, redirect, url_for, request

from service import menu, get_vacancies_info, get_areas, get_area_by_id, close_db, init_db_command, db_seed_command


def init_controller(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(db_seed_command)

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
        all_found, mean_salary_info, skills, vacancies_info = get_vacancies_info(job_title, area_id)

        model = {
            'all_found': all_found,
            'mean_salary_info': mean_salary_info,
            'skills': skills,
            'vacancies_info': vacancies_info,
        }

        with open('data.json', 'wt', encoding='utf-8') as file:
            json.dump(model, file)

        flask_session['area_id'] = area_id
        flask_session['job_title'] = job_title

        return redirect(url_for('results'))

    @app.get('/results')
    def results():
        job_title = flask_session.get('job_title')
        area_id = flask_session.get('area_id')

        if not job_title:
            return redirect(url_for('form'))

        with open('data.json', 'rt', encoding='utf-8') as file:
            model = json.load(file)

        if model is None:
            return redirect(url_for('form'))

        area = get_area_by_id(area_id)

        data = {
            'menu': menu,
            'current_endpoint': 'results',
            'model': model,
            'job_title': job_title,
            'area_name': area['name'],
        }

        template = render_template('results.html', **data)

        flask_session.clear()

        return template

    @app.get('/contacts')
    def contacts():
        return render_template('contacts.html', menu=menu, current_endpoint='contacts')
