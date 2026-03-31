from flask import Flask, redirect, render_template

app = Flask(__name__)

# @app.before_request()
# def before_request():
#     print('This function runs before each request.')
#
# @app.after_request
# def after_request(response):
#     print('This function runs after each request.')
#     return response

@app.route('/')
def main_page():
    return  render_template('main_page.html')

@app.route('/user')
def user():
    return render_template('main_page.html')

if __name__ == '__main__':
    app.run(debug=True)