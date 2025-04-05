import os
import string
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import random
from flask import send_from_directory
from forms.user_form import RegisterForm, LoginForm
from forms.media_form import UploadForm
from data import db_session
from data.users_data import User
from data.media_files import Media

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
    db_sess = db_session.create_session()
    media_entries = db_sess.query(Media).filter(Media.hiden == False).all()
    random.shuffle(media_entries)
    return render_template('main.html', current_user=current_user, title="PicFlow", media_entries=media_entries)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/profile')
    else:
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
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
                                       message="Пароли не совпадают!")
            if len(form.name.data) > 16:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Слишком длинное имя (> 16)!")
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Почта уже зарегестрирована!")
            elif db_sess.query(User).filter(User.name == form.name.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Имя пользователя уже использованно!")
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


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if file:
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1]
            unique_name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
            file_path = os.path.join('media', f"{unique_name}{ext}")

            os.makedirs('media', exist_ok=True)
            file.save(file_path)

            if current_user.is_authenticated:
                author_name = current_user.name
            else:
                author_name = 'Гость'

            db_sess = db_session.create_session()
            media = Media(
                url=unique_name,
                name=form.name.data,
                description=form.description.data,
                autor=author_name,
                hiden=False,
                extension=ext
            )
            db_sess.add(media)
            db_sess.commit()
            return redirect(f'/post/{unique_name}')
    return render_template('upload.html', current_user=current_user, form=form, title="Загрузка")


@app.route('/download/<url>')
def download_media(url):
    media_folder = 'media'
    db_sess = db_session.create_session()
    media_entry = db_sess.query(Media).filter(Media.url == url).first()

    if not media_entry:
        abort(404)

    for file in os.listdir(media_folder):
        if file.startswith(url):
            return send_from_directory(media_folder, file, as_attachment=True)

    abort(404)


@app.route('/post/<url>')
def get_post(url):
    media_folder = 'media'
    db_sess = db_session.create_session()
    media_entry = db_sess.query(Media).filter(Media.url == url).first()

    if not media_entry:
        print("aboba")
        abort(404)

    file_path = None
    for file in os.listdir(media_folder):
        if file.startswith(url):
            file_path = file
            break

    if not file_path:
        print("aboba2")
        abort(404)

    return render_template('post.html', media=media_entry, url=url, ext=media_entry.extension,
                           current_user=current_user, title=media_entry.name)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


def main():
    db_session.global_init("db/instance_data.db")
    app.run(debug=True)


if __name__ == '__main__':
    main()
