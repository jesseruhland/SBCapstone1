"""Models for SaferSexNYC app"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User"""

    __tablename__ = "users"
    
    def __repr__(self):
        """Display user information"""
        u = self
        return f"<User username:{u.username}>"

    username = db.Column(db.String(30), primary_key=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    zip_code = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String, nullable=False)

    comments = db.relationship("Comment", backref="user")
    fav_sites = db.relationship("Site", secondary="favorites", backref="fav_users")

    @classmethod
    def register(cls, username, first_name, last_name, email, zip_code, password):
        """Register a new User with a hashed password"""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, first_name=first_name, last_name=last_name, email=email, zip_code=zip_code, password=hashed_utf8)

    @classmethod
    def authenticate(cls, username, password):
        """Verify a user's credentials, return User if valid, return False if not valid"""

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        
        else:
            return False



class Comment(db.Model):
    """Comment"""

    __tablename__ = "comments"

    def __repr__(self):
        """Display comment information"""
        c = self
        return f"<Comment id:{c.id}, username:{c.username}, private?:{c.private}>"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), db.ForeignKey("users.username", ondelete="CASCADE"), nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    private = db.Column(db.Boolean, nullable=False)

class Favorite(db.Model):
    """Favorite Location relationships"""

    __tablename__ = "favorites"

    def __repr__(self):
        """Display favorite relationship information"""
        f = self
        return f"<Favorite Relationship username:{f.username}, facility:{f.facility_pk}>"

    username = db.Column(db.String(30), db.ForeignKey("users.username", ondelete="CASCADE"), primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey("sites.id", ondelete="CASCADE"), primary_key=True)

class Site(db.Model):
    """Site"""

    __tablename__ = "sites"

    def __repr__(self):
        """Display site information"""
        s = self
        return f"<Site id:{s.id}, name:{s.name}>"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    service_category = db.Column(db.String)
    service_type = db.Column(db.String)
    building_number = db.Column(db.String)
    partner_type = db.Column(db.String)
    partner_type_detailed = db.Column(db.String)
    address = db.Column(db.String)
    address_2 = db.Column(db.String)
    borough = db.Column(db.String)
    zip_code = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    phone = db.Column(db.String)
    additional_info = db.Column(db.String)
    start_date = db.Column(db.String)
    end_date = db.Column(db.String)
    monday = db.Column(db.String)
    tuesday = db.Column(db.String)
    wednesday = db.Column(db.String)
    thursday = db.Column(db.String)
    friday = db.Column(db.String)
    saturday = db.Column(db.String)
    sunday = db.Column(db.String)
    condoms_male = db.Column(db.Boolean)
    fc2_female_insertive_condoms = db.Column(db.Boolean)
    lubricant = db.Column(db.Boolean)
    facility_type = db.Column(db.String)
    website = db.Column(db.String)

    comments = db.relationship("Comment", backref="site")