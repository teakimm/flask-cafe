"""Forms for Flask Cafe."""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, SelectField, PasswordField
from wtforms.validators import InputRequired, URL, Optional, Email, Length

class CafeForm(FlaskForm):
    """Form for adding/editing cafes"""

    name = StringField(
        "Cafe Name",
        validators=[InputRequired()]
    )

    description = TextAreaField(
        "Description",
        validators=[Optional()]
    )

    url = URLField(
        "URL",
        validators=[Optional(), URL()]
    )

    address = StringField(
        "Address",
        validators=[InputRequired()]
    )

    city_code = SelectField(
        "City"
    )

    image_url = URLField(
        "Image URL",
        validators=[Optional(), URL()]
    )


class SignupForm(FlaskForm):
    """Form for adding users on signup."""

    username = StringField(
        'Username',
        validators=[InputRequired()],
    )

    first_name = StringField(
        'First Name',
        validators=[InputRequired()],
    )

    last_name = StringField(
        'Last Name',
        validators=[InputRequired()],
    )

    description = TextAreaField(
        'Description',
    )

    email = StringField(
        'Email',
        validators=[InputRequired(), Email()],
    )

    password = PasswordField(
        'Password',
        validators=[Length(min=6)],
    )

    image_url = StringField(
        'Image URL',
        validators=[URL(), Optional()],
    )


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(
        'Username',
        validators=[InputRequired()],
    )

    password = PasswordField(
        'Password',
        validators=[InputRequired()],
    )

class ProfileEditForm(FlaskForm):
    """Form for editing a user profile."""

    first_name = StringField(
        'First Name',
        validators=[InputRequired()],
    )

    last_name = StringField(
        'Last Name',
        validators=[InputRequired()],
    )

    description = TextAreaField(
        'Description',
    )

    email = StringField(
        'Email',
        validators=[InputRequired(), Email()],
    )

    image_url = StringField(
        'Image URL (Not Required)',
    )