from ..db import db

GRADES_PATTERN = {
    # """
    # Grade: [low_grade_score, high_grade_score, GPA]
    # """
    'A+': [90, 100, 4.00],
    'A': [80, 89, 3.75],
    'B+': [75, 79, 3.50],
    'B': [70, 74, 3.00],
    'C+': [65, 69, 2.50],
    'C': [60, 64, 2.00],
    'D+': [55, 59, 2.50],
    'D': [50, 54, 1.00],
    'F': [0, 49, 0.00] 
}

class Enrollement(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer(), primary_key=True)
    student_id = db.Column(db.String(), db.ForeignKey('students.student_id'), nullable=False)
    course_code = db.Column(db.String(10), db.ForeignKey('courses.course_code'), nullable=False)
    score = db.Column(db.Integer(), default=0, nullable=False)
    grade = db.Column(db.String(2), default='F')
    grade_point = db.Column(db.Float(2), default=0)
    course = db.relationship('Course', backref='enrollment') 
    student = db.relationship('Student', backref='enrollment')

    def __repr__(self):
        return f'<Score: {self.score}>'
    

    def gradeStudent(self, score):
        self.score = score

        for grade, score_range in GRADES_PATTERN.items():
            if score_range[0] <= score <= score_range[1]:

                self.grade = grade
                self.grade_point = score_range[2]

        db.session.commit()

    
    @classmethod
    def calculateGpa(cls, student_id):
        student_courses = cls.query.filter_by(student_id=student_id).all()
        # total_score = 0
        total_grade_point = 0
        gpa = 0

        if student_courses:
            total_enrollment = len(student_courses)
                
            for course in student_courses:
                # score = course.score
                total_grade_point += course.grade_point


            gpa = total_grade_point/total_enrollment

            return gpa
        else:
            return 0
        
