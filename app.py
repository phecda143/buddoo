from flask import Flask, request, render_template, redirect
import sqlite3

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


# главная страница со ссылками на авторизацию и вход
@app.route('/')
def index():
    return render_template('index.html')


# авторизация
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
            return 'successful'
        except sqlite3.IntegrityError:
            return 'Такая почта уже зарегистрирована на сайте'

    return render_template('register.html')


# вход
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
                return 'successful'
            else:
                conn.close()
                return 'Неверный пароль'
        else:
            conn.close()
            return 'Вы не авторизованы, пожалуйста вернитесь на главную страницу'

    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)