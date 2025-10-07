from sqlalchemy import ForeignKey, DateTime
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import Numeric

# --- LỚP NGƯỜI DÙNG (CƠ SỞ) ---

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.String(15), primary_key=True, nullable=False)
    email = db.Column(db.String(300), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='', nullable=False)
    full_name = db.Column(db.String(300), default='', nullable=False)
    date_of_birth = db.Column(DateTime(timezone=True), nullable=True)

    admin = db.relationship('Admin', uselist=False, back_populates='user')
    lecturer = db.relationship('Lecturer', uselist=False, back_populates='user')
    student = db.relationship('Student', uselist=False, back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- LỚP PHÂN QUYỀN (QUẢN TRỊ, GIẢNG VIÊN, SINH VIÊN) ---

class Admin(db.Model):
    __tablename__ = 'admins'
    user_id = db.Column(db.String(15), db.ForeignKey('users.id'), primary_key=True, nullable=False)

    user = db.relationship('User', back_populates='admin')

class Lecturer(db.Model):
    __tablename__ = 'lecturers'
    user_id = db.Column(db.String(15), db.ForeignKey('users.id'), primary_key=True, nullable=False)
    department_id = db.Column(db.String(15), db.ForeignKey('departments.id'), nullable=True)
    position = db.Column(db.String(100), nullable=False)

    user = db.relationship('User', back_populates='lecturer')
    department = db.relationship('Department', back_populates='lecturers')
    
    # Đã thêm: Lấy các lớp học mà giáo viên này chịu trách nhiệm
    classes = db.relationship('ClassSection', backref='lecturer_ref', lazy=True, primaryjoin="Lecturer.user_id == ClassSection.lecturer_id") 

class Student(db.Model):
    __tablename__ = 'students'
    user_id = db.Column(db.String(15), db.ForeignKey('users.id'), primary_key=True, nullable=False)
    department_id = db.Column(db.String(15), db.ForeignKey('departments.id'), nullable=False)
    entry_year = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, nullable=False)

    user = db.relationship('User', back_populates='student')
    # Đã sửa: Thêm backref cho Department
    department = db.relationship('Department', backref='students', lazy=True)
    # Đã thêm: Lấy tất cả các lần đăng ký lớp học của sinh viên này
    enrollments = db.relationship('Enrollment', backref='student_ref', lazy=True, primaryjoin="Student.user_id == Enrollment.student_id") 

# --- LỚP QUẢN LÝ TỔ CHỨC ---

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.String(15), primary_key=True, nullable=False)
    name = db.Column(db.String(300), nullable=False)

    lecturers = db.relationship('Lecturer', back_populates='department', lazy=True)
    courses = db.relationship('Course', backref='department', lazy=True)

class Terms(db.Model):
    __tablename__ = 'terms'
    id = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    start_date = db.Column(DateTime(timezone=True), nullable=False)
    end_date = db.Column(DateTime(timezone=True), nullable=False)

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.String(15), primary_key=True)
    department_id = db.Column(db.String(15), db.ForeignKey('departments.id'), nullable=False)
    name = db.Column(db.String(300), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    theory_hours = db.Column(db.Integer, nullable=False)
    practice_hours = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)

# --- LỚP QUẢN LÝ LỚP HỌC & ĐIỂM DANH/ĐIỂM SỐ ---

class ClassSection(db.Model):
    __tablename__ = "class_sections"
    id = db.Column(db.String(15), primary_key=True)
    course_id = db.Column(db.String(15), ForeignKey('courses.id'), nullable=False)
    lecturer_id = db.Column(db.String(15), ForeignKey('lecturers.user_id'), nullable=False)
    term_id = db.Column(db.String(15), ForeignKey('terms.id'), nullable=False)
    room_id = db.Column(db.String(15), ForeignKey('rooms.id'), nullable=False)
    max_students = db.Column(db.Integer, nullable=False)
    schedule = db.Column(db.Integer, nullable=False)
    start_date = db.Column(DateTime, nullable=False)
    end_date = db.Column(DateTime, nullable=False)

    # Đã sửa: Bổ sung cho chức năng ĐIỂM DANH TỰ ĐỘNG
    attendance_open = db.Column(db.Boolean, default=False, nullable=False) 
    checkin_start_time = db.Column(DateTime(timezone=True), nullable=True) 
    checkin_duration_minutes = db.Column(db.Integer, default=15, nullable=False) 
    
    # Mối quan hệ đã thêm (để truy vấn dễ hơn)
    assignments = db.relationship('Assignment', back_populates='class_section', lazy=True)
    assignment_weights = db.relationship('AssignmentWeight', back_populates='class_section', lazy=True)
    course = db.relationship('Course', backref='sections') 
    term = db.relationship('Terms', backref='sections')
    room = db.relationship('Room', backref='sections')

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.String(15), primary_key=True)
    student_id = db.Column(db.String(15), db.ForeignKey('students.user_id'), nullable=False)
    class_id = db.Column(db.String(15), db.ForeignKey('class_sections.id'), nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    final_grade = db.Column(db.Float, nullable=True)
    letter_grade = db.Column(db.String(5), nullable=True)

    # Đã thêm: Lấy thông tin ClassSection từ bản ghi Enrollment
    class_section = db.relationship('ClassSection', backref='enrollments')
    grades = db.relationship('Grade', back_populates='enrollment', lazy=True)


class Attendance(db.Model):
    __tablename__ = 'attendances'
    id = db.Column(db.String(15), primary_key=True)
    enrollment_id = db.Column(db.String(15), db.ForeignKey('enrollments.id'), nullable=False)
    date = db.Column(DateTime(timezone=True), nullable=False)
    status = db.Column(db.Boolean, nullable=False)

    # Đã thêm: Lấy thông tin Enrollment từ bản ghi Attendance
    enrollment = db.relationship('Enrollment', backref='attendances')


class AssignmentType(db.Model):
    __tablename__ = 'assignment_types'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    assignments = db.relationship('Assignment', back_populates='assignment_type', lazy=True)
    assignment_weights = db.relationship('AssignmentWeight', back_populates='assignment_type', lazy=True)


class AssignmentWeight(db.Model):
    __tablename__ = 'assignment_weights'
    class_id = db.Column(db.String(15), ForeignKey('class_sections.id'), primary_key=True)
    assignment_type_id = db.Column(db.Integer, ForeignKey('assignment_types.id'), primary_key=True)
    weight = db.Column(db.Float, nullable=False)

    assignment_type = db.relationship('AssignmentType', back_populates='assignment_weights')
    class_section = db.relationship('ClassSection', back_populates='assignment_weights')


class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.String(20), primary_key=True)
    class_id = db.Column(db.String(20), ForeignKey('class_sections.id'), nullable=False)
    assignment_type_id = db.Column(db.Integer, ForeignKey('assignment_types.id'), nullable=False)

    assignment_type = db.relationship('AssignmentType', back_populates='assignments')
    class_section = db.relationship('ClassSection', back_populates='assignments')
    grades = db.relationship('Grade', back_populates='assignment', lazy=True)

class Grade(db.Model):
    __tablename__ = 'grades'
    enrollment_id = db.Column(db.String(15), db.ForeignKey('enrollments.id'), primary_key=True, nullable=False)
    assignment_id = db.Column(db.String(15), db.ForeignKey('assignments.id'), primary_key=True, nullable=False)
    grade = db.Column(db.Float, nullable=True)

    assignment = db.relationship('Assignment', back_populates='grades')
    enrollment = db.relationship('Enrollment', back_populates='grades')