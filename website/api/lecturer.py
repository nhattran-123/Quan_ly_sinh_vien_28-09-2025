# from flask import Blueprint, jsonify
# from flask_login import login_required, current_user
# from .. import db
# from ..models import User,Lecturer,Department,Student,Exam,Enrollment,ClassSection,Grade,Course,Terms,Room
# from datetime import date
# app=Blueprint('app',__name__)

# @app.route('/userinfor',methods=["GET"])
# @login_required
# def userinfor():
#     if current_user.role!='lecturer':
#         return jsonify({
#             "error":"Không thành công",
#             "messager":"Bạn không phải là giảng viên"
#         }), 403
#     user_data={
#         "id": current_user.id,
#         "fullname":current_user.full_name,
#         "birthday": current_user.date_of_birth.strftime("%Y-%m-%d") if current_user.date_of_birth else None,
#         "email":current_user.email,
#         "role": current_user.role,
#         "address":current_user.address,
#         "numberphone":current_user.phone,
#         "gender":current_user.gender     
#     }
#     Lecturer_infor=Lecturer.query.filter_by(user_id=current_user.id).first()

#     if Lecturer_infor:
#         user_data["details"]={
#             "department_id":Lecturer_infor.department_id,
#             "department_name":Lecturer_infor.department.name,
#             "position":Lecturer_infor.position
#         }
#     else:
#         user_data["details"]={"error":"Lecturer details record missing"}
#     return jsonify(user_data),200
