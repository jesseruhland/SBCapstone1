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
    """Tests for User model"""

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
    
    def test_user_change_password(self):
        """Does User.change_password successfully return a user given valid input?
        Does User.change_password successfully change the user's password?
        Does User.change_password fail to return a user when the password is invalid?
        """

        u = User.register(username="testuser", first_name="First", last_name="Last", email="test@email.com", zip_code="10001", password="HASHED_PASSWORD")

        db.session.add(u)
        db.session.commit()

        user = User.change_password(username="testuser", password="HASHED_PASSWORD", new_password="NEW_password")

        not_user = User.change_password(username="testuser", password="PASSWORD", new_password="NEW_password")

        not_user2 = User.change_password(username="test", password="HASHED_PASSWORD", new_password="NEW_password")

        db.session.commit()

        user_with_new_password = User.authenticate(username="testuser", password="NEW_password")

        not_user3 = User.authenticate(username="testuser", password="HASHED_PASSWORD")

        self.assertEqual(u, user)
        self.assertEqual(u, user_with_new_password)
        self.assertIsInstance(user, User)
        self.assertIsInstance(user_with_new_password, User)
        self.assertEqual(not_user, False)
        self.assertNotIsInstance(not_user, User)
        self.assertEqual(not_user2, False)
        self.assertNotIsInstance(not_user2, User)
        self.assertEqual(not_user3, False)
        self.assertNotIsInstance(not_user3, User)

class SiteModelTestCase(TestCase):
    """Tests for Site model"""

    def setUp(self):
        """Create test client"""
        
        Site.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transactions"""
        db.session.rollback()

    def test_site_model(self):
        """Does basic model work? Does the repr method work as expected?"""

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

        db.session.add(s)
        db.session.commit()

        # s should be an instance of Site class and should not have any comments or favorites.
        self.assertIsInstance(s, Site)
        self.assertEqual(s.borough, "Manhattan")
        self.assertEqual(s.condoms_male, True)
        self.assertEqual(len(s.comments),0)
        self.assertEqual(len(s.fav_users),0)
        self.assertEqual(repr(s), f"<Site id:{s.id}, name:{s.name}>")


class CommentModelTestCase(TestCase):
    """Tests for Comment model"""

    def setUp(self):
        """Create test client"""
        
        User.query.delete()
        Site.query.delete()
        Comment.query.delete()

        u = User(username="testuser",
            first_name="First",
            last_name="Last",
            email="test@email.com",
            zip_code="10001",
            password="HASHED_PASSWORD")

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
        db.session.add(s)
        db.session.commit()

        self.client = app.test_client()

        self.user = u
        self.site = s

    def tearDown(self):
        """Clean up any fouled transactions"""
        db.session.rollback()

    def test_comment_model(self):
        """Does basic model work? Does the repr method work as expected?"""

        c = Comment(username=self.user.username, site_id=self.site.id, content="This is a test comment.", private=False)

        db.session.add(c)
        db.session.commit()

        # c should be an instance of Comment class and should have a database relationship to user and site.
        self.assertIsInstance(c, Comment)
        self.assertEqual(c.user, self.user)
        self.assertEqual(len(self.user.comments),1)
        self.assertEqual(c.user.zip_code, 10001)
        self.assertEqual(c.site, self.site)
        self.assertEqual(len(self.site.comments),1)
        self.assertEqual(c.site.latitude, 40.776676)
        self.assertEqual(repr(c), f"<Comment id:{c.id}, username:{c.username}, private?:{c.private}>")

class FavoriteModelTestCase(TestCase):
    """Tests for Favorite model"""

    def setUp(self):
        """Create test client"""
        
        User.query.delete()
        Site.query.delete()
        Comment.query.delete()

        u = User(username="testuser",
            first_name="First",
            last_name="Last",
            email="test@email.com",
            zip_code="10001",
            password="HASHED_PASSWORD")

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
        db.session.add(s)
        db.session.commit()

        self.client = app.test_client()

        self.user = u
        self.site = s

    def tearDown(self):
        """Clean up any fouled transactions"""
        db.session.rollback()

    def test_favorite_model(self):
        """Does basic model work? Does the repr method work as expected?"""

        f = Favorite(username=self.user.username, site_id=self.site.id)

        db.session.add(f)
        db.session.commit()

        # f should be an instance of Favorite class and should have a database relationship to user and site.
        self.assertIsInstance(f, Favorite)
        self.assertEqual(f.username, self.user.username)
        self.assertEqual(len(self.user.fav_sites),1)
        self.assertEqual(f.site_id, self.site.id)
        self.assertEqual(len(self.site.fav_users),1)
        self.assertEqual(repr(f), f"<Favorite Relationship username:{f.username}, facility:{f.site_id}>")


