import unittest
from .. import create_app
from ..main.db import db
from ..main.models.user import User
from ..main.config.config import config_dict
from flask_jwt_extended import create_access_token




class authTestCase(unittest.TestCase):
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

    def test_create_user(self):
       #Add an admin before creating new user  
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

       new_data = {
           'fullname': 'testUser',
           'username': 'user',
           'email': 'user@gmail.com',
           'password': 'password',
           'is_admin': False
       }
       
       #Create access token using admin
       token = create_access_token(identity=admin.id)

       headers = {
           'Authorization': f'Bearer {token}'
       }
 
       response = self.client.post('/auth/user/signup', json=new_data, headers=headers)

       assert response.status_code == 201
       assert response.json['id'] == 2     

    
    def test_user_login_success(self):
       #create new user using the "test_create_user function before login"
       self.test_create_user()

       loginDetails = {
           'username': 'user',
           'password': 'password'
       }

       response = self.client.post('/auth/user/login', json=loginDetails)

       assert response.status_code == 200

    
    def test_create_student(self):
       
       #Add an admin using test_create_user function before creating new student  
       self.test_create_user()
       
       token = create_access_token(identity=1)

       headers = {
           'Authorization': f'Bearer {token}'
       }

       student_data = {
           'firstname': 'testFirstName',
           'lastname': 'testLastName',
           'email': 'teststudentmail@gmail.com'
       }

       response = self.client.post('/auth/student/register', json=student_data, headers=headers)

       assert response.status_code == 201
       assert response.json['student_id'] == 'ATS00001'
    

    def test_student_login_fail(self):
        
        #Testing login failure because the student password is generated randomly when user is created
        #Add a student using test_create_student function before logging in student  
        self.test_create_student()

        loginDetails = {
           'student_id': 'ATS00001',
           'password': 'U0uJJMjB'
       }

        response = self.client.post('/auth/student/login', json=loginDetails)

        assert response.status_code == 401
        assert response.json['message'] == 'Your credentials do not match'

    def test_reset_password(self):

        #Add a user using test_create_user function before resetting user password  
       self.test_create_user()

       response = self.client.post('/auth/resetpassword/user@gmail.com')

       assert response.status_code == 200
       assert response.json['message'] == 'New password successfully generated'

    
    def test_change_password(self):

        #Add an user using test_create_user function before resetting user password  
       self.test_create_user()

       data = {
          'old_password': 'password',
          'new_password': 'newpassword'
       }

       token = create_access_token(identity=2)

       headers = {
           'Authorization': f'Bearer {token}'
       }
       
       response = self.client.put('/auth/changepassword', json=data, headers=headers)

       assert response.status_code == 200
       assert response.json['message'] == 'Password successfuly changed'

