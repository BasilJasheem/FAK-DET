from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy



@login_manager.user_loader 
def load_user(user_id):
    return User.query.get(int(user_id))
    


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    reviews = db.relationship('Review', backref='reviewer', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

#post is for trial
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Product(db.Model):
    __searchable__ = ['item_name']
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(30), nullable=False)
    details = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
    platform = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=True)
    rate = db.Column(db.Float, nullable=True)
    

    def __repr__(self):
        return f"Product('{self.item_name}', '{self.details}', '{self.image}', '{self.platform}', '{self.category}', '{self.rate}')"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rev_name = db.Column(db.String(30), db.ForeignKey('user.username'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    item_id = db.Column(db.Integer, nullable=False)
    rev_text = db.Column(db.Text, nullable=False)
    staus = db.Column(db.Integer, nullable=False)
    lr = db.Column(db.Integer, nullable=False)
    dt = db.Column(db.Integer, nullable=False)
    gbc = db.Column(db.Integer, nullable=False)
    rfc = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    mark = db.Column(db.Integer, nullable=False)
    contra = db.Column(db.Integer, nullable=False)
    c_ignore = db.Column(db.Integer, nullable=False)
    ip = db.Column(db.String(300), nullable=False)
    i_mark = db.Column(db.Integer, nullable=False)
    i_ignore = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Review('{self.rev_name}','{self.date}','{self.item_id}','{self.rev_text}','{self.lr}','{self.dt}','{self.gbc}','{self.rfc}','{self.contra}','{self.rate}')"


class Admin(db.Model):
    username = db.Column(db.String(30), primary_key=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Admin('{self.username}','{self.password}')"