from ..db import db


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    teacher = db.Column(db.String(120), nullable=False)
    course_code = db.Column(db.String(10), nullable=False, unique=True)
    students = db.relationship('Student', secondary='enrollments')


    def __repr__(self):
        return f'<Course_Name: {self.name}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()
