import requests
from flask import Flask, request, redirect
import sqlite3
import os

# создание и подключение к базе данных
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# создание таблицы для хранения пользователей
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

app = Flask(__name__)
current_joke = ""


def get_new_joke():
    response = requests.get('https://api.chucknorris.io/jokes/random')
    joke_data = response.json()
    return joke_data['value']


# главная страница со ссылками на авторизацию и вход
@app.route('/')
def index():
    return render_template('action_choice.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (login, email, password) VALUES (?, ?, ?)", (login, email, password))
            conn.commit()
            conn.close()
            return redirect('/my_form')
        except sqlite3.IntegrityError:
            return 'Такая почта уже зарегистрирована на сайте'

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        if user:
            if str(password) == str(user[3]):
                conn.close()
                return redirect('/my_form')
            else:
                conn.close()
                return 'Неверный пароль'
        else:
            conn.close()
            return 'Вы не авторизованы, пожалуйста вернитесь на главную страницу'

    return render_template('login.html')


import os
import uuid

from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, URLField, SelectField
from wtforms.validators import DataRequired, InputRequired

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)
    reqs = db.Column(db.String, nullable=False)
    media = db.Column(db.String, nullable=False)
    about = db.Column(db.Text, nullable=False)
    picture = db.Column(db.String(120), nullable=True)  # изображение может быть не указано


class ProfileForm(FlaskForm):
    picture = FileField('Обновить фото профиля', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    age = StringField('Возраст', validators=[DataRequired()])
    gender = SelectField('Пол', choices=[('male', 'Мужской'), ('female', 'Женский'), ('hide', 'Скрыть')],
                         validators=[InputRequired()])
    reqs = StringField('Ищу', validators=[DataRequired()])
    media = URLField('Соц. сети', validators=[DataRequired()])
    about = TextAreaField('О себе', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    submit = SubmitField('Обновить профиль')


def save_picture(form_picture):
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = str(uuid.uuid4()) + f_ext  # генерация имени файла
    picture_path = os.path.join(app.root_path, 'static', 'profile_pics', picture_fn)
    form_picture.save(picture_path)
    return picture_path


@app.route('/my_form', methods=['GET', 'POST'])
def my_form():
    form = ProfileForm()
    profile = None  # переменная для хранения данных профиля
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            picture_url = url_for('static', filename='profile_pics/' + os.path.basename(picture_file))
        else:
            picture_url = url_for('static', filename='profile_pics/' + 'None.png')  # путь к изображению по умолчанию
        profile = Profile(name=form.name.data, age=form.age.data, gender=form.gender.data,
                          media=form.media.data, reqs=form.reqs.data, about=form.about.data,
                          picture=picture_url)
        db.session.add(profile)
        db.session.commit()

    # if not profile: #убрала, потому что анкеты все равно к акку не привязаны
    #    profile = Profile.query.order_by(Profile.id.desc()).first()  # загрузка последнего созданного профиля

    image_file = profile.picture if profile and profile.picture else url_for('static',
                                                                             filename='profile_pics/' + 'None.png')
    return render_template('form_creation.html', form=form, profile=profile, image_file=image_file)


@app.route('/all_forms')
def all_forms():
    profiles = Profile.query.all()
    joke = generate_joke()
    return render_template('all_forms.html', profiles=profiles, joke=joke)


@app.route('/generate_joke', methods=['GET'])
def generate_joke():
    global current_joke
    current_joke = get_new_joke()
    return current_joke


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
