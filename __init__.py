from flask import Flask, render_template, request, \
                  make_response, redirect, url_for
import os
import requests


app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/', methods=['GET'])
def main_page():
    session_cookie = request.cookies.get('session')
    if session_cookie:
        cookies = {'session': session_cookie}
        url = 'https://mybook.ru'
        path = '/api/bookuserlist/'
        headers = {'Accept': 'application/json; version=5'}
        all_books = []
        while True:
            page_raw = requests.get(
                        '{}{}'.format(url, path), 
                        headers=headers,
                        cookies=cookies)
            page_json = page_raw.json()
            books_on_page = page_json['objects']
            all_books.extend(books_on_page)
            if page_json['meta']['next']:
                path = page_json['meta']['next']
            else:
                break
        return render_template('books.html', books=all_books)
    return redirect(url_for('login'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = ''
    if request.method == 'POST':
        session = requests.Session()
        response = session.post('https://mybook.ru/api/auth/', {
            'email': request.form['email'],
            'password': request.form['password']
        })
        if response.ok:
            redirect_response = make_response(redirect(url_for('main_page')))
            redirect_response.set_cookie('session', session.cookies['session'])
            return redirect_response
        else:
            error = 'Invalid username/password'
    session_cookie = request.cookies.get('session')
    if session_cookie:
        return redirect(url_for('main_page'))
    return render_template('auth.html', error=error)


@app.route('/logout', methods=['GET'])
def logout():
    session_cookie = request.cookies.get('session')
    if session_cookie:
        redirect_response = make_response(redirect(url_for('main_page')))
        redirect_response.set_cookie('session', '')
        return redirect_response
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
