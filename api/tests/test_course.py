import unittest
from .. import create_app
from ..main.db import db
from ..main.models.user import User
from ..main.models.course import Course
from ..main.config.config import config_dict
from flask_jwt_extended import create_refresh_token, create_access_token



class courseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config=config_dict['test'])
        self.appctx = self.app.app_context()
        self.appctx.push()
        self.client = self.app.test_client()
        
        db.create_all()

    
    def tearDown(self):
        db.drop_all()

        self.appctx.pop()
        self.app = None
        self.client = None

    
    def test_add_new_course(self):
        #Add an admin before adding a new course 
       data = {
           'fullname': 'administrator',
           'username': 'admin',
           'email': 'admin@gmail.com',
           'password': 'password',
           'is_admin': True,
       }

       admin = User(**data)
       db.session.add(admin)
       db.session.commit()

       course = {
           'course_code': 'TS001',
           'teacher': 'Test Teacher',
           'name': 'Test Course'
       }
       
       #Create access token using admin
       token = create_access_token(identity=admin.id)

       headers = {
           'Authorization': f'Bearer {token}'
       }
       
       response = self.client.post('/course', json=course, headers=headers)

       assert response.status_code == 201
       assert response.json['name'] == 'Test Course'

    
    def test_get_all_courses(self):

        response = self.client.get('/course')

        assert response.status_code == 200
        assert response.json == []

    def test_get_single_course(self):

        #Add a new course using test_add_new_course before retrieving course by code
        self.test_add_new_course()

        #Create access token using admin
        token = create_access_token(identity=1)

        headers = {
           'Authorization': f'Bearer {token}'
        }

        response = self.client.get('/course/TS001', headers=headers)

        assert response.status_code == 200
        assert response.json['teacher'] == 'Test Teacher'


    def test_update_course(self):

        #Add a new course using test_add_new_course before updating course by code
        self.test_add_new_course()

        #Create access token using admin
        token = create_access_token(identity=1)

        headers = {
           'Authorization': f'Bearer {token}'
        }

        data = {
            'name': 'New Course',
            'teacher': 'New Teache',
            'course_code': 'N001'
        }

        response = self.client.put('/course/TS001', json=data, headers=headers)

        assert response.status_code == 200
        assert response.json['name'] == 'New Course'


    def test_delete_course(self):

        #Add a new course using test_add_new_course before deleting course by code
        self.test_add_new_course()

        #Create access token using admin
        token = create_access_token(identity=1)

        headers = {
           'Authorization': f'Bearer {token}'
        }

        response = self.client.delete('/course/TS001', headers=headers)

        assert response.status_code == 200
        assert response.json['message'] == 'Course successfully deleted'

    
    def test_get_all_students_in_particular_course(self):
        
        self.test_add_new_course()

        #Create access token using admin
        token = create_access_token(identity=1)

        headers = {
           'Authorization': f'Bearer {token}'
        }

        response = self.client.get('/course/enrollment/TS001', headers=headers)

        assert response.status_code == 200
        assert response.json == []

    
    def test_get_students_grades_in_particular_course(self):
        
        self.test_add_new_course()

        #Create access token using admin
        token = create_access_token(identity=1)

        headers = {
           'Authorization': f'Bearer {token}'
        }

        response = self.client.get('/course/enrollment/grade/TS001', headers=headers)

        assert response.status_code == 200
        assert response.json == []