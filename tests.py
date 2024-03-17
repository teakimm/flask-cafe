"""Tests for Flask Cafe."""


import os

os.environ["DATABASE_URL"] = "postgresql:///flaskcafe_test"
os.environ["FLASK_DEBUG"] = "0"

import re
from unittest import TestCase

# from flask import session
from app import app, CURR_USER_KEY
from models import db, Cafe, City, connect_db, User, Like
from flask import session

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# Don't req CSRF for testing
app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()


#######################################
# helper functions for tests


def debug_html(response, label="DEBUGGING"):  # pragma: no cover
    """Prints HTML response; useful for debugging tests."""

    print("\n\n\n", "*********", label, "\n")
    print(response.data.decode('utf8'))
    print("\n\n")


def login_for_test(client, user_id):
    """Log in this user."""

    with client.session_transaction() as sess:
        sess[CURR_USER_KEY] = user_id


#######################################
# data to use for test objects / testing forms


CITY_DATA = dict(
    code="sf",
    name="San Francisco",
    state="CA"
)

CAFE_DATA = dict(
    name="Test Cafe",
    description="Test description",
    url="http://testcafe.com/",
    address="500 Sansome St",
    city_code="sf",
    image_url="http://testcafeimg.com/"
)

CAFE_DATA_EDIT = dict(
    name="new-name",
    description="new-description",
    url="http://new-image.com/",
    address="500 Sansome St",
    city_code="sf",
    image_url="http://new-image.com/"
)

TEST_USER_DATA = dict(
    username="test",
    first_name="Testy",
    last_name="MacTest",
    description="Test Description.",
    email="test@test.com",
    password="secret",
)

TEST_USER_DATA_EDIT = dict(
    first_name="new-fn",
    last_name="new-ln",
    description="new-description",
    email="new-email@test.com",
    image_url="http://new-image.com",
)

TEST_USER_DATA_NEW = dict(
    username="new-username",
    first_name="new-fn",
    last_name="new-ln",
    description="new-description",
    password="secret",
    email="new-email@test.com",
    image_url="http://new-image.com",
)

ADMIN_USER_DATA = dict(
    username="admin",
    first_name="Addie",
    last_name="MacAdmin",
    description="Admin Description.",
    email="admin@test.com",
    password="secret",
    admin=True,
)


#######################################
# homepage


class HomepageViewsTestCase(TestCase):
    """Tests about homepage."""

    def test_homepage(self):
        with app.test_client() as client:
            resp = client.get("/")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Flask Cafe', resp.data)


#######################################
# cities


class CityModelTestCase(TestCase):
    """Tests for City Model."""

    def setUp(self):
        """Before all tests, add sample city & users"""

        Cafe.query.delete()
        City.query.delete()

        sf = City(**CITY_DATA)
        db.session.add(sf)

        cafe = Cafe(**CAFE_DATA)
        db.session.add(cafe)

        db.session.commit()

        self.cafe = cafe

    def tearDown(self):
        """After each test, remove all cafes."""

        Cafe.query.delete()
        City.query.delete()
        db.session.commit()

    # depending on how you solve exercise, you may have things to test on
    # the City model, so here's a good place to put that stuff.


#######################################
# cafes


class CafeModelTestCase(TestCase):
    """Tests for Cafe Model."""

    def setUp(self):
        """Before all tests, add sample city & users"""

        Cafe.query.delete()
        City.query.delete()

        sf = City(**CITY_DATA)
        db.session.add(sf)

        cafe = Cafe(**CAFE_DATA)
        db.session.add(cafe)

        db.session.commit()

        self.cafe = cafe

    def tearDown(self):
        """After each test, remove all cafes."""

        Cafe.query.delete()
        City.query.delete()
        db.session.commit()

    def test_get_city_state(self):
        self.assertEqual(self.cafe.get_city_state(), "San Francisco, CA")


