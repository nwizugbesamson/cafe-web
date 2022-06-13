from cProfile import label
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, URL, Email, InputRequired

seat_choices = ["0-10", "11-25", "26-30", "40-65", "66-100"]

class RegisterForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    email = EmailField(label='Email', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label="Register")


# CREATE LOGIN FORM
class LoginForm(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label="Login")


# CREATE ADD CAFE PAGE
class AddForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    submit = SubmitField(label="Check Store")


options = ["True", "False"]

class ConfirmForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    location = StringField(label="Location", validators=[DataRequired()])
    img_url = StringField(label="img_url", validators=[DataRequired()], name="Image Address")
    map_url = StringField(label="map_url", validators=[DataRequired()], name="Map Address")
    open_hours = StringField(label="open_hours", validators=[DataRequired()], name="Open Hours")
    price = IntegerField(label="price", validators=[DataRequired()], name="Coffee Price In USD")
    seat = SelectField(label="seat", validators=[DataRequired()], choices=seat_choices)
    wifi = SelectField(label="wifi", validators=[InputRequired()], choices=options)
    plug = SelectField(label="plug", validators=[DataRequired()], choices=options)
    phone = SelectField(label="phone", validators=[DataRequired()], choices=options)
    toilet = SelectField(label="toilet", validators=[DataRequired()], choices=options)
    submit = SubmitField(label="Add Cafe")


class ReviewForm(FlaskForm):
    review = TextAreaField(label="review", validators=[DataRequired()])
    submit = SubmitField(label="post")