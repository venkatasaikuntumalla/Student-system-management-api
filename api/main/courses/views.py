from flask_smorest import Blueprint, abort
from flask import jsonify
from flask.views import MethodView
from ..schemas import courseSchema, plainCourseSchema, basicStudentSchema, courseGradeSchema
from http import HTTPStatus
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, InternalError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..db import db
from ..models.student import Student
from ..models.course import Course
from ..models.user import User
from ..models.enrollment import Enrollement

blp = Blueprint('course', __name__, description='Endpoints for course')


@blp.route('/course')
class getCreateCourse(MethodView):

    @blp.doc(description = 'Get all courses. Students, users and admins can view all available courses')
    @blp.response(HTTPStatus.OK, plainCourseSchema(many=True))
    def get(self):
        """
        Get all courses
        """
           
        courses = Course.query.all()

        return courses, HTTPStatus.OK

        # return Course.query.all()
        
    
    @jwt_required()
    @blp.doc(description = 'Add a new course. Only admins and users can add a new course')
    @blp.arguments(plainCourseSchema)
    @blp.response(HTTPStatus.CREATED, plainCourseSchema)
    def post(self, course_data):
        """
        Add a new course
        """
        user_id = get_jwt_identity()

        if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()

            course_name = course_data['name']
            course_code = course_data['course_code']

            if len(course_code) > 7:
                abort(500, message='Your course code should not be more than seven (7) characters')

            if user:
                code_exit = Course.query.filter_by(course_code=course_code.upper()).first()
                name_exit = Course.query.filter_by(name=course_name).first()
                
                if code_exit or name_exit:
                    abort(HTTPStatus.BAD_REQUEST, message= f'A course with name {course_name} or code {course_code.upper()} already exit')
                
                else:
                    new_course = Course(
                    course_code = course_data['course_code'].upper(),
                    name = course_data['name'],
                    teacher = course_data['teacher']
                    )
                
                    try:
                        new_course.save()
                    
                    except IntegrityError:
                        abort(HTTPStatus.BAD_REQUEST, message= f'A course with name {course_name} or code {course_code.upper()} already exit')

                    except SQLAlchemyError:
                        abort(HTTPStatus.INTERNAL_SERVER_ERROR, message= 'An error occured whiles adding new course')

                    return new_course, HTTPStatus.CREATED
                
            else:
                abort(401, message='Only administrators can add a course. Login as admin to perform this action')
        else:
            abort(401, message='Only administrators can add a course. Login as admin to perform this action')
        

