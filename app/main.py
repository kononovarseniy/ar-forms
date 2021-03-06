import io
from datetime import datetime
from functools import wraps

from flask import Flask, request, render_template, redirect, url_for, send_file

from api import execute_api_method
from model import SessionManager, UserManager, FormManager, FormStatisticsManager, SubmissionManager
from util.json import JSONEncoder
from util.security import get_secret

app = Flask(__name__,
            static_folder='../static',
            template_folder='../templates')
app.secret_key = get_secret(16, 'secret.key')
app.json_encoder = JSONEncoder


def authorized_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = SessionManager.get_user()
        if not user:
            return redirect(url_for('login'))
        return func(user, *args, **kwargs)

    return wrapper


@app.errorhandler(404)
def page_not_found(error):
    user = SessionManager.get_user()
    return render_template('page_not_found.html', user=user), 404


@app.route('/')
def about():
    user = SessionManager.get_user()
    return render_template('about.html', user=user)


@app.route('/api/<method>')
def api(method):
    return execute_api_method(method)


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        user = UserManager.login(
            request.form['login'],
            request.form['password'])

        if user:
            SessionManager.start_session(user)
            return redirect(url_for('dashboard'))
        else:
            error = "Incorrect username or password"
    else:
        user = SessionManager.get_user()
        if user:
            return redirect(url_for('dashboard'))

    return render_template('login.html', error=error)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    error = None
    if request.method == 'POST':
        user = UserManager.register(
            request.form['login'],
            request.form['display_name'],
            request.form['password'])

        if user:
            SessionManager.start_session(user)
            return redirect(url_for('dashboard'))
        else:
            error = "Login is already used"
    else:
        user = SessionManager.get_user()
        if user:
            return redirect(url_for('dashboard'))

    return render_template('signup.html', error=error)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    SessionManager.stop_session()
    return redirect(url_for('about'))


@app.route('/dashboard')
@authorized_only
def dashboard(user):
    forms = list(FormManager.get_forms_by_user(user, user))
    return render_template('dashboard.html', user=user, forms=forms)


@app.route('/results')
@authorized_only
def results(user):
    submissions = list(SubmissionManager.get_submissions_by_user(user))
    return render_template('results.html', user=user, submissions=submissions, today=datetime.today().date())


@app.route('/edit_form')
@authorized_only
def edit_form(user):
    return render_template('edit_form.html', user=user)


@app.route('/fill_form')
@authorized_only
def fill_form(user):
    return render_template('fill_form.html', user=user)


@app.route('/get_statistics')
@authorized_only
def get_statistics(user):
    form_id = int(request.args['form_id'])
    f = io.BytesIO()
    name = FormStatisticsManager.create_zip_file(user, form_id, f)
    f.seek(0)
    return send_file(f, as_attachment=True,
                     attachment_filename=name,
                     mimetype='application/zip')
