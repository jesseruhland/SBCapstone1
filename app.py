"""SaferSexNYC application."""

from flask import Flask, request, redirect, render_template, flash, session, g, jsonify
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Comment, Favorite, Site
from forms import RegisterForm, LoginForm, UpdateUserForm, CommentForm
from funcs import create_filters
from sqlalchemy.exc import IntegrityError
import jsonpickle
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())  # take environment variables from .env.

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///safer_sex_nyc'))
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


@app.route("/")
def display_homepage():
    """Display the homepage of the application."""

    if g.user:
        return redirect("/sites/search")

    return render_template("homepage.html")


@app.route("/login", methods=["GET", "POST"])
def log_in_user():
    """On GET -> Display login form
    On POST -> Validate user login credentials, if valid save user to session."""

    if g.user:
        return redirect("/sites/search")
    
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

    if g.user:
        return redirect(f"/users/{g.user.username}")
    
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        zip_code = int(form.zip_code.data)
        password = form.password.data
        confirm_password = request.form['confirm-password-input']

        if password != confirm_password:
            form.password.errors.append("Password entry does not match. Please try again")
            return render_template("register.html", form=form)

        new_user = User.register(username=username, first_name=first_name, last_name=last_name, email=email, zip_code=zip_code, password=password)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('That username or email is already in use. Please choose another.')
            return render_template("register.html", form=form)
        
        session["username"] = new_user.username

        return redirect(f"/users/{new_user.username}")
    
    return render_template("register.html", form=form)


@app.route("/users/<username>")
def display_user_detail(username):
    """Display user details if a current user is logged in."""

    if g.user:
        user = User.query.get_or_404(username)
        if g.user == user:
            return render_template("user-detail.html", user=user)
        else:
            flash("You are not authorized to access that page.", "danger")
            return redirect(f"/users/{g.user.username}")
    else:
        flash("Please login to view that page.", "warning")
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

            try:
                db.session.commit()
            except:
                db.session.rollback()
                form.username.errors.append('That username or email is already in use. Please choose another.')
                return render_template("user-update.html", form=form, user=user)

            session["username"] = this_user.username

            flash("Your profile has been updated.", "success")
            return redirect(f"/users/{this_user.username}")

        else:
            form.username.errors=["Invalid password. Please try again"]

    if g.user == user:
        return render_template("user-update.html", form=form, user=user)

    else:
        flash("You are not authorized to access that page.", "danger")
        return redirect("/")


@app.route("/users/<username>/update/password", methods=["GET", "POST"])
def change_user_password(username):

    user = User.query.get_or_404(username)
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        new_password = request.form['new-password-input']
        confirm_password = request.form['confirm-password-input']

        if new_password != confirm_password:
            form.password.errors=["New password entry does not match. Please try again"]
            return render_template("user-password.html", form=form, user=user)

        this_user = User.change_password(username, password, new_password)

        if this_user:
            db.session.commit()

            flash("Your password has been changed.", "success")
            return redirect(f"/users/{username}")
        
        else:
            form.password.errors=["Invalid username/password combination. Please try again."]
    
    if g.user == user:
        return render_template("user-password.html", form=form, user=user)

    else:
        flash("You are not authorized to access that page.", "danger")
        return redirect("/")


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
    
    if g.user == user:
        return render_template("user-delete.html", form=form, user=user)

    else:
        flash("You are not authorized to access that page.", "danger")
        return redirect("/")



################## Site Routes ##################

@app.route("/sites")
def return_search_results():
    """Return search results in JSON based on query."""

    query = Site.query
    filters = create_filters(request.args)
    
    if len(filters) != 0:
        result = query.filter(*filters).all()
    else:
        result = query.all()

    resultjson = jsonpickle.encode(result)

    return resultjson, 200


@app.route("/sites/search")
def display_site_search():
    """Display site search page."""

    return render_template("site-search.html")


@app.route("/sites/<int:site_id>")
def display_site_details(site_id):
    """Display information for a particular site."""

    site = Site.query.get_or_404(site_id)

    mapboxAccessToken = os.getenv('MAPBOX_ACCESS_TOKEN')
    return render_template("site-detail.html", site=site, mapboxAccessToken=mapboxAccessToken)


################## Favorite Routes ##################

@app.route("/sites/<int:site_id>/favorite", methods=["POST"])
def create_favorite(site_id):
    """Create a new favorite association between a user and a site."""

    if g.user:
        new_favorite = Favorite(username=g.user.username, site_id=site_id)

        db.session.add(new_favorite)
        db.session.commit()

        return ("success", 200)

    else:
        flash("Please login to access that functionality.", "warning")
        return redirect("/login") 


@app.route("/sites/<int:site_id>/favorite/delete", methods=["POST"])
def delete_favorite(site_id):
    """Delete a favorite association between a user and a site."""

    if g.user:

        Favorite.query.filter(Favorite.site_id==site_id, Favorite.username==g.user.username).delete()

        db.session.commit()

        return ("success", 200)

    else:
        flash("Please login to access that functionality.", "warning")
        return redirect("/login")


################## Comment Routes ##################

@app.route("/sites/<int:site_id>/comments", methods=["GET", "POST"])
def create_comment(site_id):
    """On GET -> Display new comment form.
    On POST -> Save new comment to database."""

    if g.user:

        form = CommentForm()
        site = Site.query.get_or_404(site_id)

        if form.validate_on_submit():
            content = form.content.data
            private = form.private.data

            new_comment = Comment(username=g.user.username, site_id=site_id, content=content, private=private)

            db.session.add(new_comment)
            db.session.commit()

            return redirect(f"/sites/{site_id}")
        
        else:
            return render_template("comment-form.html", form=form, site=site)

    else:
        flash("Please login to view that page.", "warning")
        return redirect("/login")


@app.route("/comments/<int:comment_id>/update", methods=["GET", "POST"])
def update_comment(comment_id):
    """On GET -> Display comment update form.
    On POST -> Save updates to comment.
    """

    if g.user:

        comment = Comment.query.get_or_404(comment_id)
        site = Site.query.get_or_404(comment.site_id)
        form = CommentForm(obj=comment)

        if comment.username == g.user.username:

            if form.validate_on_submit():

                content = form.content.data
                private = form.private.data

                comment.content = content
                comment.private = private

                db.session.commit()

                flash("Your comment has been updated successfully.", "success")
                return redirect(f"/sites/{comment.site_id}")

            else:
                return render_template("comment-update.html", form=form, site=site)

        else:
            flash("You must be the owner of that comment to edit it.", "warning")
            return redirect("/login")
    
    else:
        flash("Please login to view that page.", "warning")
        return redirect("/login")


@app.route("/comments/<int:comment_id>/delete", methods=["POST"])
def delete_comment(comment_id):
    """Delete a comment from the database"""

    if g.user:

        comment = Comment.query.get_or_404(comment_id)

        if comment.username == g.user.username:

            db.session.delete(comment)
            db.session.commit()

            return ("success", 200)

        else:
            flash("You must be the owner of that comment to delete it.", "warning")
            return redirect("/login")
    
    else:
        flash("Please login to view that page.", "warning")
        return redirect("/login")
