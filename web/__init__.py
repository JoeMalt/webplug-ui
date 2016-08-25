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
            flash("You need to login to access that page")
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session['is_admin'] != True:
            flash("You need to be an admin to access that page")
            return redirect(url_for('index'))
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

        login_status = verify_credentials(username, password)

        if login_status == 1:
            session['username'] = username
            session['is_admin'] = False
            flash("Successfully logged in")
            return redirect(url_for('index'))
        elif login_status == 2:
            session['username'] = username
            session['is_admin'] = True
            flash("Successfully logged in as an admin")
            return redirect(url_for('index'))
        else:
            flash("Incorrect username or password")
            return redirect(url_for('login'))


@app.route("/admin")
@login_required
@admin_required
def admin():

    db_session = get_db_session()
    try:
        users = db_session.query(db_user).all()
    finally:
        db_session.close()

    return render_template("admin.html", users=users)  # TODO database: populate the users list from the DB


@app.route("/add_user", methods=['POST', 'GET'])
@login_required
@admin_required
def add_user():
    if request.method == 'GET':
        return render_template('add_user.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = request.form['is_admin']

        db_session = get_db_session()
        try:
            pwd_hash = pwd_context.encrypt(password)

            new_user = db_user(username=username, pwd_hash=pwd_hash, is_admin=is_admin)
            db_session.add(new_user)
            db_session.commit()
        finally:
            db_session.close()

        flash('User added')
        return redirect(url_for('admin'))


@app.route("/admin_change_password/<user_id>", methods=['GET'])
@login_required
@admin_required
def admin_change_password(user_id):
    session['tmp_user_id_to_change'] = user_id  # this is a bit hacky but by far the easiest way
    return render_template("admin_change_password.html")


@app.route("/delete_user", methods=['POST'])
@login_required
@admin_required
def delete_user():
    user_id = request.form['user_id']

    # Delete the selected user from the database.
    db_session = get_db_session()
    try:
        db_session.query(db_user).filter(db_user.id == user_id).delete()
        db_session.commit()
    finally:
        db_session.close()

    flash("User deleted")
    return redirect(url_for('admin'))


@app.route("/toggle_admin", methods=['POST'])
@login_required
@admin_required
def toggle_admin():
    user_id = request.form['user_id']

    db_session = get_db_session()
    try:
        user = db_session.query(db_user).filter(db_user.id == user_id).first()
        if user.is_admin == 0:
            user.is_admin = 1
        else:
            user.is_admin = 0

        db_session.commit()
    finally:
        db_session.close()

    flash("Admin status toggled")
    return redirect(url_for('admin'))


@app.route("/admin_change_password", methods=['POST'])
@login_required
@admin_required
def admin_change_password_process():
    if request.form['password'] == request.form['password2']:
        user_id = session['tmp_user_id_to_change']
        password = request.form['password']

        db_session = get_db_session()
        try:
            pwd_hash = pwd_context.encrypt(password)

            user = db_session.query(db_user).filter(db_user.id == user_id).first()
            user.pwd_hash = pwd_hash
            db_session.commit()
        finally:
            session['tmp_user_id_to_change'] = None
            db_session.close()

        # No need to check current password as this is an admin feature
        flash("Password changed")
        return redirect(url_for('admin'))
    else:
        flash("Passwords do not match")
        return redirect(url_for('admin_change_password', user_id=1))


@app.route("/logout")
@login_required
def logout():
    session['username'] = None
    flash("Successfully logged out")
    return redirect(url_for('login'))


@app.route("/toggle", methods=['POST'])  # TODO: implement CSRF token
def toggle():
    host = request.form['host']
    plug = request.form['plug']

    # Connect to the daemon here

    # Now tell the user that we've done it
    flash('Toggled plug ' + plug + ' on host ' + host + '.')
    return redirect(url_for('index'))


def verify_credentials(username, password):
    # Returns 0 for bad credentials, 1 for standard user, 2 for admin
    # We need to guarantee closure of the database.
    db_session = get_db_session()
    try:
        user = db_session.query(db_user).filter(db_user.username == username).first()
    finally:
        db_session.close()

    if user is not None and pwd_context.verify(password, user.pwd_hash):
        if user.is_admin == 1:
            return 2
        return 1
    else:
        return 0
