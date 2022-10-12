"""Tests for all favorite routes."""

import os
from unittest import TestCase
from models import db, User, Comment, Favorite, Site

os.environ['DATABASE_URL'] = "postgresql:///safer_sex_nyc_test"

from app import app

app.config['TESTING'] = True

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class FavoriteRoutesTestCase(TestCase):
    """Test all routes related to routes."""

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

    def test_new_favorite(self):
        """Does this route create a new favorite association for the current user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = "testuser"
            
            site = Site.query.filter(Site.name == "Name").one_or_none()
            resp = c.post(f'sites/{site.id}/favorite')

            self.assertEqual(resp.status_code, 200)

            this_site = Site.query.filter(Site.name == "Name").one_or_none()
            user = User.query.get("testuser")

            self.assertEqual(len(user.fav_sites), 1)
            self.assertEqual(len(this_site.fav_users), 1)
            self.assertEqual(user.fav_sites[0].borough, "Manhattan")
            self.assertEqual(this_site.fav_users[0].email, "test@email.com")

    def test_new_favorite_not_logged_in(self):
        """Does this route redirect the user if there is not a logged in user?"""
        with self.client as c:
            resp = c.post(f'sites/{self.site.id}/favorite', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Please login to access that functionality.", html)

    def test_delete_favorite(self):
        """Does this route delete a favorite association for the current user?"""
        with self.client as c:
            site = Site.query.filter(Site.name == "Name").one_or_none()
            user = User.query.get("testuser")
            f = Favorite(username=user.username, site_id=site.id)
            db.session.add(f)
            db.session.commit()

            self.assertEqual(len(user.fav_sites), 1)
            self.assertEqual(len(site.fav_users), 1)

            with c.session_transaction() as sess:
                sess["username"] = "testuser"

            resp = c.post(f'sites/{site.id}/favorite/delete')

            this_user = User.query.get("testuser")
            this_site = Site.query.filter(Site.name == "Name").one_or_none()

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(this_user.fav_sites), 0)
            self.assertEqual(len(this_site.fav_users), 0)

    def test_delete_favorite_not_logged_in(self):
        """Does this route redirect the user if there is not a logged in user?"""
        with self.client as c:
            resp = c.post(f'sites/{self.site.id}/favorite/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Please login to access that functionality.", html)




