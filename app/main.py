from flask import Flask, request, render_template, redirect, url_for

from model import SessionManager, UserManager
from util import get_secret

app = Flask(__name__,
            static_folder='../static',
            template_folder='../templates')
app.secret_key = get_secret(16)


def authorized_only(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = SessionManager.get_user()
        if not user:
            return redirect(url_for('login'))
        return func(user, *args, **kwargs)

    return wrapper


@app.route('/')
def index():
    user = SessionManager.get_user()
    if user:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))


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
    return redirect(url_for('login'))


@app.route('/dashboard')
@authorized_only
def dashboard(user):
    name = user.display_name
    return render_template('dashboard.html', name=name)
