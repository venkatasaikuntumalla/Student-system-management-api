from flask import Flask
from flask_smorest import Api
from .main.db import db
from werkzeug.security import generate_password_hash
from .main.models.course import Course
from .main.models.student import Student
from .main.models.user import User
from .main.models.enrollment import Enrollement
from .main.config.config import config_dict
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from .main.students.views import blp as studentBlueprint
from .main.auth.views import blp as authBlueprint
from .main.courses.views import blp as courseBlueprint


def create_app(config=config_dict['dev']):
    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)
    migrate = Migrate(app, db)

    api = Api(app)

    jwt = JWTManager(app)

    @app.before_first_request
    def create_admin():
        user = User.query.filter_by(username='superadmin').first()

        if user:
            pass
        else:
            admin = User(
                fullname='Super Administrator', 
                username='superadmin', 
                email='superadmin@gmail.com',
                is_admin= True,
                password=generate_password_hash('password')
            )    

            db.session.add(admin)
            db.session.commit()

    api.register_blueprint(authBlueprint)
    api.register_blueprint(studentBlueprint)
    api.register_blueprint(courseBlueprint)


    @app.shell_context_processor
    def make_shell_context():

        return {
            'db': db,
            'Student': Student,
            'Course': Course,
            'User': User,
            'Enrollment': Enrollement
        }

    return app
