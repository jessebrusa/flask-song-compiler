from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/library')
def library():
    return render_template('library.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)