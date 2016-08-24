from flask import *
from functools import wraps
app = Flask(__name__)

#Config
app.config['SECRET_KEY'] = "sdfharwifsfhqht89qthehfq938rutu9e4ufgpWQEUFQEUF498"

@app.route("/")
@login_required
def index():
	return render_template('index.html')

@app.route("/login", methods = ['POST', 'GET'])
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

@app.route("/toggle", methods=['POST']) #TODO: implement CSRF token
def toggle():
	host = request.form['host']
	plug = request.form['plug']
		
	#Talk to the C code here
	
	#Now tell the user that we've done it
	flash('Toggled plug ' + plug + ' on host ' + host + '.')
	return redirect(url_for('index'))
	

#These functions should probably go elsewhere

def is_logged_():
	if 'username' not in session.keys() or session['username'] == None:
			#User is not logged in
			flash("You must log in to access this page")
			redirect(url_for('login'))
			return False
	return True
	
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session.keys() or session['username'] == None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
   
def verify_credentials(username, password):
	return True

if __name__ == "__main__":
	app.run()
