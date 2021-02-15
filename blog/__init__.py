import os
from flaskext.markdown import Markdown
from . import db
from flask import render_template
from flask import Flask
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import send_from_directory
from flask import abort
from flask_simplemde import SimpleMDE
# from flask import jsonify
import bcrypt

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'database.sql'),
    )
    md = Markdown(app, output_format='html5')
    smde = SimpleMDE(app)
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
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static/ico'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        message = ""
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            database = db.get_db()
            user_password_query = database.execute(
                'SELECT * FROM user WHERE username = ?', (username,)
            ).fetchone()
            if user_password_query:
                user_hashed_password = user_password_query['password']
                if app.testing:
                    print("User is trying to login. Username = {u}, Password = {p}\r\n".format(u=username, p=password))

                if bcrypt.checkpw(bytes(password, "utf-8"), bytes(bytearray.fromhex(user_hashed_password))):
			#todo make it okay, u got me?
                    session['user-id'] = user_password_query['id']
                    return redirect(url_for('index'))
                else:
                    message = "Login error"
            else:
                message = "You even not registered -_-"

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
                hashed_password = bcrypt.hashpw(bytes(password, "utf-8"), bcrypt.gensalt()).hex()
                if app.testing:
                    print("No user found")
                    print("Trying to reg User: \r\nusername = {u}, password = {p}, hashed={h}".format(u=username, p=password, h=hashed_password))
                user_query = database.execute('INSERT INTO user ("id","username","password") VALUES (NULL,?,?)', (username, hashed_password,)).fetchone()
                database.commit()
                # return "Registration complete!"
                # message = "Registration complete !"
                # return render_template('blog/auth/register.html', message=message )
                
                # session['user-id'] = user_query['id']
                return redirect(url_for('index'))
            else:
                message = "User {u} allready exists !".format(u=username)
                return render_template('blog/auth/register.html', message=message)
            
        else:
            return render_template('blog/auth/register.html')
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))
        
    
    @app.route('/')
    def index():
        return redirect(url_for('list'))

    @app.route('/list')
    def list():
        database = db.get_db()
        posts = user = database.execute('SELECT * FROM post')
        return render_template('blog/list.html', posts=posts)
    @app.route('/add', methods=['GET', 'POST'])
    def add():
        message = "Unexpected error occured. Did u forget to log in?"
        if request.method == 'POST':
            if 'user-id' in session:
                title = request.form['title']
                content = request.form['content']
                database = db.get_db()
                hz = database.execute('INSERT INTO post ("id","title","content", "author_id") VALUES (NULL,?,?, ?)', (title, content,int(session['user-id']))).fetchone()
                database.commit()
        return render_template('blog/add.html', message = "Okay we done there")
    @app.route('/edit/<int:post_id>', methods = ['GET', 'POST'])
    def edit(post_id):
        if 'user-id' in session:
            database= db.get_db()
            if request.method == 'POST':
                title = request.form['title']
                content = request.form['content']
                hz = database.execute('UPDATE post SET title=?, content=? WHERE id =?', (title, content, post_id)).fetchone()
                database.commit()
                return redirect(url_for('show', post_id=post_id))
            else:
                post = database.execute('SELECT * FROM post WHERE id=?', (post_id, )).fetchone()
                if post:
                    return render_template('blog/edit.html', post=post)    
            abort(404)
    @app.route('/show/<int:post_id>')
    def show(post_id):
        database = db.get_db()
        post = database.execute('SELECT * FROM post WHERE id=?', (post_id, )).fetchone()
        if post:
            return render_template('blog/show.html', post=post)
        else:
            abort(404)


    db.init_app(app)

    return app

