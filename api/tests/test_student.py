import unittest
from .. import create_app
from ..main.db import db
from ..main.models.user import User
from flask_jwt_extended import create_access_token
from ..main.config.config import config_dict




class studentTestCase(unittest.TestCase):
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

    def test_get_all_students(self):

        #Add an admin
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

        token = create_access_token(identity=admin.id)

        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = self.client.get('/student', headers=headers)

        assert response.status_code == 200
        assert response.json == []

     
    def test_enroll_for_course(self):
        
        #Add an admin
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

        token = create_access_token(identity=admin.id)

        headers = {
            'Authorization': f'Bearer {token}'
        }

        course = {'course_code': 'TS001'}
        
        response = self.client.post("/student/enrollment", json=course, headers=headers)

        assert response.status_code == 401
        assert response.json['message'] == 'Only registered students can enroll for a coure. Login as a student to perform this action'
    
    
    def test_get_courses_of_a_student(self):
        #Add an admin
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

        token = create_access_token(identity=admin.id)

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # Create a new student before getting courses
        student_data = {
           'firstname': 'testFirstName',
           'lastname': 'testLastName',
           'email': 'teststudentmail@gmail.com'
       }
        
        self.client.post('/auth/student/register', json=student_data, headers=headers)
        
        response = self.client.get('/student/enrollment/ATS00001', headers=headers)

        assert response.status_code == 200
        assert response.json == []
    
    def test_update_student_score(self):
        #Add an admin
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

        token = create_access_token(identity=admin.id)

        headers = {
            'Authorization': f'Bearer {token}'
        }

        score = {
            'score': 90
        }

        response = self.client.put('/student/enrollment/ATS00001/CS001', json=score, headers=headers)

        assert response.status_code == 404
        assert response.json['message'] == 'Student is not enrolled for this course'


    def test_unregister_student_from_course(self):
        #Add an admin
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

        token = create_access_token(identity=admin.id)

        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = self.client.delete('/student/enrollment/ATS00001/CS001', headers=headers)

        assert response.status_code == 404
        assert response.json['message'] == 'Student with ID ATS00001 is not enrolled under the course CS001'

    def test_get_grades_of_all_course_for_a_student(self):
        #Add an admin
        data = {
            'fullname': 'administrator',
            'username': 'superadmin',
            'email': 'admin@gmail.com',
            'password': 'password',
            'is_admin': True,
        }

        admin = User(**data)
        db.session.add(admin)
        db.session.commit()

        token = create_access_token(identity=admin.id)

        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = self.client.get('/student/enrollment/grade/ATS00001', headers=headers)

        assert response.status_code == 200
        assert response.json == []


    def test_get_gpa_of_all_students(self):
        #Add an admin
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

        token = create_access_token(identity=admin.id)

        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = self.client.get('/student/enrollment/gpa', headers=headers)

        assert response.status_code == 200
        assert response.json == []


    def test_get_gpa_of_a_student(self):
        #Add an admin
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

        token = create_access_token(identity=admin.id)

        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = self.client.get('/student/enrollment/gpa/ATS00001', headers=headers)

        assert response.status_code == 404
        assert response.json['message'] == 'Student not found'


    def test_get_student_by_id(self):
       
       #Add an admin
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

        token = create_access_token(identity=admin.id)

        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        student_data = {
           'firstname': 'testFirstName',
           'lastname': 'testLastName',
           'email': 'teststudentmail@gmail.com'
       }

        self.client.post('/auth/student/register', json=student_data, headers=headers) #Create a student
 
        response = self.client.get('/student/ATS00001', headers=headers)

        assert response.status_code == 200
        assert response.json['student_id'] == 'ATS00001'


    def test_update_student(self):
       #Add an admin
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

        token = create_access_token(identity=admin.id)

        headers = {
            'Authorization': f'Bearer {token}'
        }

        student_data = {
            'firstname': 'testFirstName',
            'lastname': 'testLastName',
            'email': 'teststudentmail@gmail.com'
        }

        self.client.post('/auth/student/register', json=student_data, headers=headers) #Create a student

        update = {
            'firstname': 'testFirst',
            'lastname': 'testLast',
            'email': 'testmail@gmail.com'
            }
       
        response = self.client.put('/student/ATS00001', json=update, headers=headers)

        assert response.status_code == 201
        assert response.json['email'] == 'testmail@gmail.com'
        assert response.json['lastname'] == 'testLast'


    def test_delete_student(self):
        
        #Add an admin
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

        token = create_access_token(identity=admin.id)

        headers = {
            'Authorization': f'Bearer {token}'
        }

        student_data = {
            'firstname': 'testFirstName',
            'lastname': 'testLastName',
            'email': 'teststudentmail@gmail.com'
        }

        self.client.post('/auth/student/register', json=student_data, headers=headers) #Create a student
       
        response = self.client.delete('/student/ATS00001', headers=headers)

        assert response.status_code == 200
        assert response.json['message'] == 'Student successfully deleted'
 