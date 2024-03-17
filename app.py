"""Flask App for Flask Cafe."""

import os

from flask import Flask, render_template, flash, session, redirect, g, jsonify, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, Cafe, City, User, DEFAULT_USER_IMAGE
from forms import CafeForm, SignupForm, LoginForm, ProfileEditForm


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///flask_cafe')
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "shhhh")

if app.debug:
    app.config['SQLALCHEMY_ECHO'] = True

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)

#######################################
# auth & auth routes

CURR_USER_KEY = "curr_user"
NOT_LOGGED_IN_MSG = "You are not logged in."


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    do_logout()

    form = SignupForm()

    if form.validate_on_submit():
        user = User.register(
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            description=form.description.data,
            password=form.password.data,
            email=form.email.data,
            image_url=form.image_url.data or None,
        )

        try:
            db.session.commit()

        except IntegrityError:
            form.username.errors = ["Username already exists."]
            return render_template('auth/signup-form.html', form=form)

        do_login(user)

        flash(f"You are signed up and logged in.", "success")
        return redirect("/cafes")

    else:
        return render_template('auth/signup-form.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login. Redirects on success to cafe list."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/cafes")

        flash("Invalid credentials.", 'danger')

    return render_template('auth/login-form.html', form=form)


@app.post('/logout')
def logout():
    """Handle logout of user. Redirects to homepage."""

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/")


#######################################
# homepage

@app.get("/")
def homepage():
    """render homepage"""

    return render_template("homepage.html")


#######################################
# cafes


@app.get('/cafes')
def cafe_list():
    """Render page of all the cafes in abc order"""

    cafes = Cafe.query.order_by('name').all()

    return render_template('cafe/list.html', cafes=cafes)


@app.get('/cafes/<int:cafe_id>')
def cafe_detail(cafe_id):
    """Render page for a given cafe's details"""

    cafe = Cafe.query.get_or_404(cafe_id)

    return render_template('cafe/detail.html', cafe=cafe)


@app.route("/cafes/add", methods=["GET", "POST"])
def add_Cafe():
    """Renders the form or adds the cafe to the db given form data"""

    #regular ole users should not be able to add/edit cafes
    if not g.user or not g.user.admin:
        flash("Access Denied", "danger")
        return redirect("/cafes")

    form = CafeForm()

    form.city_code.choices = City.get_cities()

    if form.validate_on_submit():
        cafe = Cafe(
            name=form.name.data,
            description=form.description.data,
            url=form.url.data,
            address=form.address.data,
            city_code=form.city_code.data,
            image_url=form.image_url.data or None,
        )

        db.session.add(cafe)

        db.session.flush()
        cafe.save_map()

        db.session.commit()

        flash(f"Added {cafe.name}.", "success")
        return redirect(f"/cafes/{cafe.id}")
    else:
        return render_template("/cafe/add-form.html", form=form)


@app.route('/cafes/<int:cafe_id>/edit', methods=["GET", "POST"])
def edit_cafe(cafe_id):
    """Renders form or sends form data for editing a cafe"""

    if not g.user or not g.user.admin:
        flash("Access Denied", "danger")
        return redirect("/cafes")

    cafe = Cafe.query.get_or_404(cafe_id)

    form = CafeForm(obj=cafe)
    form.city_code.choices = City.get_cities()

    if form.validate_on_submit():
        new_map = (cafe.address != form.address.data or \
                cafe.city_code != form.city_code.data)

        cafe.name = form.name.data
        cafe.description = form.description.data
        cafe.url = form.url.data
        cafe.address = form.address.data
        cafe.city_code = form.city_code.data
        cafe.image_url = form.image_url.data or None

        if new_map:
            db.session.flush()
            cafe.save_map()

        db.session.commit()

        flash(f"Edited {cafe.name}.", "success")
        return redirect(f"/cafes/{cafe.id}")

    else:
        return render_template("cafe/edit-form.html", cafe=cafe, form=form)


#########################################################
# users

@app.get('/profile')
def profile():
    """Render Page for user profile information"""

    if not g.user:
        flash(NOT_LOGGED_IN_MSG, "danger")
        return redirect("/login")

    return render_template("profile/detail.html", user=g.user)


@app.route('/profile/edit', methods=["GET", "POST"])
def profile_edit():
    """Renders form or sends form data for editing a user profile"""

    if not g.user:
        flash(NOT_LOGGED_IN_MSG, "danger")
        return redirect("/login")

    user = g.user

    form = ProfileEditForm(obj=g.user)

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.description = form.description.data
        user.email = form.email.data
        user.description = form.description.data
        user.image_url = form.image_url.data or DEFAULT_USER_IMAGE
        db.session.commit()

        flash("Profile edited.", "success")
        return redirect("/profile")

    else:
        return render_template('profile/edit-form.html', form=form)


@app.get("/api/likes")
def check_like_cafe():
    """Given a query string of cafe id, checks if a user likes a cafe
    If logged in, returns JSON:
    {
        "likes": true (or false)
    }
    """

    if not g.user:
        return jsonify({"error": "Not logged in"})

    cafe_id = int(request.args['cafe_id'])
    current_cafe = Cafe.query.get_or_404(cafe_id)

    like = current_cafe in g.user.liked_cafes

    return jsonify({"likes": like})


@app.post("/api/like")
def like_cafe():
    """Passing a cafe id as JSON:
    {
        "cafe_id" : 3
    }
    add the liked cafe to the db and return JSON:
    {
        "liked" : 3
    }
    """

    if not g.user:
        return jsonify({"error": "Not logged in"})

    cafe_id = int(request.json['cafe_id'])
    current_cafe = Cafe.query.get_or_404(cafe_id)

    g.user.liked_cafes.append(current_cafe)
    db.session.commit()

    response = {"liked": current_cafe.id}
    return jsonify(response)


@app.post("/api/unlike")
def unlike_cafe():
    """Passing a cafe id as JSON:
    {
        "cafe_id" : 3
    }
    remove the liked cafe to the db and return JSON:
    {
        "unliked" : 3
    }
    """

    if not g.user:
        return jsonify({"error": "Not logged in"})

    cafe_id = int(request.json['cafe_id'])
    current_cafe = Cafe.query.get_or_404(cafe_id)

    g.user.liked_cafes.remove(current_cafe)
    db.session.commit()

    response = {"unliked": current_cafe.id}
    return jsonify(response)


##########################################################
#404
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")