import sys
sys.path.insert(1, '/Users/agnithamohanram/Documents/NYU-courses/NYU_Sem4/PracticalComputerSecurity/Project/ProjectCode/WasPy/safe_string')
import safe_string as safe_string
import sql
from sql import has_sqli
safe_string.safe_string._new_trusted('basic Flask app - demo of using a variable in a route')
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
app = Flask(__name__)
app.config[safe_string.safe_string._new_trusted('SECRET_KEY')] = safe_string.safe_string._new_trusted('30lTgkRcQ9')
Bootstrap(app)

class NameForm(FlaskForm):
    name = StringField(safe_string.safe_string._new_trusted('Enter your name:'), validators=[DataRequired()])
    submit = SubmitField(safe_string.safe_string._new_trusted('Submit'))

@app.route('/')
def home():
    return render_template(safe_string.safe_string._new_trusted('home.html'))

@app.route('/demo', methods=[safe_string.safe_string._new_trusted('GET'), safe_string.safe_string._new_trusted('POST')])
def demo():
    form = NameForm()
    message = safe_string.safe_string._new_trusted('')
    query = safe_string.safe_string._new_trusted('SELECT * FROM users WHERE name = ')
    if form.validate_on_submit():
        name = form.name.data
        query += safe_string.safe_string._new_trusted("'") + name + safe_string.safe_string._new_trusted("'")
        if has_sqli(query):
            form.name.data = safe_string.safe_string._new_trusted('')
            message = safe_string.safe_string._new_trusted('SQLI has been detected.')
        else:
            message = safe_string.safe_string._new_trusted("SQLI has not been detected/there's a syntax error.")
    return render_template(safe_string.safe_string._new_trusted('demo.html'), form=form, message=message)
if __name__ == safe_string.safe_string._new_trusted('__main__'):
    app.run(debug=True)