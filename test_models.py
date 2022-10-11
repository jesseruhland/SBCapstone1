"""Tests for all models."""

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Comment, Favorite, Site

os.environ['DATABASE_URL'] = "postgresql:///safer_sex_nyc_test"

from app import app

app.config['TESTING'] = True

db.create_all()

class UserModelTestCase(TestCase):
    """Tests for user model"""

    def setUp(self):
        """Create test client"""
        
        User.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transactions"""
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work? Does the repr method work as expected?"""

        u = User(username="testuser", first_name="First", last_name="Last", email="test@email.com", zip_code="10001", password="HASHED_PASSWORD")

        db.session.add(u)
        db.session.commit()

        # u should be an instance of User class and should not have any comments or favorites.
        self.assertIsInstance(u, User)
        self.assertEqual(len(u.comments),0)
        self.assertEqual(len(u.fav_sites),0)
        self.assertEqual(repr(u), f"<User username:{u.username}>")

    def test_user_register(self):
        """Does User.register successfully create a new user given valid credentials?"""

        u = User.register(username="testuser", first_name="First", last_name="Last", email="test@email.com", zip_code="10001", password="HASHED_PASSWORD")

        db.session.add(u)
        db.session.commit()

        # u should be an instance of User class and should not have any comments or favorites.  Password should not match entry (should be hashed).
        self.assertIsInstance(u, User)
        self.assertEqual(len(u.comments),0)
        self.assertEqual(len(u.fav_sites),0)
        self.assertEqual(repr(u), f"<User username:{u.username}>")
        self.assertNotEqual(u.password, "HASHED_PASSWORD")

    def test_invalid_user_register(self):
        """Does User.register fail to create a new user if any of the validation (e.g. uniqueness) fail?"""

        with self.assertRaises(IntegrityError):

            u = User.register(username="testuser", first_name="First", last_name="Last", email="test@email.com", zip_code="10001", password="HASHED_PASSWORD")

            u2 = User.register(username="testuser", first_name="First", last_name="Last", email="test@email.com", zip_code="10001", password="HASHED_PASSWORD")

            db.session.add(u)
            db.session.add(u2)
            db.session.commit()

    def test_user_authenticate(self):
        """Does User.authenticate successfully return a user when given a valid username and password?
        Does User.authenticate fail to return a user when the username is invalid?
        Does User.authenticate fail to return a user when the password is invalid?
        """
        
        u = User.register(username="testuser", first_name="First", last_name="Last", email="test@email.com", zip_code="10001", password="HASHED_PASSWORD")

        db.session.add(u)
        db.session.commit()

        user = User.authenticate(username=u.username, password="HASHED_PASSWORD")

        not_user = User.authenticate(username=u.username, password="PASSWORD")

        not_user2 = User.authenticate(username='username', password="HASHED_PASSWORD")

        self.assertEqual(u, user)
        self.assertIsInstance(user, User)
        self.assertEqual(not_user, False)
        self.assertNotIsInstance(not_user, User)
        self.assertEqual(not_user2, False)
        self.assertNotIsInstance(not_user2, User)

# class CommentModelTestCase(TestCase):

# class FavoriteModelTestCase(TestCase):

# class SiteModelTestCase(TestCase):
