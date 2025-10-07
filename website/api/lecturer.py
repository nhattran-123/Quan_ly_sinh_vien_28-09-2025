from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import Lecturer,User,ClassSection,Enrollment,Student,Room,Course,Terms
#,Department,Exam,Grade
# from datetime import date
from .. import login_manager
lecturer_bp=Blueprint('lecturer',__name__)
"""
    Lấy thông tin giảng viên :http://127.0.0.1:5000/api/lecturer/userinfor
    Danh sách các lớp mà giảng viên giảng dạy:http://127.0.0.1:5000/api/lecturer/classSections
    Danh sách sinh viên từng lớp:http://127.0.0.1:5000/api/lecturer/list_student/<class_id>
"""

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
@lecturer_bp.route('/userinfor',methods=["GET"])
@login_required
def userinfor():
    if current_user.role!='lecturer':
        return jsonify({
            "error":"Không thành công",
            "messager":"Bạn không phải là giảng viên"
        }), 403
    user_data={
        "id": current_user.id,
        "fullname":current_user.full_name,
        "birthday": current_user.date_of_birth.strftime("%d-%m-%Y") if current_user.date_of_birth else None,
        "email":current_user.email,
        "role": current_user.role,   
    }
    Lecturer_infor=Lecturer.query.filter_by(user_id=current_user.id).first()

    if Lecturer_infor:
        user_data["details"]={
            "department_id":Lecturer_infor.department_id,
            "department_name":Lecturer_infor.department.name,
            "position":Lecturer_infor.position
        }
    else:
        user_data["details"]={"error":"Lecturer details record missing"}
    return jsonify(user_data),200
@lecturer_bp.route("/classSections",methods=["GET"])
@login_required
def classSections():
    dem=1
    lecturer_classs=ClassSection.query.filter(ClassSection.lecturer_id==current_user.id).all()
    list_class=[]
    for i in lecturer_classs:
        room=Room.query.filter(Room.id==i.room_id).first()
        vtri_phong=room.name+" "+ room.location
        course=Course.query.filter(Course.id==i.course_id).first()

        list_class.append({
            "STT":dem,
            "coure": i.course_id,
            "lecturer_name":current_user.full_name,
            "name":course.name,
            "credit":course.credits,
            "theory_hours":course.theory_hours,
            "practice_hours":course.practice_hours,
            "room":vtri_phong,
            "max_students":i.max_students,
            "schedule":i.schedule,
            "start_date":i.start_date.strftime("%d-%m-%Y"),
            "end_date":i.end_date.strftime("%d-%m-%Y")
        })
        dem+=1
    if not list_class:
        return jsonify("Không có phụ trách lớp nào"), 200
    else:
        return jsonify(list_class), 200
@lecturer_bp.route("/list_student/<class_id>", methods=["GET"])
@login_required
def list_student(class_id):
    students_in_class = db.session.query(
        User.id, 
        User.full_name, 
        User.date_of_birth, 
        User.email
    ).join(
        Student, User.id == Student.user_id 
    ).join(
        Enrollment, Student.user_id == Enrollment.student_id 
    ).filter(
        Enrollment.class_id == class_id 
    ).all() # Lấy tất cả kết quả
    danh_sach = []
    dem = 1
    
    for student_id, full_name, date_of_birth, email in students_in_class:
        # Kiểm tra và định dạng ngày sinh
        birth_day_str = date_of_birth.strftime("%d-%m-%Y") if date_of_birth else None

        # Sử dụng 'dem' làm key thay vì luôn là '1'
        danh_sach.append({
            "STT":dem,
            "full_name": full_name,
            "id": student_id,
            "email": email,
            "birth_day": birth_day_str
        })
        dem += 1
    if not danh_sach:
        return jsonify({"message": "Không có sinh viên nào trong lớp này hoặc ID lớp không hợp lệ."}), 404
    else:
        return jsonify(danh_sach)
        

