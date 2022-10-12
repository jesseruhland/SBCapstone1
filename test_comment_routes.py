"""Tests for all comment routes."""

import os
from unittest import TestCase
from models import db, User, Comment, Favorite, Site

os.environ['DATABASE_URL'] = "postgresql:///safer_sex_nyc_test"

from app import app

app.config['TESTING'] = True

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class CommentRoutesTestCase(TestCase):
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

    def test_create_comment_get(self):
        """Does this route display the form for a new comment?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = "testuser"
            
            site = Site.query.filter(Site.name == "Name").one_or_none()
            resp = c.get(f'/sites/{site.id}/comments', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Add A Comment", html)
            self.assertIn("</form>", html)

    def test_create_comment_post(self):
        """Does this route save a new comment to the database and redirect the user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = "testuser"
            
            site = Site.query.filter(Site.name == "Name").one_or_none()
            resp = c.post(f'/sites/{site.id}/comments', data={"content":"this is another new comment", "private":False}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            this_site = Site.query.filter(Site.name == "Name").one_or_none()
            this_user = User.query.get("testuser")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("this is another new comment", html)
            self.assertIn("Manhattan", html)
            self.assertEqual(len(this_user.comments), 2)
            self.assertEqual(len(this_site.comments), 2)

    def test_create_comment_get_not_logged_in(self):
        """Does this route redirect if a user is not logged in?"""
        with self.client as c:
            resp = c.get(f'/sites/{self.site.id}/comments', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Please login to view that page.", html)
            self.assertIn("</form>", html)

    def test_create_comment_post_not_logged_in(self):
        """Does this route redirect if a user is not logged in?"""
        with self.client as c:
            resp = c.post(f'/sites/{self.site.id}/comments', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Please login to view that page.", html)
            self.assertIn("</form>", html)

    def test_update_comment_get(self):
        """Does this route display the form for to update comment?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = "testuser"
            
            comment = Comment.query.filter(Comment.username == "testuser").one_or_none()
            resp = c.get(f'/comments/{comment.id}/update', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Update A Comment", html)
            self.assertIn("</form>", html)

    def test_update_comment_post(self):
        """Does this route save an updated comment to the database and redirect the user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = "testuser"
            
            comment = Comment.query.filter(Comment.username == "testuser").one_or_none()
            resp = c.post(f'/comments/{comment.id}/update', data={"content":"this is the updated comment", "private":True}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            this_site = Site.query.filter(Site.name == "Name").one_or_none()
            this_user = User.query.get("testuser")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("this is the updated comment", html)
            self.assertIn("Manhattan", html)
            self.assertEqual(len(this_user.comments), 1)
            self.assertEqual(len(this_site.comments), 1)
    
    def test_update_comment_get_not_logged_in(self):
        """Does this route redirect if a user is not logged in?"""
        with self.client as c:
            comment = Comment.query.filter(Comment.username == "testuser").one_or_none()
            resp = c.get(f'/comments/{comment.id}/update', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Please login to view that page.", html)
            self.assertIn("</form>", html)

    def test_update_comment_post_not_logged_in(self):
        """Does this route redirect if a user is not logged in?"""
        with self.client as c:
            comment = Comment.query.filter(Comment.username == "testuser").one_or_none()
            resp = c.post(f'/comments/{comment.id}/update', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Please login to view that page.", html)
            self.assertIn("</form>", html)

    def test_update_comment_get_wrong_user(self):
        """Does this route redirect if the current user is not the owner of a comment?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = "testuser2"
            
            comment = Comment.query.filter(Comment.username == "testuser").one_or_none()
            resp = c.get(f'/comments/{comment.id}/update', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("You must be the owner of that comment to edit it.", html)
            self.assertIn("</form>", html)

    def test_update_comment_post_wrong_user(self):
        """Does this route redirect if the current user is not the owner of a comment?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = "testuser2"
            
            comment = Comment.query.filter(Comment.username == "testuser").one_or_none()
            resp = c.post(f'/comments/{comment.id}/update', data={"content":"this is the updated comment", "private":True}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("You must be the owner of that comment to edit it.", html)
            self.assertIn("</form>", html)

    def test_delete_comment_post(self):
        """Does this route delete a comment from the database?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = "testuser"
            
            comment = Comment.query.filter(Comment.username == "testuser").one_or_none()
            resp = c.post(f'/comments/{comment.id}/delete', follow_redirects=True)

            this_site = Site.query.filter(Site.name == "Name").one_or_none()
            this_user = User.query.get("testuser")

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(this_user.comments), 0)
            self.assertEqual(len(this_site.comments), 0)

    def test_update_comment_post_not_logged_in(self):
        """Does this route redirect if a user is not logged in?"""
        with self.client as c:
            comment = Comment.query.filter(Comment.username == "testuser").one_or_none()
            resp = c.post(f'/comments/{comment.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Please login to view that page.", html)
            self.assertIn("</form>", html)

    def test_update_comment_post_wrong_user(self):
        """Does this route redirect if the current user is not the owner of a comment?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["username"] = "testuser2"
            
            comment = Comment.query.filter(Comment.username == "testuser").one_or_none()
            resp = c.post(f'/comments/{comment.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("You must be the owner of that comment to delete it.", html)
            self.assertIn("</form>", html)