from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView



db = SQLAlchemy()
DB_NAME = "database.db"




def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "helloworld"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    admin = Admin(app)

    from .views import views
    from .auth import auth
    from .models import User, Post, Comment, Like

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    

    create_database(app)
    admin.add_view(ModelView(User,db.session))
    admin.add_view(ModelView(Post,db.session))
    admin.add_view(ModelView(Comment,db.session))
    

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists("website/" + DB_NAME):
        db.create_all(app=app)
        print("Created database!")




