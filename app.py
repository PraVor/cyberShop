from flask import Flask, render_template, request, session, redirect
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'ytrewq321'


@app.route('/')
def index():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        items = request.form['items']


        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password, email, items) VALUES (?, ?, ?, ?)",
                           (username, hashed_password, email, items)
            )
            conn.commit()
        except:
            return 'Такий користувач вже зареестрований'

        conn.close()


        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):
            session['user'] = username
            return redirect('/shop')
        else:
            return 'Неправильний логін або пароль'

    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, items FROM users WHERE username = ?", (session['user'],))
    user = cursor.fetchone()
    conn.close()

    items_list = [i.strip() for i in user[2].split(',') if i.strip()] if user[2] else []

    return render_template('profile.html', username=user[0], email=user[1], items=items_list)



@app.route('/shop', methods=['GET', 'POST'])
def shop():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        item_name = request.form.get('item')

        if item_name:
            cursor.execute(
                "SELECT items FROM users WHERE username = ?",
                (session['user'],)
            )
            result = cursor.fetchone()

            current_items = result[0] if result and result[0] else ""
            items_list = current_items.split(",") if current_items else []

            if item_name not in items_list:
                items_list.append(item_name)
                updated_items = ",".join(items_list)
                cursor.execute(
                    "UPDATE users SET items = ? WHERE username = ?",
                    (updated_items, session['user'])
                )
                conn.commit()

    cursor.execute("SELECT items FROM users WHERE username = ?", (session['user'],))
    result = cursor.fetchone()
    current_items = result[0] if result and result[0] else ""
    items_list = [i.strip() for i in current_items.split(",") if i.strip()]

    conn.close()
    return render_template('shop.html', user_items=items_list)





@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


port = int(os.environ.get('PORT', 10000))
app.run(host='0.0.0.0', port=port)