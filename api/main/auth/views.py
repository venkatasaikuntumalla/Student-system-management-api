from flask_smorest import Blueprint, abort
from ..db import db
from flask.views import MethodView
from ..schemas import adminLoginSchema, studentLoginSchema, basicStudentSchema, userSchema, userSignupSchema, changePasswordSchema
from ..models.student import Student
from ..models.user import User
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import random, string


blp = Blueprint('auth', __name__, description='Enpoints for authentication')


@blp.route('/auth/user/signup')
class createUser(MethodView):

    @jwt_required()
    @blp.doc(description='To add a new user, Login as an admin. Only admins can add a new user')
    @blp.arguments(userSignupSchema)
    @blp.response(201, userSchema)
    def post(self, user_data):
        """
        Create or add a new user
        """
        user_id = get_jwt_identity()
        
        if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()

            if user and user.is_admin == True:
                email = user_data['email']
                username = user_data['username']

                email_exit = User.query.filter_by(email=email).first()
                username_exit = User.query.filter_by(username=username).first()

                if email_exit or username_exit:
                    abort(400, message= f'A user with the email {email} or username {username} already exit')
                
                else:
                    new_user = User(
                        fullname = user_data['fullname'],
                        username = username,
                        email = email,
                        password = generate_password_hash(user_data['password']),
                        is_admin = user_data['is_admin']
                    )

                    try:
                        db.session.add(new_user)
                        db.session.commit()
                    
                    except IntegrityError:
                        abort(400, message= f'A user with the email {email} or username {username} already exit')
                    
                    except SQLAlchemyError:
                        abort(500, message = 'An error occured whiles adding user')

                    return new_user, 201
            else:
                abort(401, message='Only administrators can add a user. Login as admin to add user')
        else:
            abort(401, message='Only administrators can add a user. Login as admin to add user')


@blp.route('/auth/user/login')
class loginUser(MethodView):

    @blp.arguments(adminLoginSchema)
    @blp.doc(description='Use this route to login as admin or user. This will generate Access Token for Admin or user')
    def post(self, user_data):
        """
        Generate Access Token for Admininistrator or user
        """

        user = User.query.filter_by(username=user_data['username']).first()

        if user and check_password_hash(user.password, user_data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)

            response = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }

            return response, 200
        
        else:

            abort(401, message='Your credentials do not match')


@blp.route('/auth/student/register')
class createStudent(MethodView):

    @jwt_required()
    @blp.doc(description='Use this route to create or Register a new student. Login as admin or normal user to perform this action. Students cannot add other students')
    @blp.arguments(basicStudentSchema)
    def post(self, student_data):
        """
        Register a new student
        """
        user_id = get_jwt_identity()

        if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()

            if user:
                email = student_data['email']

                email_exit = Student.query.filter_by(email=email).first()

                if email_exit:
                    abort(400, message= f'A student with the email {email} already exit')

                else:
                    #Generate a random password for student
                    characters = string.ascii_letters + string.digits
                    password = ''.join((random.choice(characters) for i in range(8)))

                    new_student = Student(
                        firstname = student_data['firstname'],
                        lastname = student_data['lastname'],
                        email = email,
                        password = generate_password_hash(password)
                    )

                    try:
                        db.session.add(new_student)
                        db.session.commit()

                        #Generate a student ID for student
                        student_id = 'ATS'+ str(0)*(5-(len(str(new_student.id)))) + str(new_student.id)
                        new_student.student_id = student_id
                        
                        db.session.commit()
                    
                    except IntegrityError:
                        abort(400, message= f'A student with the email {email} already exit')
                    
                    except SQLAlchemyError:
                        abort(500, message = 'An error occured whiles adding student')

                    return {
                        'message': 'New student successfully created. Use the credentials below to login as a student',
                        'student_id': student_id,
                        'password': password
                    }, 201
            else:
                abort(401, message='Only administrators and users can add a student. Login as admin or user to add student')
        else:
            abort(401, message='Only administrators and users can add a student. Login as admin or user to add student')


@blp.route('/auth/student/login')
class loginStudent(MethodView):

    @blp.arguments(studentLoginSchema)
    @blp.doc(description='Generate Access Token for student. This route is used to login students')
    def post(self, student_data):
        """
        Generate Access Token for student
        """
        student_id = student_data['student_id'].upper()
        student = Student.query.filter_by(student_id=student_id).first()

        if student and check_password_hash(student.password, student_data['password']):
            access_token = create_access_token(identity=student.student_id, fresh=True)
            refresh_token = create_refresh_token(identity=student.student_id)

            response = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }

            return response, 200
        
        else:

            abort(401, message='Your credentials do not match')


