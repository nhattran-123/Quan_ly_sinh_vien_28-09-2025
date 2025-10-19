from flask import Blueprint, jsonify, request
from flask_login import fresh_login_required,current_user
from .. import db
from ..models import User,Department
from collections import Counter
from .. import login_manager

admin_bp=Blueprint('admin',__name__)
"""
Lấy thông tin admin :http://127.0.0.1:5000/api/admin/userinfor
Lấy ra danh sách khoa:http://127.0.0.1:5000/api/admin/list_department

"""
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
@admin_bp.route('/userinfor',methods=["GET"])
@fresh_login_required
def userinfor():
    if current_user.role!='admin':
        return jsonify({
            "error":"Không thành công",
            "mesgager":"Bạn không phải là admin"

        }), 403
    user_data={
        "id":current_user.id,
        "email":current_user.email,
        "role":current_user.role,
        "full name":current_user.full_name,
    }
    return jsonify(user_data), 200
@admin_bp.route('/list_department',methods=["GET"])
@fresh_login_required
def list_department():
    if current_user.role!='admin':
        return jsonify({"error":"Không thành công","message":"Bạn không có quyền truy cập"}), 403
    department=Department.query.all()
    if not department:
        return jsonify({"error":"lỗi","message":"Không tìm thấy khoa"}), 404
    list_departments=[]
    for x in department:
        list_departments.append({"id":x.id,"name":x.name})
    return jsonify(list_departments), 200
@admin_bp.route('/add_department',methods=['GET'])
@fresh_login_required
def add_department():
    if current_user.role!='admin':
        return jsonify({"error":"Không thành công","message":"Bạn không có quyền truy cập"}), 403
    data = request.get_json(silent=True) or request.form
    department_list= data if isinstance(data,list) else data.get("departments",[])
    if not department_list:
        return jsonify({"error":"Lỗi","message":"Không có dữ liệu nào được gửi"}), 400
    
