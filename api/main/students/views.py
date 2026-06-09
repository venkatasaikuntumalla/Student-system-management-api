from flask_smorest import Blueprint, abort
from flask.views import MethodView
from ..schemas import basicStudentSchema, fullStudentSchema, enrollmentSchema, scoreSchema, studentGradeSchema, plainCourseSchema
from http import HTTPStatus
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..db import db
from ..models.student import Student
from ..models.course import Course
from ..models.enrollment import Enrollement
from ..models.user import User

blp = Blueprint('student', __name__, description='Enpoints for student')



@blp.route('/student')
class getStudents(MethodView):

    @jwt_required()
    @blp.doc(description='Get all registered students. Login as an admin or user to use this route. Not available for students')
    @blp.response(HTTPStatus.OK, basicStudentSchema(many=True))
    def get(self):
        """
        Get all students
        """
        user_id = get_jwt_identity()

        if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()

            if user:
                return Student.query.all()
            else:
                abort(HTTPStatus.UNAUTHORIZED, message='Only administrators and users can view all students info. Login as admin or user to have access')
        else:
            abort(HTTPStatus.UNAUTHORIZED, message='Only administrators and users can view all students info. Login as admin or user to have access')
    

@blp.route('/student/enrollment')
class courseEnrollment(MethodView):

    @jwt_required()
    @blp.doc(description='This is a students route for registering course. Only logged in students can register for a course. Login as a student to use this route.')
    @blp.arguments(enrollmentSchema)
    @blp.response(HTTPStatus.CREATED, fullStudentSchema)
    def post(self, data):
        """
        Enroll for a course as a student
        """
        
        student_id = get_jwt_identity()

        if isinstance(student_id, str):
            student = Student.query.filter_by(student_id=student_id).first()
            course_available = Course.query.filter_by(course_code=data['course_code'].upper()).first()
            enrolled = Enrollement.query.filter_by(student_id=student_id, course_code=data['course_code'].upper()).first()

            if enrolled:
                abort(401, message="You have already enrolled for this course")
            if student:
                if course_available:

                    enrollment = Enrollement(course_code=data['course_code'].upper())
                    enrollment.student_id = student_id
                        

                    db.session.add(enrollment)
                    db.session.commit()

                    return student, HTTPStatus.CREATED
                else:
                    abort(HTTPStatus.NOT_FOUND, message='This course is not availabe. Check your course code again to register')
            else:
                abort(HTTPStatus.UNAUTHORIZED, message='Only registered students can enroll for a coure. Login as a student to perform this action')
        else:
            abort(HTTPStatus.UNAUTHORIZED, message='Only registered students can enroll for a coure. Login as a student to perform this action')
    

@blp.route('/student/enrollment/<string:student_id>')
class getAllStudentCourse(MethodView):
    
    @jwt_required()
    @blp.doc(
        description = 'Get all the courses of a particular student. A student can view his/her courses, but cannot view that of others. An admin or user can view the courses of any student',
        parameters=[
            {
                'name': 'student_id', 
                'in': 'path', 
                'description': 'The ID of student Eg. ATS00001', 
                'required': 'true'
                }
            ]
        )
    @blp.response(HTTPStatus.OK, plainCourseSchema(many=True))
    def get(self, student_id):
       """
       Get all courses of a particular student
       """
       user_id = get_jwt_identity()
       user = {}

       if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()
            
       if user or student_id.upper() == user_id:
            student = Student.query.filter_by(student_id=student_id.upper()).first()
            if student:
                course = student.courses
                return course, HTTPStatus.OK
            else:
                abort(404, message="Student not found")
       else:
           abort(401, message='You cannot view course of other students. Login as admin or user to view other student course')
       

