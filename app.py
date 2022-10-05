"""SaferSexNYC application."""

from flask import Flask, request, redirect, render_template, flash, session, g
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Comment, Favorite, Site
from forms import RegisterForm, LoginForm, UpdateUserForm, CommentForm
from secret import api_app_token
from sqlalchemy.exc import IntegrityError
import pandas as pd
from sodapy import Socrata

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///safer_sex_nyc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'secretkey'

# debug = DebugToolbarExtension(app)

connect_db(app)

@app.before_request
def add_user_to_global():

    if session.get("username"):
        g.user = User.query.get(session["username"])
    
    else:
        g.user = None

def check_login():
    """Determine if a user is currently logged-in. If so, return that user object.  If not, return False."""

    if session.get("username"):
        id = session["username"]
        user = User.query.get_or_404(id)
        return user
    else:
        return False

# def login_required(f):
#     @wraps(f)
#     def wrap(*args, **kwargs):
#         if "username" in session:
#             return f(*args, **kwargs)
#         else:
#             flash("You must login to view that page.", "warning")
#             return redirect("/login")
        
#     return wrap

@app.route("/")
def display_homepage():
    """Display the homepage of the application."""

    if check_login():
        return redirect("/sites")
    return render_template("homepage.html")


@app.route("/login", methods=["GET", "POST"])
def log_in_user():
    """On GET -> Display login form
    On POST -> Validate user login credentials, if valid save user to session."""

    if check_login():
        return redirect("/sites")
    
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username
            flash(f"Welcome back, {user.first_name}!", "success")
            return redirect(f"/users/{user.username}")
        
        else:
            form.username.errors=["Invalid login. Please try again."]
    
    return render_template("login.html", form=form)


@app.route("/logout", methods=["POST"])
def log_out_user():
    """Logout current user."""

    session.pop("username")
    return redirect("/")


################## User Routes ##################

@app.route("/users/register", methods=["GET", "POST"])
def create_new_user():
    """On GET -> Display form for new user registration.
    On POST -> Process new user registration, login new user."""

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        zip_code = int(form.zip_code.data)
        password = form.password.data

        new_user = User.register(username=username, first_name=first_name, last_name=last_name, email=email, zip_code=zip_code, password=password)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('That username is already in use. Please choose another.')
            return redirect("/users/register")
        
        session["username"] = new_user.username

        return redirect("/")
    
    return render_template("register.html", form=form)


@app.route("/users/<username>")
def display_user_detail(username):
    """Display user details if a current user is logged in."""

    if check_login():
        user = User.query.get_or_404(username)
        return render_template("user-detail.html", user=user)
    else:
        flash(f"Please login to view that page.", "warning")
        return redirect("/login")

    

@app.route("/users/<username>/update", methods=["GET", "POST"])
def display_user_edit_form(username):
    """On GET -> Display the user edit form for the specified user if that user is logged in.
    On POST -> Process changes to user profile."""

    user = User.query.get_or_404(username)
    form = UpdateUserForm(obj=user)

    if form.validate_on_submit():
        username = session.get("username")
        password = request.form["password"]

        this_user = User.authenticate(username, password)
        
        if this_user:
            this_user.username = form.username.data
            this_user.first_name = form.first_name.data
            this_user.last_name = form.last_name.data
            this_user.email = form.email.data
            this_user.zip_code = form.zip_code.data

            db.session.commit()

            session["username"] = this_user.username

            return redirect(f"/users/{this_user.username}")

        else:
            form.username.errors=["Invalid password. Please try again"]

    if check_login() == user:
        return render_template("user-update.html", form=form, user=user)

    else:
        flash("You are not authorized to access that page.", "danger")
        return redirect(f"/users/{session.get('username')}")

@app.route("/users/<username>/delete", methods=["GET", "POST"])
def delete_user(username):

    user = User.query.get_or_404(username)
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        this_user = User.authenticate(username, password)

        if this_user:
            db.session.delete(this_user)
            db.session.commit()

            session.pop("username")

            flash(f"Your account has been deleted.", "success")
            return redirect("/")
        
        else:
            form.password.errors=["Invalid username/password combination. Please try again"]
    
    if check_login() == user:
        return render_template("user-delete.html", form=form, user=user)

    else:
        flash("You are not authorized to access that page.", "danger")
        return redirect(f"/users/{session.get('username')}")



