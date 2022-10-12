"""Tests for all user routes."""

import os
from unittest import TestCase
from models import db, User, Comment, Favorite, Site

os.environ['DATABASE_URL'] = "postgresql:///safer_sex_nyc_test"

from app import app

app.config['TESTING'] = True

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserRoutesTestCase(TestCase):
    """Test all routes related to user accounts."""

    def setUp(self):

        User.query.delete()
        Site.query.delete()
        Comment.query.delete()
        Favorite.query.delete()

        u = User.register(username="testuser",
            first_name="First",
            last_name="Last",
            email="test@email.com",
            zip_code="10001",
            password="HASHED_PASSWORD")

        u2 = User.register(username="testuser2",
            first_name="FirstName",
            last_name="LastName",
            email="test2@email.com",
            zip_code="11237",
            password="PASSWORD")

        s = Site(name="Name",
            service_category="Service Category",
            service_type="Service Type",
            building_number="Building Number",
            partner_type="Partner Type",
            partner_type_detailed="Partner Type Detailed",
            address="123 Main St",
            address_2="Address 2",
            borough="Manhattan",
            zip_code="10001",
            latitude=40.776676,
            longitude=-73.971321,
            phone="212-555-1234",
            additional_info="Additional Info",
            start_date="Start Date",
            end_date="End Date",
            monday="10:00 AM - 05:00 PM",
            tuesday="10:00 AM - 05:00 PM",
            wednesday="10:00 AM - 05:00 PM",
            thursday="10:00 AM - 05:00 PM",
            friday="10:00 AM - 05:00 PM",
            saturday="10:00 AM - 05:00 PM",
            sunday="10:00 AM - 05:00 PM",
            condoms_male=True,
            fc2_female_insertive_condoms=False,
            lubricant=True,
            facility_type="Facility Type",
            website="www.website.com")
        
        db.session.add(u)
        db.session.add(u2)
        db.session.add(s)
        db.session.commit()

        c = Comment(username=u.username, site_id=s.id, content="This is a test comment.", private=False)

        f = Favorite(username=u.username, site_id=s.id)

        
        db.session.add(c)
        db.session.add(f)
        db.session.commit()

        self.client = app.test_client()

        self.user = u
        self.user2 = u2
        self.site = s
        self.comment = c
        self.favorite = f
        

    def tearDown(self):
        """Clean up any fouled transactions"""
        db.session.rollback()
    
    def test_homepage_not_logged_in(self):
        """Does this route display the homepage if user not logged in?"""
        with self.client as c:
            resp = c.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<button>Register</button>", html)

    def test_homepage(self):
        """Does this route display the search page if user logged in?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = self.user.username
            resp = c.get('/', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Search by borough:", html)
            self.assertIn("Logout", html)
        
    def test_login_get(self):
        """Does this route display the login page if no user is logged in?"""
        with self.client as c:
            resp = c.get('/login')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Username", html)
            self.assertIn("<input", html)
    
    def test_login_post(self):
        """Does this route display the user profile upon successful login?"""
        with self.client as c:
            resp = c.post('/login', data={"username":"testuser", "password":"HASHED_PASSWORD"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("My Favorite Sites", html)
            self.assertIn("Welcome back, First!", html)

    def test_login_post_invalid_credentials(self):
        """Does this route display the user profile upon successful login?"""
        with self.client as c:
            resp = c.post('/login', data={"username":"testuser", "password":"PASSWORD"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid login. Please try again.", html)
            self.assertIn("</form>", html)

    def test_login_when_logged_in(self):
        """Does this route display the search page if user already logged in?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = self.user.username
            resp = c.get('/login', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Search by borough:", html)
            self.assertIn("Logout", html)

    def test_logout(self):
        """Does this route remove "username" from session and display the homepage?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = self.user.username
            resp = c.post('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<button>Register</button>", html)
            self.assertIn("Anonymous Search", html)
        
    def test_user_register_get(self):
        """Does this route display the registration form if no user is logged in?"""
        with self.client as c:
            resp = c.get('/users/register')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("New User Registration", html)
            self.assertIn("CONFIRM PASSWORD", html)
            self.assertIn("<input", html)

    def test_user_register_post(self):
        """Does this route create a new user and redirect to the user's profile page?"""
        with self.client as c:
            resp = c.post('/users/register', data={"username":"testuser3", "first_name":"fname", "last_name":"lname", "email":"email@test.com", "zip_code":"10001", "password":"PASSWORD", "confirm-password-input":"PASSWORD"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            user = User.query.get("testuser2")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("My Favorite Sites", html)
            self.assertIn("fname lname", html)
            self.assertIn("Update/Delete Your Profile", html)
            self.assertIsInstance(user, User)
    
    def test_user_register_post_invalid_password_confirmation(self):
        """Does this route confirm password entry?"""
        with self.client as c:
            resp = c.post('/users/register', data={"username":"testuser3", "first_name":"fname", "last_name":"lname", "email":"email@test.com", "zip_code":"10001", "password":"PASSWORD", "confirm-password-input":"PASS"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("</form>", html)
            self.assertIn("Password entry does not match. Please try again", html)

    def test_user_register_post_duplicate_user(self):
        """Does this route prevent duplicate user information?"""
        with self.client as c:
            resp = c.post('/users/register', data={"username":"testuser", "first_name":"fname", "last_name":"lname", "email":"email@test.com", "zip_code":"10001", "password":"PASSWORD", "confirm-password-input":"PASSWORD"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("</form>", html)
            self.assertIn("That username or email is already in use. Please choose another.", html)

    def test_user_profile_page(self):
        """Does this route display user information for the current user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = self.user.username
            resp = c.get(f'/users/{self.user.username}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("My Favorite Sites", html)
            self.assertIn("This is a test comment.", html)
            self.assertIn("Manhattan", html)

    def test_user_profile_page_not_logged_in(self):
        """Does this route display login page if user not logged in?"""
        with self.client as c:
            resp = c.get(f'/users/{self.user.username}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Please login to view that page.", html)
            self.assertIn("<input", html)

    def test_user_profile_page_different_user(self):
        """Does this route redirect to display current user information if user tries to view another user's profile?""" 
        with self.client as c:        
            with c.session_transaction() as sess:
                sess["username"] = self.user2.username            
            resp = c.get('/users/testuser', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("My Favorite Sites", html)
            self.assertIn("You are not authorized to access that page.", html)
            self.assertNotIn("This is a test comment.", html)
            self.assertNotIn("Manhattan", html)
    
    def test_user_update_get(self):
        """Does this route display the update form for the current user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = self.user.username
            resp = c.get(f'users/{self.user.username}/update')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Update Your Profile", html)
            self.assertIn("</form>", html)
            self.assertIn("First", html)
    
    def test_user_update_post(self):
        """Does this route update user information for the current user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = self.user.username
            resp = c.post(f'users/{self.user.username}/update', data={"username":"newUserName", "first_name":"fname", "last_name":"lname", "email":"email@test.com", "zip_code":"10001", "password":"HASHED_PASSWORD"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("newUserName", html)
            self.assertIn("Your profile has been updated.", html)
            self.assertNotIn("First", html)

    def test_user_update_get_not_logged_in(self):
        """Does this route display the homepage if a user is not logged in?"""
        with self.client as c:
            resp = c.get(f'users/{self.user.username}/update', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("You are not authorized to access that page.", html)
            self.assertIn("Anonymous Search", html)

    def test_user_update_get_different_user(self):
        """Does this route display the search page if the current user is not the user to update?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = self.user2.username
            resp = c.get('users/testuser/update', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("You are not authorized to access that page.", html)
            self.assertIn("Search by borough:", html)

    def test_user_update_post_wrong_password(self):
        """Does this route redirect to update form if passwords do not match?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = self.user.username
            resp = c.post(f'users/{self.user.username}/update', data={"username":"newUserName", "first_name":"fname", "last_name":"lname", "email":"email@test.com", "zip_code":"10001", "password":"PASSWORD"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid password. Please try again", html)
            self.assertIn("</form>", html)

    def test_user_update_post_taken_username(self):
        """Does this route redirect to update form if username is taken?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = self.user.username
            resp = c.post(f'users/{self.user.username}/update', data={"username":"testuser2", "first_name":"fname", "last_name":"lname", "email":"email@test.com", "zip_code":"10001", "password":"HASHED_PASSWORD"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("That username or email is already in use. Please choose another.", html)
            self.assertIn("</form>", html)

    def test_user_password_update_get(self):
        """Does this route display the update form for the current user to change their password?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = self.user.username
            resp = c.get(f'users/{self.user.username}/update/password')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("NEW PASSWORD:", html)
            self.assertIn("In order to change your password, please confirm your username", html)

    def test_user_password_update_post(self):
        """Does this route update password information for the current user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = self.user.username
            resp = c.post(f'users/{self.user.username}/update/password', data={"username":"testuser", "password":"HASHED_PASSWORD", "new-password-input":"password123", "confirm-password-input":"password123"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", html)
            self.assertIn("Your password has been changed.", html)
            self.assertIn("First Last", html)
            self.assertNotEqual(User.authenticate(username="testuser", password="password123"), False)

    def test_user_password_update_get_not_logged_in(self):
        """Does this route display the homepage if a user is not logged in?"""
        with self.client as c:
            resp = c.get(f'users/{self.user.username}/update/password', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("You are not authorized to access that page.", html)
            self.assertIn("Anonymous Search", html)
    
    def test_user_password_update_get_different_user(self):
        """Does this route display the search page if a user tries to access another user's update page?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = self.user2.username
            resp = c.get('users/testuser/update/password', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("You are not authorized to access that page.", html)
            self.assertIn("Search by borough:", html)

    def test_user_password_update_post_wrong_password(self):
        """Does this route display error if current password is not correct?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = self.user.username
            resp = c.post(f'users/{self.user.username}/update/password', data={"username":"testuser", "password":"PASSWORD", "new-password-input":"password123", "confirm-password-input":"password123"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("</form>", html)
            self.assertIn("Invalid username/password combination. Please try again.", html)
