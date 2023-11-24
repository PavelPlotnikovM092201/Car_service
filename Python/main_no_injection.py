# Стандартные библиотеки
import os
import re
import json

# Библиотека pymysql для подключения к MYSQL
import pymysql
from pymysql.converters import escape_string

# Библиотека flask для создание запросов к веб серверу
from flask import Flask, render_template, request


app = Flask(__name__, template_folder='C:\\Users\\Morze\\Desktop\\Web\\site_mtuci\\')


def get_config_connect() -> dict:
    """
    Получение конфига для БД
    :return:
    """
    json_path = os.path.dirname(os.path.abspath(__file__))
    with open(rf'{json_path}\Config.json', encoding='utf8') as f:
        file_content = f.read()
        params = json.loads(file_content)
        f.close()
        config = params["Database"]
    return config


config = get_config_connect()


@app.route("/", methods=['POST', 'GET'])
def home():
    return render_template("vxod.html")


@app.route('/site_data/', methods=['POST', 'GET'])
def login() -> None:
    """
    Авторизация пользователя
    :return: None
    """
    # Получение переменных из HTML формы регистрации
    """данный метод escape_string() экранирует ' и ", что не дает сделать sql-инъекцию"""
    email = escape_string(request.form['email'])
    password = escape_string(request.form['psw'])

    print(email, password)
    # Подлкючение к БД Mysql
    connection = pymysql.connect(**config, cursorclass=pymysql.cursors.DictCursor, charset='utf8', use_unicode=True)
    with connection.cursor() as cursor:
        select_movies_query = "SELECT * FROM users WHERE email = %s AND password = %s"
        val = (email, password)
        """Передачи в sql через аргументы не дает выполнить sql-инъекцию"""
        cursor.execute(select_movies_query, val)
        result = cursor.fetchall()

        # Проверка сущетсвования пользователя в БД
        if not result:
            print("Кортеж пустой")
            error = "Такого пользователя не существует"
            return render_template("vxod.html", error=error)
            # return flask.flash("Идиот", category='message')
        n = 0
        number_row = 0
        for row in result:
            print(row)
            if row["email"] == email:
                number_row = n
            n += 1

        key_privilege = "privilege"
        privilege = result[number_row][key_privilege]
        cursor.close()

        # Проверка привелегий, если значение 1 то админ сайт, иначе открывается обычный сайт
        match privilege:
            case 1:
                print("Админ сайт")
                print(privilege)
                return render_template("siteadmin.html")
            case 2:
                print("Основной сайт")
                print(privilege)
                return render_template("site.html")
            case _:
                print("Основной сайт")
                print(privilege)
                return render_template("site.html")


@app.route('/registration_data/vxod.html')
@app.route('/site_data/vxod.html')
def vxod_html_win():
    return render_template("vxod.html")


@app.route('/registration_data/', methods=['POST', 'GET'])
def registration() -> None:
    """
    Регистрация пользователя
    :return: None
    """
    # Получение переменных из HTML формы регистрации
    """данный метод escape_string() экранирует ' и ", что не дает сделать sql-инъекцию"""
    email = escape_string(request.form['email'])
    password = escape_string(request.form['psw'])
    password_repeat = escape_string(request.form['psw-repeat'])

    # Проверка email на правильность
    if not re.match(r"^((([0-9A-Za-z]{1}[-0-9A-z\.]{0,30}[0-9A-Za-z]?)|([0-9А-Яа-я]{1}[-0-9А-я\.]{0,30}[0-9А-Яа-я]?))@([-A-Za-z]{1,}\.){1,}[-A-Za-z]{2,})$",
                email):
        print(f"eror email {email}")
        error_email = "Введите корректный email"
        return render_template("registration.html", error=error_email)

    # Проверка совпадения паролей
    if password != password_repeat:
        print("Пароли неправильные")
        error_repeat = "Введённые пароли не совпадают"
        return render_template("registration.html", error=error_repeat)

    # Проверка на защищенный пароль он должен быть 8 символов и содержать верхний, нижний регистр, цифры и спец.сим.
    if not re.match(r"((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%]).{8,})", password):
        print("Пароль слабый")
        error_weak_password =  "Слабый пароль (не короче 8 букв и цифр, а также спецсимволы. Не используйте личные данные, последовательности (123456, qwerty) и популярные пароли (password)"
        return render_template("registration.html", error=error_weak_password)

    # Подлкючение к БД Mysql
    connection = pymysql.connect(**config, cursorclass=pymysql.cursors.DictCursor, charset='utf8', use_unicode=True)
    with connection.cursor() as cursor:
        select_movies_query = "SELECT * FROM users WHERE email = %s"
        """Передачи в sql через аргументы не дает выполнить sql-инъекцию"""
        cursor.execute(select_movies_query, email)
        result = cursor.fetchall()
        # Проверка есть ли такой пароль и логин в БД
        if result:
            print("Кортеж не пустой")
            print("Есть такой аккаунт в БД")
            error_have_user = "Такой аккаунт уже был зарегестрирован"
            return render_template("registration.html", error=error_have_user)
            cursor.close()
            
        # Запись в БД нового пользователя
        else:
            privilege = 2
            select_insert = "INSERT INTO users (email, password, privilege) VALUES (%s,%s,%s)"
            val = (email, password, privilege)
            """Передачи в sql через аргументы не дает выполнить sql-инъекцию"""
            cursor.execute(select_insert, val)
            connection.commit()
            print("Регистрация завершена")
            cursor.close()
            return render_template("site.html")


@app.route('/registration_data/registration.html')
@app.route('/registration.html')
@app.route('/site_data/registration.html')
def registration_site_html_win():
    return render_template("registration.html")


if __name__ == '__main__':
    # Библиотека waitress для создание веб сервера
    from waitress import serve
    serve(app, host="127.0.0.1", port=8080)