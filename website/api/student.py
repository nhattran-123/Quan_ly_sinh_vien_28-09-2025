from flask import Blueprint, jsonify, request,send_file
from flask_login import fresh_login_required, current_user
from .. import db
from io import BytesIO
from ..models import Lecturer,User,ClassSection,Enrollment,Student,Room,Course,Terms,Grade,Assignment,AssignmentType,AssignmentWeight
from collections import Counter
#,Department,Exam
from datetime import datetime
from .. import login_manager
import pandas as pd

student_bp=Blueprint('student',__name__)
"""
TỔNG HỢP API CHO SINH VIÊN(STUDENT)

-Lấy thông tin sinh viên (cá nhân): http://127.0.0.1:5000/api/student/profile (GET)
-Sửa thông tin sinh viên (cá nhân): http://127.0.0.1:5000/api/student/profile (PUT)
-Lấy ra các kỳ đã và đang học: http://127.0.0.1:5000/api/student/terms (GET)
-Lấy ra các lớp đã đăng ký (trong kỳ): http://127.0.0.1:5000/api/student/enrollments/<term_id> (GET)
-Lấy ra danh sách sinh viên lớp bạn đã đăng ký (trong kỳ): http://127.0.0.1:5000/api/student/list_student/<class_id>/<term_id>(GET)
-Lấy ra thông tin chi tiết và điểm của bạn đăng ký: http://127.0.0.1:5000/api/student/enrollments/<class_id> (GET)
-lấy ra các môn bạn đã đăng ký (trong kỳ): http://127.0.0.1:5000/api/student/course/<term_id>(GET)
-Lấy ra thông tin chi tiết môn bạn đã đăng ký (trong kỳ): http://127.0.0.1:5000/api/student/<course_id>/<term_id>(GET)

"""
