from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, TextAreaField, DateTimeField
from wtforms.validators import InputRequired, DataRequired

class AddUserForm(FlaskForm):
    """New User Form"""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class UserForm(FlaskForm):
    """Existing User"""

    # firstname = StringField("First Name", validators=[InputRequired()])
    # namename = StringField("Last Name", validators=[InputRequired()])
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class WorkoutForm(FlaskForm):
    """Workout Post to li"""
    exercise = StringField("Exercise Name")
    weight = StringField("Weight")
    reps = IntegerField("Reps")
    sets = IntegerField("Sets")
    date = StringField("Date")

class NutritionForm(FlaskForm):
    """Workout Post to li"""
    food = StringField("Food Name")
    protein = IntegerField("Protein")
    carbs = IntegerField("Carbohydrates")
    fats = IntegerField("Fats")
    calories = IntegerField("Calories")
    date = StringField("Date")

# class MessageForm(FlaskForm):
#     """Form for sharing post"""

#     text = TextAreaField('text', validators=[DataRequired()])