class CafeViewsTestCase(TestCase):
    """Tests for views on cafes."""

    def setUp(self):
        """Before all tests, add sample city & users"""

        User.query.delete()
        Cafe.query.delete()
        City.query.delete()


        sf = City(**CITY_DATA)
        db.session.add(sf)

        cafe = Cafe(**CAFE_DATA)
        db.session.add(cafe)

        db.session.flush()

        db.session.commit()

        self.cafe_id = cafe.id

    def tearDown(self):
        """After each test, remove all cafes."""

        db.session.rollback()

    def test_list(self):
        with app.test_client() as client:
            resp = client.get("/cafes")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Test Cafe", resp.data)

    def test_detail(self):
        with app.test_client() as client:
            resp = client.get(f"/cafes/{self.cafe_id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Test Cafe", resp.data)
            self.assertIn(b'testcafe.com', resp.data)


class CafeAdminViewsTestCase(TestCase):
    """Tests for add/edit views on cafes."""

    def setUp(self):
        """Before each test, add sample city, users, and cafes"""

        Cafe.query.delete()
        City.query.delete()
        User.query.delete()

        sf = City(**CITY_DATA)
        db.session.add(sf)

        user = User.register(**TEST_USER_DATA)

        #create an admin
        admin = User.register(**ADMIN_USER_DATA)

        db.session.add_all([user, admin])

        cafe = Cafe(**CAFE_DATA)

        db.session.add(cafe)

        db.session.commit()

        self.user_id = user.id
        self.admin_id = admin.id
        self.cafe_id = cafe.id

    def tearDown(self):
        """After each test, delete the cities."""

        db.session.rollback()

    def test_logged_out_add_render(self):
        with app.test_client() as client:
            resp = client.get("/cafes/add", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access Denied', html)


    def test_logged_out_add(self):
        with app.test_client() as client:
            resp = client.post(
                "/cafes/add",
                data=CAFE_DATA_EDIT,
                follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn('Access Denied', html)

    def test_add_cafe_non_admin_page_render(self):
        with app.test_client() as client:
            login_for_test(client, self.user_id)

            resp = client.get("/cafes/add", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access Denied", html)


    def test_add_cafe_non_admin(self):
        with app.test_client() as client:
            login_for_test(client, self.user_id)

            resp = client.post(
                f"/cafes/add",
                data=CAFE_DATA_EDIT,
                follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access Denied', html)

    def test_add_cafe_page_admin(self):
        with app.test_client() as client:
            login_for_test(client, self.admin_id)

            resp = client.get(f"/cafes/add")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add Cafe', html)


    def test_add_cafe_admin(self):
        with app.test_client() as client:
            login_for_test(client, self.admin_id)

            resp = client.post(
                f"/cafes/add",
                data=CAFE_DATA_EDIT,
                follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Added', html)

    def test_dynamic_cities_vocab(self):
        id = self.cafe_id

        # the following is a regular expression for the HTML for the drop-down
        # menu pattern we want to check for
        choices_pattern = re.compile(
            r'<select [^>]*name="city_code"[^>]*><option [^>]*value="sf">' +
            r'San Francisco</option></select>')

        with app.test_client() as client:
            login_for_test(client, self.admin_id)

            resp = client.get(f"/cafes/add")
            self.assertRegex(resp.data.decode('utf8'), choices_pattern)

            resp = client.get(f"/cafes/{id}/edit")
            self.assertRegex(resp.data.decode('utf8'), choices_pattern)

    def test_logged_out_edit_render(self):
        with app.test_client() as client:
            id = self.cafe_id
            resp = client.get(f"/cafes/{id}/edit", follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access Denied', html)


    def test_logged_out_edit(self):
        with app.test_client() as client:
            id = self.cafe_id
            resp = client.post(
                f"/cafes/{id}/edit",
                data=CAFE_DATA_EDIT,
                follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn('Access Denied', html)

    def test_edit_cafe_non_admin_page_render(self):
        with app.test_client() as client:
            login_for_test(client, self.user_id)
            id = self.cafe_id
            resp = client.get(f"/cafes/{id}/edit", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access Denied", html)


    def test_edit_cafe_non_admin(self):
        with app.test_client() as client:
            login_for_test(client, self.user_id)
            id = self.cafe_id
            resp = client.post(
                f"/cafes/{id}/edit",
                data=CAFE_DATA_EDIT,
                follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access Denied', html)

    def test_edit_cafe_page_admin(self):
        with app.test_client() as client:
            login_for_test(client, self.admin_id)
            id = self.cafe_id
            resp = client.get(f"/cafes/{id}/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Edit', html)


    def test_edit_cafe_admin(self):
        with app.test_client() as client:
            login_for_test(client, self.admin_id)
            id = self.cafe_id
            resp = client.post(
                f"/cafes/{id}/edit",
                data=CAFE_DATA_EDIT,
                follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Edited', html)


#######################################
# users


class UserModelTestCase(TestCase):
    """Tests for the user model."""

    def setUp(self):
        """Before each test, add sample users."""
        User.query.delete()

        user = User.register(**TEST_USER_DATA)
        db.session.add(user)
        db.session.commit()


        self.user = user

    def tearDown(self):
        """After each test, remove all users."""

        db.session.rollback()


    def test_authenticate(self):
        rez = User.authenticate("test", "secret")
        self.assertEqual(rez, self.user)

    def test_authenticate_fail(self):
        rez = User.authenticate("no-such-user", "secret")
        self.assertFalse(rez)

        rez = User.authenticate("test", "password")
        self.assertFalse(rez)

    def test_full_name(self):
        self.assertEqual(self.user.get_full_name(), "Testy MacTest")

    def test_register(self):
        u = User.register(**TEST_USER_DATA)
        # test that password gets bcrypt-hashed (all start w/$2b$)
        self.assertEqual(u.hashed_password[:4], "$2b$")
        db.session.rollback()


class AuthViewsTestCase(TestCase):
    """Tests for views on logging in/logging out/registration."""

    def setUp(self):
        """Before each test, add sample users."""
        User.query.delete()

        user = User.register(**TEST_USER_DATA)
        db.session.add(user)

        db.session.commit()

        self.user_id = user.id


    def tearDown(self):
        """After each test, remove all users."""
        db.session.rollback()

    def test_signup(self):
        with app.test_client() as client:
            resp = client.get("/signup")
            self.assertIn(b'Sign Up', resp.data)

            resp = client.post(
                "/signup",
                data=TEST_USER_DATA_NEW,
                follow_redirects=True,
            )

            self.assertIn(b"You are signed up and logged in.", resp.data)
            self.assertTrue(session.get(CURR_USER_KEY))

    def test_signup_username_taken(self):
        with app.test_client() as client:
            resp = client.get("/signup")
            self.assertIn(b'Sign Up', resp.data)

            # signup with same data as the already-added user
            resp = client.post(
                "/signup",
                data=TEST_USER_DATA,
                follow_redirects=True,
            )

            self.assertIn(b"Username already exists.", resp.data)

    def test_login(self):
        with app.test_client() as client:
            resp = client.get("/login")
            self.assertIn(b'Welcome Back!', resp.data)

            resp = client.post(
                "/login",
                data={"username": "test", "password": "WRONG"},
                follow_redirects=True,
            )

            self.assertIn(b"Invalid credentials", resp.data)

            resp = client.post(
                "/login",
                data={"username": "test", "password": "secret"},
                follow_redirects=True,
            )

            self.assertIn(b"Hello, test", resp.data)
            self.assertEqual(session.get(CURR_USER_KEY), self.user_id)

    def test_logout(self):
        with app.test_client() as client:
            login_for_test(client, self.user_id)
            resp = client.post("/logout", follow_redirects=True)

            self.assertIn(b"successfully logged out", resp.data)
            self.assertEqual(session.get(CURR_USER_KEY), None)


class NavBarTestCase(TestCase):
    """Tests navigation bar."""

    def setUp(self):
        """Before tests, add sample user."""

        User.query.delete()

        user = User.register(**TEST_USER_DATA)


        db.session.commit()

        self.user_id = user.id

    def tearDown(self):
        """After tests, remove all users."""
        db.session.rollback()


    def test_logged_out_navbar(self):
        with app.test_client() as client:
            resp = client.get("/cafes")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Log In', html)
            self.assertNotIn('Log Out', html)

    def test_logged_in_navbar(self):
        with app.test_client() as client:
            login_for_test(client, self.user_id)
            resp = client.get("/cafes")

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('Log In', html)
            self.assertIn('Log Out', html)


class ProfileViewsTestCase(TestCase):
    """Tests for views on user profiles."""

    def setUp(self):
        """Before each test, add sample user."""

        User.query.delete()

        user = User.register(**TEST_USER_DATA)

        db.session.commit()

        self.user_id = user.id

    def tearDown(self):
        """After each test, remove all users."""

        db.session.rollback()

    def test_anon_profile(self):
        with app.test_client() as client:
            resp = client.get("/profile", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are not logged in.', html)

    def test_logged_in_profile(self):
        with app.test_client() as client:
            login_for_test(client, self.user_id)
            resp = client.get("/profile", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Edit Your Profile', html)

    def test_anon_profile_edit(self):
        with app.test_client() as client:
            resp = client.get("/profile/edit", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are not logged in.', html)


    def test_logged_in_profile_edit(self):
        with app.test_client() as client:
            login_for_test(client, self.user_id)
            resp = client.get("/profile/edit", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Edit Profile', html)


#######################################
# likes


class LikeViewsTestCase(TestCase):
    """Tests for views on cafes."""

    def setUp(self):
        """Before each test, add sample city, users, and cafes"""

        Like.query.delete()
        Cafe.query.delete()
        City.query.delete()
        User.query.delete()

        sf = City(**CITY_DATA)
        db.session.add(sf)

        user = User.register(**TEST_USER_DATA)
        db.session.add(user)

        cafe = Cafe(**CAFE_DATA)
        db.session.add(cafe)

        db.session.commit()

        self.user_id = user.id
        self.cafe_id = cafe.id

    def tearDown(self):
        """reset everything after every test"""
        Like.query.delete()
        db.session.commit()

    def test_no_likes(self):
        with app.test_client() as client:
            login_for_test(client, self.user_id)

            resp = client.get(f"/profile", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('no liked cafes', html)

    def test_user_profile_likes(self):
        with app.test_client() as client:
            login_for_test(client, self.user_id)

            like = Like(user_id=self.user_id, cafe_id=self.cafe_id)
            db.session.add(like)
            db.session.commit()

            resp = client.get(f"/profile", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Test Cafe', html)

    def test_api_likes(self):
        """test like api for when user is logged out and logged in"""
        with app.test_client() as client:

            resp = client.get(f"/api/likes?cafe_id={self.cafe_id}")
            self.assertEqual(resp.json, {"error": "Not logged in"})

            login_for_test(client, self.user_id)
            like = Like(user_id=self.user_id, cafe_id=self.cafe_id)
            db.session.add(like)
            db.session.commit()

            resp = client.get(f"/api/likes?cafe_id={self.cafe_id}")
            self.assertEqual(resp.json, {"likes": True})

    def test_api_like(self):
        """test liking a cafe when a user is logged out and logged in"""
        with app.test_client() as client:
            json = {"cafe_id": self.cafe_id}

            resp = client.post(f"/api/like", json=json)

            self.assertEqual(resp.json, {"error": "Not logged in"})

            login_for_test(client, self.user_id)

            resp = client.post(f"/api/like", json=json)
            self.assertEqual(resp.json, {"liked": self.cafe_id})

    def test_api_unlike(self):
        """test unliking a cafe when a user is logged out and logged in"""
        with app.test_client() as client:

            like = Like(user_id=self.user_id, cafe_id=self.cafe_id)
            db.session.add(like)
            db.session.commit()
            json = {"cafe_id": self.cafe_id}
            resp = client.post(f"/api/unlike", json=json)
            self.assertEqual(resp.json, {"error": "Not logged in"})

            login_for_test(client, self.user_id)

            resp = client.post(f"/api/unlike", json=json)
            self.assertEqual(resp.json, {"unliked": self.cafe_id})

