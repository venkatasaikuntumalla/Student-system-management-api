from ..db import db


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    student_id = db.Column(db.String(), unique=True)
    password = db.Column(db.String(), nullable=False)
    courses = db.relationship('Course', secondary='enrollments')

    def __repr__(self):
        return f'<Student_Name: {self.firstname} {self.lastname}>'
    