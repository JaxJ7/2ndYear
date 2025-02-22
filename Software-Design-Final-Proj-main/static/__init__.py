from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__, template_folder='../static/templates', static_folder='../static')
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SECRET_KEY'] = '54d4ba538a7892d0e826d4ac'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from static import routes, entities

@login_manager.user_loader
def load_user(user_id):
    return entities.User.query.get(user_id)