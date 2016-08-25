from flask import *
from functools import wraps
from passlib.apps import custom_app_context as pwd_context

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .orm_template import db_user

app = Flask(__name__)

# Config
app.config['SECRET_KEY'] = "sdfharwifsfhqht89qthehfq938rutu9e4ufgpWQEUFQEUF498"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session.keys() or session['username'] == None:
            flash("You need to login to access this page")
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
@login_required
def index():
    return render_template('index.html')


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if verify_credentials(username, password):
            session['username'] = username
            flash("Successfully logged in")
            return redirect(url_for('index'))
        else:
            flash("Incorrect username or password")
            return redirect(url_for('login'))


@app.route("/logout")
def logout():
    session['username'] = None
    flash("Successfully logged out")
    return redirect(url_for('login'))


@app.route("/toggle", methods=['POST'])  # TODO: implement CSRF token
def toggle():
    host = request.form['host']
    plug = request.form['plug']

    # Talk to the C code here

    # Now tell the user that we've done it
    flash('Toggled plug ' + plug + ' on host ' + host + '.')
    return redirect(url_for('index'))


def get_db_session():
    engine = create_engine('sqlite:///web/webplug.db')
    Session = sessionmaker(bind=engine)
    db_session = Session()

    return db_session


def verify_credentials(username, password):
    # We need to guarantee closure of the database.
    db_session = get_db_session()
    try:
        user = db_session.query(db_user).filter(db_user.username == username).first()
    finally:
        db_session.close()

    if pwd_context.verify(password, user.pwd_hash):
        return True
    else:
        return False
