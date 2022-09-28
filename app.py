"""SaferSexNYC application."""

from flask import Flask, request, redirect, render_template, flash, session
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db
from forms import
from secret import api_app_token

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///safer_sex_nyc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'secretkey'

api_base_url = "https://data.cityofnewyork.us/resource/4kpn-sezh.json"

# debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

def check_login():
    """Determine if a user is currently logged-in. If so, return that user object.  If not, return False."""
    if session["username"]:
        id = session["username"]
        user = User.query.get_or_404(id)
        return user
    else:
        return False

@app.route("/")
def display_homepage():
    """Display the homepage of the application"""

@app.route("/register")
def display_user_form():
    """Display form for new user registration"""

@app.route("/login", methods=["GET", "POST"])
def log_in_user():
    """On GET -> Display login form
    On POST -> Validate user login credentials, if valid save user to session"""

@app.route("/logout", methods=["POST"])
def log_out_user():
    """Logout current user"""


################## User Routes ##################
@app.route("/users", methods=["POST"])
def create_user():
    """Create a new user from entered form data"""

@app.route("/users/<username>", methods=["GET", "PATCH", "DELETE"])

@app.route("/users/<username>/update", methods=["GET"])
def display_user_edit_form(username):
    """Display the user edit form for the specified user if that user is logged in."""


################## Facility Routes ##################

@app.route("/facilities")

@app.route("/facilities/<int:facility_pk>")

@app.route("/facilities/<int:facility_pk>/comments", methods=["GET", "POST"])

@app.route("/facilities/<int:facility_pk>/comments/<int:comment_id>", methods=["GET", "PATCH", "DELETE"])

@app.route("/facilities/<int:facility_pk>/favorites", method=["POST", "DELETE"])