@blp.route('/auth/resetpassword/<string:email>')
class resetPassword(MethodView):

    @blp.doc(
            description='Use this route to reset a forgotten password. This can be performed by both students and users. However you cannot reset the password of the Super admin',
            parameters=[
            {
                'name': 'email', 
                'in': 'path', 
                'description': 'Email of the student or user whose password needs to be reset', 
                'required': 'true'
                }
            ]
        )
    def post(self, email):
        """
        Reset password
        """
        student = Student.query.filter_by(email=email).first()
        user = User.query.filter_by(email=email).first()

        if user and user.username == 'superadmin':
            return {
                'message': 'For testing purposes, you are not allowed to reset the super admin password'
            }
            
        elif student:

            #Generate a random password for student
            characters = string.ascii_letters + string.digits
            new_password = ''.join((random.choice(characters) for i in range(8)))        
                
            student.password = generate_password_hash(new_password)

            db.session.commit()

            return {
                'message': 'New password successfully generated',
                'student_id': student.student_id,
                'new_password': new_password
            }, 200
            
        elif user and user.username != 'superadmin':
            #Generate a random password for user
            characters = string.ascii_letters + string.digits
            new_password = ''.join((random.choice(characters) for i in range(8)))        
                
            user.password = generate_password_hash(new_password)

            db.session.commit()

            return {
                'message': 'New password successfully generated',
                'username': user.username,
                'new_password': new_password
            }, 200
        
        else:
            return {
                'message': 'Email not found'
            }, 404
        

@blp.route('/auth/changepassword')
class changePassword(MethodView):

    @jwt_required()
    @blp.doc(description='Use this route to change a password. This can be performed by both students and users. However you cannot change the password of the Super admin')
    @blp.arguments(changePasswordSchema)
    def put(self, data):
        """
        Change password
        """
        user_id = get_jwt_identity()
        response = {'message': 'Password successfuly changed'}

        if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()

            if user and user.username == 'superadmin':
                return {
                    'message': 'For testing purposes, you are not allowed to change the super admin password'
                }
            
            elif user and check_password_hash(user.password, data['old_password']):
                user.password = generate_password_hash(data['new_password'])
                db.session.commit()

                return response, 200
            
            else:
                return {
                    'message': 'Your old password is incorrect'
                } 
            

        if isinstance(user_id, str):
            student = Student.query.filter_by(student_id=user_id).first()

            if student and check_password_hash(student.password, data['old_password']):
                student.password = generate_password_hash(data['new_password'])    
                db.session.commit()

                return response, 200
            else:
                return {
                    'message': 'Your old password is incorrect'
                }
            
            
        


        
            
             
            
        
         
        

 

# @blp.route('/auth/resetpass/<string:student_id>')
# class resertStudentPassword(MethodView):

#     @jwt_required()
#     def post(self, student_id):
#         """
#         Reset password for students
#         """
#         student = Student.query.filter_by(student_id=student_id.upper()).first()

#         user_id = get_jwt_identity()
#         user = User.query.filter_by(id=user_id).first()

#         if user and user.is_admin == True:
            
#             if student:

#                 #Generate a random password for student
#                 characters = string.ascii_letters + string.digits
#                 new_password = ''.join((random.choice(characters) for i in range(8)))        
                
#                 student.password = generate_password_hash(new_password)

#                 db.session.commit()

#                 return {
#                     'message': 'New password successfully generated',
#                     'student_id': student.student_id,
#                     'new_password': new_password
#                 }, 201
            
#             else:
#                 return {
#                 'message': 'Student not found'
#             }, 404
                
#         else:
#             abort(401, message='Only administrators can regenerate a password. Login as admin to perform this action')
            

# @blp.route('/refresh')
# class refreshToken(MethodView):
     
#     @jwt_required(refresh=True)
#     @blp.doc(description='Refresh Access Token')
#     def get(self):
#         """
#         Generate Refresh Access Token
#         """
#         user = get_jwt_identity()

#         access_token = create_refresh_token(identity=user)

#         return {
#             'access_token': access_token
#         }, 201