@blp.route('/course/<string:course_code>')
class getCourseByCode(MethodView):

    @jwt_required()
    @blp.doc(
        description = 'Get a course by its code. Only admins and users can perform this action',
        parameters = [
            {
                'name': 'course_code',
                'in': 'path',
                'description': 'A course code eg. EN001',
                'required': 'true'
            }
        ]
    )
    @blp.response(HTTPStatus.OK, courseSchema)
    def get(self, course_code):
        """
        Get a course by course code
        """
        user_id = get_jwt_identity()

        if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()

            if user:
                course = Course.query.filter_by(course_code=course_code.upper()).first()
                
                if course:
                    return course, HTTPStatus.OK
                else:
                    abort(404, message='Course not found')
            else:
                abort(401, message='only admins and users can perform this function. Login as admin or user')
        else:
            abort(401, message='only admins and users can perform this function. Login as admin or user')

    
    @jwt_required()
    @blp.doc(
        description = 'Update or edit a course by its code. Only admins and users can perform this action',
        parameters = [
            {
                'name': 'course_code',
                'in': 'path',
                'description': 'A course code eg. CS001',
                'required': 'true'
            }
        ]
    )
    @blp.arguments(plainCourseSchema)
    @blp.response(HTTPStatus.OK, plainCourseSchema)
    def put(self, data, course_code):
        """
        Update or Edit a Course
        """
        user_id = get_jwt_identity()

        if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()

            if user and user.is_admin == True:
                course_update = Course.query.filter_by(course_code=course_code.upper()).first()
                if course_update:
                    course_name = data['name']
                    code = data['course_code'].upper()
                    enrollments = Enrollement.query.filter_by(course_code=course_code.upper()).all()
                    try:
                        course_update.name = data['name']
                        course_update.teacher = data['teacher']
                        course_update.course_code = data['course_code'].upper()
                        if enrollments:
                            for enrollment in enrollments:
                                enrollment.course_code = code

                        db.session.commit()
                    except IntegrityError:
                        abort(HTTPStatus.BAD_REQUEST, message= f'A course with name {course_name} or code {code} already exit')

                    except SQLAlchemyError:
                        abort(HTTPStatus.INTERNAL_SERVER_ERROR, message= 'An error occured whiles adding new course')

                    return course_update, HTTPStatus.OK
                else:
                    abort(404, message="Course not found")
            else:
                abort(401, message='Only administrators can update a course. Login as admin to perform this action')
        else:
            abort(401, message='Only administrators can update a course. Login as admin to perform this action')


    @jwt_required()
    @blp.doc(
        description = 'Delete a course from the database using the course code. Only admins can perform this action',
        parameters = [
            {
                'name': 'course_code',
                'in': 'path',
                'description': 'A course code eg. CS001',
                'required': 'true'
            }
        ]
    )
    def delete(self, course_code):
            """
            Delete a course
            """
            user_id = get_jwt_identity()

            if isinstance(user_id, int):
                user = User.query.filter_by(id=user_id).first()

                course = Course.query.filter_by(course_code=course_code.upper()).first()
                
                if user and user.is_admin == True:
                    if course:
                        try:
                            db.session.delete(course)
                            db.session.commit()

                            return {
                                'message': 'Course successfully deleted'
                            }, 200
                            
                        except SQLAlchemyError:
                            abort(500, message='There are students already enrolled to this course')

                    else:
                        abort(404, message='Course not found')
                else:
                    abort(401, message='Only administrators can delete a course. Login as admin to perform this action')
            else:
                abort(401, message='Only administrators can delete a course. Login as admin to perform this action')



@blp.route('/course/enrollment/<string:course_code>')
class enrolledStudents(MethodView):

    @jwt_required()
    @blp.doc(
        description = 'Get all students registered or enrolled for a particular course by its code. Only admins and users can perform this action',
        parameters = [
            {
                'name': 'course_code',
                'in': 'path',
                'description': 'A course code eg. MA001',
                'required': 'true'
            }
        ]
    )
    @blp.response(HTTPStatus.OK, basicStudentSchema(many=True))
    def get(self, course_code):
       """
       Get all Students Registered in a particular course
       """
       user_id = get_jwt_identity()

       if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()
            
            course = Course.query.filter_by(course_code=course_code.upper()).first()           
            
            if user:
                if course:
                        students = course.students
                        
                        return students, HTTPStatus.OK
                else:
                    abort(404, message='Course not found')
            else:
               abort(401, message='Only administrators and users can perform this action. Login as admin or user to have access')
       else:
           abort(401, message='Only administrators and users can perform this action. Login as admin or user to have access')
             

@blp.route('/course/enrollment/grade/<string:course_code>')
class getStudentCourseGrades(MethodView):

    @jwt_required()
    @blp.doc(
        description = 'Get the grades of all students in a particular course by its code. Only admins and users can perform this action',
        parameters = [
            {
                'name': 'course_code',
                'in': 'path',
                'description': 'A course code eg. CS001',
                'required': 'true'
            }
        ]
    )
    @blp.response(200, courseGradeSchema(many=True))
    def get(self, course_code):
        """
        Get grades of all students for a particular course
        """
        user_id = get_jwt_identity()

        if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id)

            if user:
                enrollment = Enrollement.query.filter_by(course_code=course_code.upper()).all()

                return enrollment, 200
            else:
                abort(401, message='Only administrators and users can perform this action. Login as admin or user to have access')
        else:
            abort(401, message='Only administrators and users can perform this action. Login as admin or user to have access')
        