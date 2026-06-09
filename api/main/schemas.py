from marshmallow import Schema, fields

class userSchema(Schema):
    id = fields.Int(dump_only=True)
    fullname = fields.Str(required=True)
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    is_admin = fields.Bool(required=True)

class userSignupSchema(userSchema):
    
    password = fields.Str(required=True)

class plainCourseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    teacher = fields.Str(required=True)
    course_code = fields.Str(required=True)

class basicStudentSchema(Schema):
    id = fields.Int(dump_only=True)
    firstname = fields.Str(required=True)
    lastname = fields.Str(required=True)
    email = fields.Str(required=True)
    student_id = fields.Str(dump_only=True)

class fullStudentSchema(basicStudentSchema):
    courses = fields.List(fields.Nested(plainCourseSchema()), dump_only=True)

class courseSchema(plainCourseSchema):
    students = fields.List(fields.Nested(basicStudentSchema()), dump_only=True)

class enrollmentSchema(Schema):
    
    course_code = fields.Str(required=True, load_only=True)
    courses = fields.Nested(plainCourseSchema(), dump_only=True)

class studentGradeSchema(Schema):
    course = fields.Str(dump_only=True)
    grade = fields.Str(dump_only=True)
     
class scoreSchema(studentGradeSchema):
    score = fields.Int(required=True)
    # student = fields.Nested(basicStudentSchema(), dump_only=True)
    # course = fields.Nested(plainCourseSchema(), dump_only=True)
    student = fields.Str(dump_only=True)
    # course =  fields.Str(dump_only=True)

class courseGradeSchema(Schema):    
    student = fields.Str(dump_only=True)
    grade = fields.Str(dump_only=True)

class adminLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class studentLoginSchema(Schema):
    student_id = fields.Str(required=True)
    password = fields.Str(required=True)

class changePasswordSchema(Schema):
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True)