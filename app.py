"""SaferSexNYC application."""

from flask import Flask, request, redirect, render_template, flash, session
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Comment, Favorite
from forms import RegisterForm, LoginForm, UpdateUserForm, CommentForm
from secret import api_app_token
from sqlalchemy.exc import IntegrityError

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
    """Display the homepage of the application"""

    if check_login():
        return redirect("/facilities")
    return render_template("homepage.html")


@app.route("/register")
def display_user_form():
    """Display form for new user registration"""

    form = RegisterForm()
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def log_in_user():
    """On GET -> Display login form
    On POST -> Validate user login credentials, if valid save user to session"""

    if check_login():
        return redirect("/facilities")
    
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
    """Logout current user"""

    session.pop("username")
    return redirect("/")


################## User Routes ##################


@app.route("/users", methods=["POST"])
def create_user():
    """Create a new user from entered form data"""

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
            return redirect("/register")
        
        session["username"] = new_user.username

        return redirect(f"/users/{new_user.username}")


@app.route("/users/<username>", methods=["GET", "PATCH", "DELETE"])
def display_user_detail(username):
    """On GET -> display user profile page
    on PATCH -> update user details
    on DELETE -> delete user"""

    if check_login():
        user = User.query.get_or_404(username)

        method = request.method

        if method == "GET":
            return render_template("user-detail.html", user=user)
        
        if method == "PATCH":
            if username == session.get("username"):
                password = form.password.data
                username = session.get("username")

                this_user = User.authenticate(username=username, password=password)

                if this_user:
                    this_user.username = form.username.data
                    this_user.first_name = form.first_name.data
                    this_user.last_name = form.last_name.data
                    this_user.email = form.email.data
                    this_user.zip_code = form.zip_code.data

                    db.session.commit()

                    session["username"] = this_user.username

                    flash("Your profile has been successfully updated!", "success")
                    return redirect(f"/users/{this_user.username}")
                
                else:
                    flash(f"Incorrect password entered for {username}, please try again.", "warning")
                    return redirect(f"users/{username}/update")


        # if method == "DELETE":
    
    else:
        flash("You must login to view that page.", "warning")
        return redirect("/login")


@app.route("/users/<username>/update", methods=["GET"])
def display_user_edit_form(username):
    """Display the user edit form for the specified user if that user is logged in."""

    if username == session.get("username"):
        user = User.query.get_or_404(username)
        form = UpdateUserForm(obj=user)
        return render_template("user-update.html", form=form, user=user)
    else:
        flash("You are not authorized to access that page.", "danger")
        return redirect(f"/users/{session.get('username')}")


