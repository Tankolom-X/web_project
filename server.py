import datetime
import os
import random
import secrets
from tkinter import Tk
from tkinter.filedialog import askopenfilename

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, redirect, session, make_response, abort, request, current_app
from werkzeug.utils import secure_filename

from data import db_session
from data.users import User
from data.news import News
from forms.user import RegisterForm
from forms.loginform import LoginForm
from forms.news import NewsForm
from forms.orderform import OrderForm
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/blogs.db")
    app.run(debug=True)


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True).order_by(News.created_date.desc())
    return render_template('index.html', news=news)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


# выпадающее меню
@app.route('/doors')
def doors():
    return render_template('doors.html')


@app.route('/stairs')
def stairs():
    return render_template('stairs.html')


@app.route('/bar')
def bar():
    return render_template('bar.html')


@app.route('/furniture')
def furniture():
    return render_template('furniture.html')


@app.route('/usual')
def usual():
    return render_template('usual.html')


# отзывы и заказы
@app.route('/order', methods=['GET', 'POST'])
def order():
    input_data = None
    file_name_abc = ""
    file = None
    flag = False
    if request.method == 'POST':
        if 'image' not in request.files:
            return 'Нет файла в запросе'
        file = request.files['image']
        if file:
            print(file)
            filename = file.filename
            for i in filename:
                if i == "." or flag:
                    file_name_abc += i
                    flag = True
            save_path = os.path.join('images_email', "image_2_email" + file_name_abc)
            if not os.path.exists('images_email'):
                os.makedirs('images_email')
            file.save(save_path)
            with open("files_flag/flag.txt", 'w') as file:
                file.write('_')
        input_data = request.form['login']
    if input_data != "":
        # Email configuration        sender_email = "orderwood56@internet.ru"
        receiver_email = "orderwood56@internet.ru"
        sender_password = "m3Z-DQ9-nbB-gWC"
        sender_email = "orderwood56@internet.ru"
        with open('files_order/file_number_of_order.txt', 'r') as file:
            number = int(file.read().strip())
        new_number = number + 1
        with open('files_order/file_number_of_order.txt', 'w') as file:
            file.write(str(new_number))
        subject = f'Заказ №{number}'
        print(input_data)
        message = f"номер заказчика/цы: {input_data}"
        msc_login_user = "orderwood56@internet.ru"
        msc_login_pass = 'y3n8H64LrmDevpT3EDbw' # Пароль для приложения

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        if os.path.exists("files_flag/flag.txt"):
            with open(f'images_email/{os.listdir("images_email")[0]}', 'rb') as f:
                image = MIMEImage(f.read())
                image.add_header('Content-Disposition', 'attachment', filename='image.jpg')
                msg.attach(image)

        smtp_server = 'smtp.mail.ru'
        smtp_port = 465

        try:
            server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
            server.login(msc_login_user, msc_login_pass)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
            print('Email sent successfully')
            if os.path.exists("files_flag/flag.txt"):
                os.remove("files_flag/flag.txt")
            if os.path.exists("images_email/image_2_email.jpg"):
                os.remove("images_email/image_2_email.jpg")
            if os.path.exists("images_email/image_2_email.png"):
                os.remove("images_email/image_2_email.png")
            if os.path.exists("images_email/image_2_email.jpeg"):
                os.remove("images_email/image_2_email.jpeg")
            if os.path.exists("images_email/image_2_email.raw"):
                os.remove("images_email/image_2_email.raw")
        except Exception as e:
            print('Email not sent. An error occurred:', str(e))
        finally:
            server.quit()
    return render_template('order.html')


@app.route('/reviews')
def reviews():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True).order_by(News.created_date.desc())
    import locale
    locale.setlocale(
        category=locale.LC_ALL,
        locale="Russian"  # Note: do not use "de_DE" as it doesn't work
    )

    return render_template('reviews.html', news=news)






@app.route('/create_feedback', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.content = form.content.data
        news.is_private = form.is_private.data
        import uuid
        if form.picture.data:
            picture_file = request.files['picture']
            if picture_file:
                # Генерируем уникальное имя файла
                picture_fn = str(uuid.uuid4()) + secure_filename(picture_file.filename)
                picture_path = os.path.join(app.static_folder, 'AddPicture', picture_fn)
                os.makedirs(os.path.dirname(picture_path), exist_ok=True)
                picture_file.save(picture_path)
                news.image_file = picture_fn
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/reviews')
    return render_template('create_feedback.html',
                           form=form)


@app.route('/create_feedback/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            if news.image_file:
                image_path = os.path.join(app.root_path, 'static', 'AddPicture', news.image_file)
                if os.path.exists(image_path):
                    os.remove(image_path)

            # Загрузка и сохранение нового изображения
            if form.picture.data:
                picture_file = request.files['picture']
                if picture_file:
                    picture_fn = secure_filename(picture_file.filename)
                    picture_path = os.path.join(app.static_folder, 'AddPicture', picture_fn)
                    os.makedirs(os.path.dirname(picture_path), exist_ok=True)
                    picture_file.save(picture_path)
                    news.image_file = picture_fn
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/reviews')
        else:
            abort(404)
    return render_template('create_feedback.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/create_feedback_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        image_path = os.path.join("static/AddPicture", news.image_file)
        if os.path.exists(image_path):
            os.remove(image_path)
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/reviews')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


if __name__ == '__main__':
    main()
