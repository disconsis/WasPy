"""basic Flask app - demo of using a variable in a route"""

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from safe_string.safe_string import safe_string
from safe_string.safe_sql import has_sqli


app = Flask(__name__)
app.config['SECRET_KEY'] = '30lTgkRcQ9'
Bootstrap(app)


class NameForm(FlaskForm):
    name = StringField('Enter your name:', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/demo', methods=['GET', 'POST'])
def demo():
    form = NameForm()
    message = ""
    query = safe_string._new_trusted("SELECT * FROM users WHERE name = '{}'")

    if form.validate_on_submit():
        name = form.name.data
        query = query.format(name)
        if has_sqli(query):
            # empty the form field
            form.name.data = ""
            message = "SQLI has been detected."
        else:
            message = "SQLI has not been detected/there's a syntax error."
    return render_template('demo.html', form=form, message=message)


if __name__ == '__main__':
    app.run(debug=True)
