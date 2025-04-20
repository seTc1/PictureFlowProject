import os
import string
from doctest import debug
import re
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

application = Flask(__name__, static_folder='static', static_url_path='/static')
with open('API_KEY.api', 'r') as file:
    API_KEY = file.readline().strip()
application.config['SECRET_KEY'] = API_KEY
application.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
login_manager = LoginManager()
login_manager.init_app(application)

BANNED_IPS = []

@application.before_request
def block_banned_ips():
    client_ip = request.remote_addr
    if client_ip in BANNED_IPS:
        abort(403)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@application.teardown_appcontext
def shutdown_session(exception=None):
    db_session.Session.remove()

from flask import jsonify

@application.route('/')
def index():
    db_sess = db_session.create_session()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 40, type=int)
        media_query = db_sess.query(Media).filter(Media.hiden_post == False).order_by(Media.created_date.desc())
        media_entries = media_query.offset((page - 1) * per_page).limit(per_page).all()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            media_list = [{
                'post_url': media.post_url,
                'post_name': media.post_name,
                'file_extension': media.file_extension,
                'autor_name': media.autor_name,
            } for media in media_entries]
            return jsonify({
                'media': media_list,
                'has_next': len(media_entries) == per_page
            })
        else:
            return render_template('main.html',
                                 current_user=current_user,
                                 title="PicFlow",
                                 media_entries=media_entries)
    finally:
        db_sess.close()

@application.route('/delete/<url>', methods=['POST'])
@login_required
def delete_post(url):
    db_sess = db_session.create_session()
    media_entry = db_sess.query(Media).filter(Media.post_url == url).first()

    if not media_entry:
        abort(404)

    if current_user.name != media_entry.autor_name and current_user.name != "setc1":
        abort(403)

    media_folder = 'media'
    for file in os.listdir(media_folder):
        if file.startswith(url):
            os.remove(os.path.join(media_folder, file))
            break

    db_sess.delete(media_entry)
    db_sess.commit()
    return redirect('/')

@application.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/profile')

    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        try:
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        finally:
            db_sess.close()
    return render_template('login.html', title='Авторизация', form=form)

@application.route('/register', methods=['GET', 'POST'])
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
            if not re.match(r'^[a-zA-Z0-9_\.:\/]+$', form.name.data):
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Имя содержит недопустимые символы")
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

@application.route('/profile/<username>')
def profile(username):
    db_sess = db_session.create_session()
    try:
        is_owner = current_user.is_authenticated and current_user.name == username
        if is_owner:
            media_entries = db_sess.query(Media).filter(Media.autor_name == username).order_by(Media.created_date.desc()).all()
        else:
            media_entries = db_sess.query(Media).filter(Media.autor_name == username, Media.hiden_post == False).order_by(Media.created_date.desc()).all()
        user_data = db_sess.query(User).filter(User.name == username).first()
        if not user_data:
            abort(404)
        return render_template('profile.html',
                               current_user=current_user,
                               title=f"Профиль пользователя {username}",
                               media_entries=media_entries)
    finally:
        db_sess.close()

@application.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        description = form.description.data.strip()
        file_name = form.file.data.filename

        if len(name) > 20:
            return render_template('upload.html', current_user=current_user, form=form,
                                   title="Загрузка публикации", message="Название не должно превышать 20 символов")

        if len(description) > 200:
            return render_template('upload.html', current_user=current_user, form=form,
                                   title="Загрузка публикации", message="Описание не должно превышать 200 символов")
        if not file_name.endswith((".jpg", ".png", ".jpeg")):
            return render_template('upload.html', current_user=current_user, form=form,
                                   title="Загрузка публикации", message="Не поддерживаемое расширение файла")

        if not name:
            name = "Нет названия"
        if not description:
            description = "Нет описания"

        file = form.file.data
        if file:
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1]
            unique_name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
            file_path = os.path.join('media', f"{unique_name}{ext}")

            os.makedirs('media', exist_ok=True)
            file.save(file_path)

            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    width, height = img.size
                    if width > 4096 or height > 4096:
                        os.remove(file_path)
                        return render_template('upload.html', current_user=current_user, form=form,
                                            title="Загрузка публикации", message="Размер изображения превышает 4096x4096 пикселей")
            except:
                os.remove(file_path)
                return render_template('upload.html', current_user=current_user, form=form,
                                    title="Загрузка публикации", message="Неверный формат изображения")

            author_name = current_user.name if current_user.is_authenticated else 'Гость'
            author_ip = request.remote_addr or 'Неизвестно'

            db_sess = db_session.create_session()
            media = Media(
                post_url=unique_name,
                post_name=name,
                post_description=description,
                autor_name=author_name,
                autor_ip=author_ip,
                hiden_post=form.is_private.data if current_user.is_authenticated else False,
                file_extension=ext
            )
            db_sess.add(media)
            db_sess.commit()
            return redirect(f'/post/{unique_name}')
    return render_template('upload.html', current_user=current_user, form=form, title="Загрузка публикации")

@application.route('/download/<url>')
def download_media(url):
    media_folder = 'media'
    db_sess = db_session.create_session()
    try:
        media_entry = db_sess.query(Media).filter(Media.post_url == url).first()
        if not media_entry:
            abort(404)

        for file in os.listdir(media_folder):
            if file.startswith(url):
                return send_from_directory(media_folder, file, as_attachment=True)
        abort(404)
    finally:
        db_sess.close()

@application.route('/post/<url>')
def get_post(url):
    media_folder = 'media'
    db_sess = db_session.create_session()
    media_entry = db_sess.query(Media).filter(Media.post_url == url).first()

    if not media_entry:
        abort(404)

    file_path = None
    for file in os.listdir(media_folder):
        if file.startswith(url):
            file_path = file
            break

    if not file_path:
        abort(404)

    return render_template('post.html', media=media_entry, url=url, ext=media_entry.file_extension,
                           current_user=current_user, title=media_entry.post_name)

@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@application.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


def main():
    db_session.global_init("db/instance_data.db")
    application.run(debug=True)


if __name__ == '__main__':
    main()
