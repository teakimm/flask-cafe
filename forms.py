"""Forms for Flask Cafe."""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, SelectField
from wtforms.validators import InputRequired, URL, Optional

class cafeForm(FlaskForm):
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
