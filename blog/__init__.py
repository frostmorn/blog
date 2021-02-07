import os

from . import db
from flask import render_template
from flask import Flask
from flask import request

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'database.sql'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/login', methods=['GET', 'POST'])
    def login():
    # TODO: Add password hashing    
        message = ""
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            database = db.get_db()
            user = database.execute(
                'SELECT * FROM user WHERE username = ? AND password = ?', (username, password)
            ).fetchone()
            if user:
                message = "Login complete"
            else:
                message = "Login error"

        return render_template('blog/auth/login.html', message = message)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            database = db.get_db()
            user = database.execute(
                'SELECT * FROM user WHERE username = ?', (username,)
            ).fetchone()

            if user == None:
                print("No user found")
                print("Trying to reg User: \r\nusername = {u}, password = {p}".format(u=username, p=password))
                hz = database.execute('INSERT INTO user ("id","username","password") VALUES (NULL,?,?)', (username, password,)).fetchone()
                database.commit()
                # return "Registration complete!"
                message = "Registration complete !"
                return render_template('blog/auth/register.html', message=message )
            else:
                message = "User {u} allready exists !".format(u=username)
                return render_template('blog/auth/register.html', message=message)
            
        else:
            return render_template('blog/auth/register.html')

    
    @app.route('/')
    def index():
        return render_template('base.html')

    @app.route('/list')
    def list():
        return render_template('blog/base.html')

    @app.route('/show/<int:page>')
    def show(page):
        
        return render_template('blog/base.html')


    db.init_app(app)

    return app

