from flask import Flask, current_app, url_for
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os
from flask_mail import Mail
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database_setup import Base, Pages

# Connect to Database and create database session
engine = create_engine('sqlite:///app/data/pages-collection.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'allo'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/database.db'


app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'lam.ricky98website@gmail.com'
app.config['MAIL_PASSWORD'] = 'WebsitePassword'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
mail = Mail(app)

Bootstrap(app)




from app import routes
