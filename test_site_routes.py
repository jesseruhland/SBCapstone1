"""Tests for all site routes."""

import os
from unittest import TestCase
import jsonpickle
from models import db, User, Comment, Favorite, Site

os.environ['DATABASE_URL'] = "postgresql:///safer_sex_nyc_test"

from app import app

app.config['TESTING'] = True

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class SiteRoutesTestCase(TestCase):
    """Test all routes related to sites."""

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

    def test_sites_get(self):
        """Does this route respond with JSON about the sites in the database?"""
        with self.client as c:
            resp = c.get('/sites')
            data = jsonpickle.decode(resp.get_data())

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0].borough, "Manhattan")
            self.assertIsInstance(data[0], Site)

    def test_sites_get_with_filter(self):
        """Does this route respond with JSON about the sites in the database that match the passed filters?"""
        with self.client as c:
            resp = c.get('/sites?borough=Manhattan')
            data = jsonpickle.decode(resp.get_data())

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0].borough, "Manhattan")
            self.assertIsInstance(data[0], Site)

    def test_sites_get_with_filter_expect_no_result(self):
        """Does this route respond with JSON about the sites in the database that match the passed filters?"""
        with self.client as c:
            resp = c.get('/sites?borough=Brooklyn')
            data = jsonpickle.decode(resp.get_data())

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(data), 0)

    def test_site_detail(self):
        """Does this route display site details for the specified site?"""
        with self.client as c:
            resp = c.get(f'/sites/{self.site.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Name", html)
            self.assertIn("Manhattan", html)
            self.assertNotIn("Comments", html)
            self.assertNotIn("Favorite", html)