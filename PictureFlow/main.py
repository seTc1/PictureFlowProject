from doctest import debug

from flask import Flask, render_template
from data import db_session

app = Flask(__name__)
with open('API_KEY.api', 'r') as file:
    API_KEY = file.readline().strip()
app.config['SECRET_KEY'] = API_KEY


def main():
    db_session.global_init("db/users.db")
    app.run(debug=True)


@app.route('/')
def index():
    return render_template('main.html')

@app.route('/login')
def login():
    return render_template('register.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    main()