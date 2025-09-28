from sqlalchemy import ForeignKey
from __init__ import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.String(15), primary_key=True, nullable=False)
    email = db.Column(db.String(300), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='', nullable=False)
    full_name = db.Column(db.String(300), default='', nullable=False)
    date_of_birth = db.Column(db.DateTime(timezone=True), nullable=True)

    lecturer = db.relationship('Lecturer', uselist=False, back_populates='user')
    student = db.relationship('Student', uselist=False, back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Admin(db.Model):
    __tablename__ = 'admin'
    user_id = db.Column(db.String(15), db.ForeignKey('user.id'), primary_key=True, nullable=False)

class Lecturer(db.Model):
    __tablename__ = 'lecturer'
    user_id = db.Column(db.String(15), db.ForeignKey('user.id'), primary_key=True, nullable=False)
    department_id = db.Column(db.String(15), db.ForeignKey('department.id'), nullable=True)
    position_id = db.Column(db.String(100), nullable=False)

    user = db.relationship('User', back_populates='lecturer')
    department = db.relationship('Department', back_populates='lecturers')

class Student(db.Model):
    __tablename__ = 'student'
    user_id = db.Column(db.String(15), db.ForeignKey('user.id'), primary_key=True, nullable=False)
    department_id = db.Column(db.String(15), db.ForeignKey('department.id'), nullable=False)
    entry_year = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, nullable=False)

    user = db.relationship('User', back_populates='student')

class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.String(15), primary_key=True, nullable=False)
    name = db.Column(db.String(300), nullable=False)

    lecturers = db.relationship('Lecturer', back_populates='department', lazy=True)
    courses = db.relationship('Course', backref='department', lazy=True)

class ClassSection(db.Model):
    __tablename__ = "class_sections"
    id = db.Column(db.String(15), primary_key=True)
    course_id = db.Column(db.String(15), ForeignKey('course.id'), nullable=False)
    lecturer_id = db.Column(db.String(15), ForeignKey('lecturer.user_id'), nullable=False)
    term_id = db.Column(db.String(15), ForeignKey('terms.id'), nullable=False)
    room_id = db.Column(db.String(15), ForeignKey('room.id'), nullable=False)
    max_students = db.Column(db.Integer, nullable=False)
    schedule = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    id = db.Column(db.String(15), primary_key=True)
    student_id = db.Column(db.String(15), db.ForeignKey('student.user_id'), nullable=False)
    class_id = db.Column(db.String(15), db.ForeignKey('class_sections.id'), nullable=False)
    status = db.Column(db.Boolean, nullable=False)

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.String(15), primary_key=True)
    enrollment_id = db.Column(db.String(15), db.ForeignKey('enrollment.id'), nullable=False)
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    status = db.Column(db.Boolean, nullable=False)

class Grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.String(15), primary_key=True)
    enrollment_id = db.Column(db.String(15), db.ForeignKey('enrollment.id'), nullable=False)
    exam_id = db.Column(db.String(15), db.ForeignKey('exam.id'), nullable=False)
    final_score = db.Column(db.Float, nullable=False)
    letter_score = db.Column(db.String(2), nullable=False)
    notes = db.Column(db.Text, nullable=True)

class Exam(db.Model):
    __tablename__ = 'exam'
    id = db.Column(db.String(15), primary_key=True)
    class_id = db.Column(db.String(15), db.ForeignKey('class_sections.id'), nullable=False)
    name = db.Column(db.String(300), nullable=False)
    max_score = db.Column(db.Numeric(8, 2))
    weight = db.Column(db.Numeric(5, 2))
    grade = db.relationship('Grade', backref='exam', lazy=True)

class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.String(15), primary_key=True)
    department_id = db.Column(db.String(15), db.ForeignKey('department.id'), nullable=False)
    name = db.Column(db.String(300), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    theory_hours = db.Column(db.Integer, nullable=False)
    practice_hours = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)

class Terms(db.Model):
    __tablename__ = 'term'
    id = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    start_date = db.Column(db.DateTime(timezone=True), nullable=False)
    end_date = db.Column(db.DateTime(timezone=True), nullable=False)

class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)