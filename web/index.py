from flask import render_template, request

app = Flask(__name__)

# Config
app.config['SECRET_KEY'] = "sdfharwifsfhqht89qthehfq938rutu9e4ufgpWQEUFQEUF498"


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/toggle", methods=['POST'])  # TODO: implement CSRF token
def toggle():
    host = request.form['host']
    plug = request.form['plug']

    # Talk to the C code here

    # Now tell the user that we've done it
    flash('Toggled plug ' + plug + ' on host ' + host + '.')
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
