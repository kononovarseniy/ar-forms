from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__,
            static_folder='../static',
            template_folder='../templates')


@app.route('/')
def index():
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    name = request.args.get("name", "World")
    return render_template('dashboard.html', name=name)