@blp.route('/student/enrollment/<string:student_id>/<string:course_code>')
class updateDeleteStudentCourse(MethodView):
    
    @jwt_required()
    @blp.doc(
        description = 'Score a student out of 100 by the course. Only admins or users can enter a students score',
        parameters=[
            {
                'name': 'student_id', 
                'in': 'path', 
                'description': 'The ID of student Eg. ATS00001', 
                'required': 'true'
                },
            {
                'name': 'course_code', 
                'in': 'path', 
                'description': 'The course code to score Eg. CS001', 
                'required': 'true'
                }
            ]
        )
    @blp.arguments(scoreSchema)
    @blp.response(HTTPStatus.OK, scoreSchema)
    def put(self, data, student_id, course_code):
       """
       Enter or update a student's score for a course
       """
       user_id = get_jwt_identity()

       if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()
        
            enrollment = Enrollement.query.filter_by(student_id=student_id.upper(), course_code=course_code.upper()).first()
            
            score = data['score']

            if 0 > score > 100:
                abort(401, message = 'The score can only be from 0 to 100')

            if user:
                    
                    if enrollment:

                        enrollment.gradeStudent(score)
                        # enrollment.score = data['score']
                        # db.session.commit()

                        return enrollment, HTTPStatus.OK
                    else:
                        abort(404, message='Student is not enrolled for this course')
            else:
                abort(401, message='Only admins or users can add scores to student course. Login as admin or user to perform this action')
       else:
           abort(401, message='Only admins or users can add scores to student course. Login as admin or user to perform this action')
             

    # @jwt_required()
    # @blp.arguments(enrollmentSchema)
    # @blp.response(HTTPStatus.OK, plainCourseSchema(many=True))
    # def put(self, data, student_id, course_code):
    #    """
    #    Update or change course enrollment for student
    #    """
    #    user_id = get_jwt_identity()
    #    user = User.query.filter_by(id=user_id).first()
    #    course_available = Course.query.filter_by(course_code=data['course_code'].upper()).first()
       
    #    if user and user.is_admin == True:
    #        if course_available:
    #             student = Student.query.filter_by(student_id=student_id.upper()).first()
    #             course = Grade.query.filter_by(student_id=student_id.upper(), course_code=course_code.upper()).first()

    #             if course:
    #                 course.course_code = data['course_code'].upper()
    #                 db.session.commit()

    #                 courses = student.courses

    #                 return courses, HTTPStatus.OK
    #             else:
    #                 abort(401, message=f'Student with ID {student_id.upper()} is not enrolled under the course {course_code.upper()}')
    #        else:
    #             abort(HTTPStatus.NOT_FOUND, message='This course is not availabe. Check your course code again to register')
    #    else:
    #        abort(404, message='Only admins can change a student course. Login as admin to perform this action') 


    @jwt_required()
    @blp.doc(
        description = 'Delete or remove a student from an enrollment or course. Only admins can perform this task',
        parameters=[
            {
                'name': 'student_id', 
                'in': 'path', 
                'description': 'The ID of student Eg. ATS00001', 
                'required': 'true'
                },
            {
                'name': 'course_code', 
                'in': 'path', 
                'description': 'The course delete or unregister Eg. CS001', 
                'required': 'true'
                }
            ]
        )
    def delete(self, student_id, course_code):
       """
       Delete or unregister course enrollment for student
       """
       user_id = get_jwt_identity()

       if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()
            
            if user and user.is_admin == True:
                
                enrollment = Enrollement.query.filter_by(student_id=student_id.upper(), course_code=course_code.upper()).first()

                if enrollment:
                    student = Student.query.filter_by(student_id=student_id.upper()).first()
                    
                    db.session.delete(enrollment)

                    for course in student.courses:
                        if course.course_code == course_code.upper():
                            student.courses.remove(course)
                            break

                    db.session.commit()

                    return {
                        'message': f'You have successfully unregistered student {student_id.upper()} from the course {course_code.upper()}'
                    }, HTTPStatus.OK
                else:
                    abort(404, message=f'Student with ID {student_id.upper()} is not enrolled under the course {course_code.upper()}')

            else:
                abort(401, message='Only admins can unregister students from a course. Login as admin to perform this action') 
       else:
           abort(401, message='Only admins can unregister students from a course. Login as admin to perform this action') 


@blp.route('/student/enrollment/grade/<string:student_id>')
class getGrades(MethodView):

    @jwt_required()
    @blp.doc(
        description = 'Get all the grades of a particular student for all the courses he/she is enrolled under. Students can view only thier grades. Admins and users can view grades of all students',
        parameters=[
            {
                'name': 'student_id', 
                'in': 'path', 
                'description': 'The ID of student Eg. ATS00001', 
                'required': 'true'
                }
            ]
        )
    @blp.response(200, studentGradeSchema(many=True))
    def get(self, student_id):
        """
        Get grades of all courses for a particular student
        """

        user_id = get_jwt_identity()
        user = {}

        if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()

        if student_id.upper() == user_id or user:

            enrollment = Enrollement.query.filter_by(student_id=student_id.upper()).all()

            return enrollment, 200
        else:
            abort(401, message='You cannot view the grades of other students. Login as admin or user to view other students grade')
        

    
@blp.route('/student/enrollment/gpa')
class getGrades(MethodView):

    @blp.doc(description = 'Get the GPA of all students. only admins and user can view GPA of all students',)
    @jwt_required()
    def get(self):
        """
        Get the Grade Point Average (GPA) of all students
        """
        user_id = get_jwt_identity()
        all_gpa = []

        if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()
            
            if user:
                students = Student.query.all()
                
                for student in students:
                    raw_gpa = Enrollement.calculateGpa(student.student_id)
                    gpa = '%.2f' %raw_gpa   # convert gpa to two decimal places

                    result = {
                    'student_id': student.student_id,
                    'student_name': f'{student.firstname} {student.lastname}',
                    'gpa': gpa
                }

                    all_gpa.append(result)

                return all_gpa, 200
            
            else:
                abort(401, message='Only admins or users can view grades of all student. Login in as admin or user to perform this action')
        else:
            abort(401, message='Only admins or users can view grades of all student. Login in as admin or user to perform this action')