################## Site Routes ##################

client = Socrata("data.cityofnewyork.us", api_app_token)
api_ext = "4kpn-sezh"

@app.route("/sites")

@app.route("/sites/search")
def display_site_search():
    """Display site search page."""

    return render_template("site-search.html")


@app.route("/sites/<int:site_id>")
def display_site_details(site_id):
    """Obtain site information from the API and display for user interaction."""

    form = CommentForm()

    if g.user:
        favorite = Favorite.query.filter(Favorite.site_id==site_id, Favorite.username==g.user.username).one_or_none()
    
    else:
        favorite = None

    result = client.get(api_ext, limit=1, site_id=site_id)
    site = result[0]

    comments = Comment.query.filter_by(site_id=site_id)

    return render_template("site-detail.html", site=site, comments=comments, form=form, favorite=favorite)


@app.route("/sites/<int:site_id>/favorite", methods=["POST"])
def create_favorite(site_id):
    """Create a new favorite association between a user and a site."""

    user = check_login()

    if user:
        site_name = request.form['site_name']
        site_address = request.form['site_address']

        new_favorite = Favorite(username=user.username, site_id=site_id, site_name=site_name, site_address=site_address)

        db.session.add(new_favorite)
        db.session.commit()

        return redirect(f"/sites/{site_id}")

    else:
        flash(f"Please login to view that page.", "warning")
        return redirect("/login")    


@app.route("/sites/<int:site_id>/favorite/delete", methods=["POST"])
def delete_favorite(site_id):
    """Delete a favorite association between a user and a site."""

    user = check_login()

    if user:

        Favorite.query.filter(Favorite.site_id==site_id, Favorite.username==user.username).delete()

        db.session.commit()

        return redirect(f"/sites/{site_id}")

    else:
        flash(f"Please login to view that page.", "warning")
        return redirect("/login")


################## Comment Routes ##################

@app.route("/sites/<int:site_id>/comments", methods=["GET", "POST"])
def create_comment(site_id):
    """On GET -> Display new comment form.
    On POST -> Save new comment to database."""

    user = check_login()

    if user:

        form = CommentForm()

        if form.validate_on_submit():
            content = form.content.data
            private = form.private.data

            result = client.get(api_ext, limit=1, site_id=site_id)
            site = result[0]

            site_name = site['sitename']
            site_address = site['address']

            new_comment = Comment(username=user.username, site_id=site_id, content=content, private=private, site_name=site_name, site_address=site_address)

            db.session.add(new_comment)
            db.session.commit()



            return redirect(f"/sites/{site_id}")
        
        else:
            return render_template("comment-form.html", form=form)

    else:
        flash(f"Please login to view that page.", "warning")
        return redirect("/login")


@app.route("/comments/<int:comment_id>/update", methods=["GET", "POST"])
def update_comment(comment_id):
    """On GET -> Display comment update form.
    On POST -> Save updates to comment.
    """

    user = check_login()

    if user:

        comment = Comment.query.get_or_404(comment_id)
        form = CommentForm(obj=comment)

        if comment.username == user.username:

            if form.validate_on_submit():

                content = form.content.data
                private = form.private.data

                comment.content = content
                comment.private = private

                db.session.commit()

                flash("Your comment has been updated successfully.", "success")
                return redirect(f"/sites/{comment.site_id}")

            else:
                return render_template("comment-form.html", form=form)

        else:
            flash(f"You must be the owner of that comment to edit it.", "warning")
            return redirect("/login")
    
    else:
        flash(f"Please login to view that page.", "warning")
        return redirect("/login")


@app.route("/comments/<int:comment_id>/delete", methods=["POST"])
def delete_comment(comment_id):
    """Delete a comment from the database"""

    user = check_login()

    if user:

        comment = Comment.query.get_or_404(comment_id)

        if comment.username == user.username:

            site_id = comment.site_id
            db.session.delete(comment)
            db.session.commit()

            flash("Your comment has been deleted successfully.", "success")
            return redirect(f"/sites/{site_id}")

        else:
            flash("You must be the owner of that comment to delete it.", "warning")
            return redirect("/login")
    
    else:
        flash("Please login to view that page.", "warning")
        return redirect("/login")