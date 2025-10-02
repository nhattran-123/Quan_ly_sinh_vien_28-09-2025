from flask import Blueprint, jsonify
from flask_login import login_required, current_user
# from .. import db
from ..models import Lecturer,User,ClassSection 
#,Department,Student,Exam,Enrollment,Grade,Course,Terms,Room
# from datetime import date
from .. import login_manager
lecturer_bp=Blueprint('lecturer',__name__)
"""
    Lấy thông tin giảng viên :http://127.0.0.1:5000/api/lecturer/userinfor
    Danh sách các lớp mà giảng viên giảng dạy:http://127.0.0.1:5000/api/lecturer/classSections
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
        "birthday": current_user.date_of_birth.strftime("%Y-%m-%d") if current_user.date_of_birth else None,
        "email":current_user.email,
        "role": current_user.role,   
    }
    Lecturer_infor=Lecturer.query.filter_by(user_id=current_user.id).first()

    if Lecturer_infor:
        user_data["details"]={
            "department_id":Lecturer_infor.department_id,
            "department_name":Lecturer_infor.department.name,
            "position":Lecturer_infor.position_id
        }
    else:
        user_data["details"]={"error":"Lecturer details record missing"}
    return jsonify(user_data),200
@lecturer_bp.route("/classSections",methods=["GET"])
@login_required
def classSections():
    lecturer_classs=ClassSection.query.filter(ClassSection.lecturer_id==current_user.id).all()
    list_class={}
    for i in lecturer_classs:
        list_class[i.id]={
            "coure": i.course_id,
            "term": i.term_id,
            "room":i.room_id,
            "max_students":i.max_students,
            "schedule":i.schedule,
            "start_date":i.start_date.strftime("%Y-%m-%d"),
            "end_date":i.end_date.strftime("%Y-%m-%d")
        }
    if not list_class:
        return jsonify("Không có phụ trách lớp nào"), 200
    else:
        return jsonify(list_class), 200