@blp.route('/student/enrollment/gpa/<string:student_id>')
class getGrades(MethodView):

    @jwt_required()
    @blp.doc(
        description = 'Get GPA of a particular student. Students can view only thier GPA. Admins and users can view the GPA of any student',
        parameters=[
            {
                'name': 'student_id', 
                'in': 'path', 
                'description': 'The ID of student Eg. ATS00001', 
                'required': 'true'
                }
            ]
    )
    def get(self, student_id):
        """
        Get the Grade Point Average (GPA) of a particular student
        """
        user_id = get_jwt_identity()
        user = {}

        if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()


        if student_id.upper() == user_id or user:
            student = Student.query.filter_by(student_id=student_id.upper()).first()
                
            if student:
                raw_gpa = Enrollement.calculateGpa(student_id.upper())

                gpa = '%.2f' %raw_gpa   # convert gpa to two decimal places

                return {
                    'student_id': student.student_id,
                    'student_name': f'{student.firstname} {student.lastname}',
                    'gpa': gpa
                }, 200
            else:
                abort(404, message='Student not found')
        else:
            abort(401, message='You cannot view other students info. Login as admin or user to perform this action')
        
            

@blp.route('/student/<string:student_id>')
class GetUpdateDeleteStudent(MethodView):

    @jwt_required()
    @blp.doc(
            description='Get a student by ID. A student can view his/her details but not that of others. Admins and users can view details of any student',
            parameters=[
            {
                'name': 'student_id', 
                'in': 'path', 
                'description': 'ID of student to search for', 
                'required': 'true'
                }
            ]
        )
    @blp.response(HTTPStatus.OK, fullStudentSchema)
    def get(self, student_id):
        """
        Get a student by ID
        """
        user_id = get_jwt_identity()
        user = {}

        if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()

        if student_id.upper() == user_id or user:
            student = Student.query.filter_by(student_id=student_id.upper()).first()

            if student:
                return student, HTTPStatus.OK
            else:
                abort(404, message='Student not found')
        else:
            abort(401, message='You cannot view other students info. Login as admin or user to perform this action')
       

    @jwt_required()
    @blp.doc(
            description="Update a student's information. Only admins and users can update a student's info",
            parameters=[
            {
                'name': 'student_id', 
                'in': 'path', 
                'description': 'ID of student to update', 
                'required': 'true'
                }
            ]
        )
    @blp.arguments(basicStudentSchema)
    @blp.response(HTTPStatus.CREATED, basicStudentSchema)
    def put(self, student_data, student_id):
        """
        Update a student's information
        """
        user_id = get_jwt_identity()

        if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()

            if user:
                student = Student.query.filter_by(student_id=student_id.upper()).first()

                if student:
                    email = student_data['email']
                    
                    try:
                        student.firstname = student_data['firstname']
                        student.lastname = student_data['lastname']
                        student.email = student_data['email']

                        db.session.commit()
                    except IntegrityError:
                        abort(400, message= f'A student with the email {email} already exit')
                
                    except SQLAlchemyError:
                        abort(500, message = 'An error occured whiles updating student')

                    return student, HTTPStatus.CREATED
                else:
                    abort(404, message='Student not found')
            else:
                abort(HTTPStatus.UNAUTHORIZED, message='Only administrators can update students info. Login as admin to perform this action')
        else:
            abort(HTTPStatus.UNAUTHORIZED, message='Only administrators can update students info. Login as admin to perform this action')
    

    @jwt_required()   
    @blp.doc(
            description='Delete a student from database by ID. This can only be done by an admin',
            parameters=[
            {
                'name': 'student_id', 
                'in': 'path', 
                'description': 'ID of student you want to delete', 
                'required': 'true'
                }
            ]
        )
    def delete(self, student_id):
        """
        Delete a student from database by ID
        """
        user_id = get_jwt_identity()

        if isinstance(user_id, int):
            user = User.query.filter_by(id=user_id).first()
            

            if user and user.is_admin == True:
                student = Student.query.filter_by(student_id=student_id.upper()).first()
                if student:
                    try:
                        db.session.delete(student)
                        db.session.commit()

                        return {'message': 'Student successfully deleted'}, HTTPStatus.OK
                    except SQLAlchemyError:
                        abort(HTTPStatus.INTERNAL_SERVER_ERROR, message='Student is already enrolled to a course')
                else:
                    abort(404, message='Student not found')

            else:
                abort(HTTPStatus.UNAUTHORIZED, message='Only administrators can delete students. Login as admin to perform this action')
        else:
            abort(HTTPStatus.UNAUTHORIZED, message='Only administrators can delete students. Login as admin to perform this action')



        


