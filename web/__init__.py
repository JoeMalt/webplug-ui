from functools import wraps

from flask import *
from passlib.apps import custom_app_context as pwd_context

from core.orm_template import db_user, db_host, db_plugSocket, db_scheduleRule
from core import get_db_session, msg_worker

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
        schedule_rules = db_session.query(db_scheduleRule, db_plugSocket).join(db_plugSocket).all()
        
    finally:
        db_session.close()

    return render_template('index.html', query=query, schedule_rules=schedule_rules)


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

    return render_template("admin.html", users=users)


@app.route("/add_user", methods=['POST', 'GET'])
@login_required
@admin_required
def add_user():
    if request.method == 'GET':
        return render_template('add_user.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if "is_admin" in request.form.keys() and request.form['is_admin'] == "on":
            is_admin = 1
        else:
            is_admin = 0
            

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
        return redirect(url_for('admin_change_password'))



@app.route("/rename_device/<plug_socket_id>", methods=['GET']) #This is the primary key from the plug_sockets table, plug_sockets.id It is *not* the plug_id because this is not a PK
@login_required
@admin_required
def rename_device(plug_socket_id):
    session['tmp_plug_socket_id_to_change'] = plug_socket_id  # this is a bit hacky but by far the easiest way
    return render_template("rename_device.html")


@app.route("/rename_device", methods=['POST'])
@login_required
@admin_required
def rename_device_process():

    plug_socket_id = session['tmp_plug_socket_id_to_change']
    name = request.form['name']

    db_session = get_db_session()
    try:
        plug_socket = db_session.query(db_plugSocket).filter(db_plugSocket.id == plug_socket_id).first()
        plug_socket.name = name
        db_session.commit()
    finally:
        session['tmp_plug_socket_id_to_change'] = None
        db_session.close()

    flash("Name updated")
    return redirect(url_for('index'))
  
        
        
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
    db_session = get_db_session()
    try:
        query = db_session.query(db_plugSocket, db_host).filter(db_plugSocket.host_id == host,
                                                                db_plugSocket.plug_id == plug).join(db_host).first()
        if query.db_plugSocket.status == 0:
            # Turn it on
            if msg_worker('N', host, plug):
                flash('Toggled plug ' + plug + ' on host ' + host + '.')
            else:
                flash('Host {} was not connectable.'.format(host))
        else:
            # If anything else, just turn it off to be safe
            if msg_worker('F', host, plug):
                flash('Toggled plug ' + plug + ' on host ' + host + '.')
            else:
                flash('Host {} was not connectable.'.format(host))
    finally:
        db_session.close

    return redirect(url_for('index'))


#SCHEDULING
@app.route("/delete_schedule_rule", methods=['POST'])
@login_required
@admin_required
def delete_schedule_rule():
    schedule_rule_id = request.form['schedule_rule_id']

    # Delete the selected user from the database.
    db_session = get_db_session()
    try:
        db_session.query(db_scheduleRule).filter(db_scheduleRule.id == schedule_rule_id).delete()
        db_session.commit()
    finally:
        db_session.close()

    flash("Schedule rule deleted")
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
