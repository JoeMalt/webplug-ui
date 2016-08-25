from functools import wraps

from flask import *
from passlib.apps import custom_app_context as pwd_context


from core.orm_template import db_user, db_plugSocket
from core import get_db_session

app = Flask(__name__)

# Config
app.config['SECRET_KEY'] = "sdfharwifsfhqht89qthehfq938rutu9e4ufgpWQEUFQEUF498"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session.keys() or session['username'] is None:
            flash("You need to login to access this page")
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
@login_required
def index():
    # Guarantee the database connection is closed
    db_session = get_db_session()
    try:
        query = db_session.query(db_plugSocket).all()
    finally:
        db_session.close()

    return render_template('index.html', query=query)


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

@app.route("/admin")
@login_required
def admin():
    return render_template("admin.html")
    
@app.route("/admin_change_password/<user_id>", methods=['GET'])
@login_required
def admin_change_password(user_id):
    return render_template("admin_change_password.html")

@app.route("/admin_change_password", methods=['POST'])
@login_required
def admin_change_password_process():
    if request.form['password'] == request.form['password2']:
        # change password here
        flash("Password changed")
        return redirect(url_for('admin'))
    else:
        flash("Passwords do not match")
        return redirect(url_for('admin_change_password', user_id = 1))

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

def verify_credentials(username, password):
    # We need to guarantee closure of the database.
    db_session = get_db_session()
    try:
        user = db_session.query(db_user).filter(db_user.username == username).first()
    finally:
        db_session.close()

    if user is not None and pwd_context.verify(password, user.pwd_hash):
        return True
    else:
        return False
