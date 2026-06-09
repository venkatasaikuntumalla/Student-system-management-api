import os
from decouple import config
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

uri = config('DATABASE_URL') #or other relevant config var
if uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)

authorization = {
        'security':[{"bearerAuth": []}],
        'components':{
            "securitySchemes":
                {
                    "bearerAuth": {
                        "type":"http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "Add a JWT Token to the header ** &lt; JWT &gt; ** to get authorized"
                    }

                    # USE THE CONFIGURATION BELOW FOR apiKey 
                    # "bearerAuth": {
                    #     "type":"apiKey",
                    #     "in": "header",
                    #     "name": "Authorization",
                    #     "description": "Add a JWT Token to the header with ** Bearer &lt; JWT &gt; ** to get authorized"
                    # }
                }
        }
    }


class Config:
    SECRET_KEY = config('SECRET_KEY', 'secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_SECRET_KEY = config('JWT_SECRET_KEY', 'jwt_secret')
    
    PROPAGATE_EXCEPTIONS = True
    API_TITLE = "Student Management API"
    API_VERSION = "v1"
    OPENAPI_DESCRIPTION = "A student Management system for registering students and courses"
    API_SPEC_OPTIONS = authorization
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = ""
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATION = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(BASE_DIR, 'db.sqlite3')
   

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATION = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://' #THIS USES SQL MEMORY DATABASE INSTEAD OF CREATING A NEW ONE
    
class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = config('DEBUG', False, cast=bool)
    # pass


config_dict = {
    'dev': DevConfig,
    'prod': ProdConfig,
    'test': TestConfig
}