from doctest import debug

from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.user import RegisterForm, LoginForm
from data import db_session
from data.users import User

app = Flask(__name__)
with open('API_KEY.api', 'r') as file:
    API_KEY = file.readline().strip()
app.config['SECRET_KEY'] = API_KEY
login_manager = LoginManager()
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route('/')
def index():
    username = None
    if current_user.is_authenticated:
        username = current_user.name
        print(current_user)
    return render_template('main.html', registered=current_user.is_authenticated, username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/profile')
    else:
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()

            users = db_sess.query(User).all()
            print("\n=== Список пользователей в базе данных ===")
            for u in users:
                print(u)
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('login.html', title='Авторизация', form=form)

@app.route('/register', methods=['GET', 'POST'])
def reqister():
    if current_user.is_authenticated:
        return redirect('/profile')
    else:
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            if len(form.name.data) > 16:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Слишком длинное имя (> 16)")
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                name=form.name.data,
                email=form.email.data,
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                return redirect("/")
            return redirect('/')
        return render_template('register.html', title='Регистрация', form=form)

@app.route('/profile')
@login_required
def profile():
    if current_user.is_authenticated:
        return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

def main():
    db_session.global_init("db/users.db")
    db_session.global_init("db/media_files.db")
    app.run(debug=True)

if __name__ == '__main__':
    main()