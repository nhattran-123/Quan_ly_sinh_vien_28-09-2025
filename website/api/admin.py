from flask import Blueprint, jsonify, request,send_file
from flask_login import fresh_login_required,current_user
from .. import db
from io import BytesIO
from ..models import User,Department,Lecturer
from collections import Counter
from .. import login_manager
import pandas as pd
admin_bp=Blueprint('admin',__name__)
"""
  1.THÔNG TIN CHUNG
-Lấy thông tin admin :http://127.0.0.1:5000/api/admin/userinfor (GET)
  2.THÔNG TIN KHOA
-Lấy ra danh sách khoa:http://127.0.0.1:5000/api/admin/list_department (GET)
-Thêm một khoa bằng thủ công:http://127.0.0.1:5000/api/admin/add_department (POST)
-Thêm khoa bằng file excel:http://127.0.0.1:5000/api/admin/upload-excel-department (POST)
-Sửa thông tin một khoa:http://127.0.0.1:5000/api/admin/update-department/<department_id>(PUT)
-Xóa một khoa:http://127.0.0.1:5000/api/admin/delete-department/<department_id>(DELETE)
  3.GIẢNG VIÊN TỪNG KHOA
-lấy ra danh sách giáo viên một khoa:http://127.0.0.1:5000/api/admin/lecturers/<department_id> (GET)
-Thêm giáo viên bằng nhập thủ công:http://127.0.0.1:5000/api/admin/add_lecturer (POST)

"""
#1
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
@admin_bp.route('/userinfor',methods=["GET"])
@fresh_login_required
def userinfor():
    if current_user.role!='admin':
        return jsonify({
            "error":"Không thành công",
            "mesgage":"Bạn không phải là admin"

        }), 403
    user_data={
        "id":current_user.id,
        "email":current_user.email,
        "role":current_user.role,
        "full name":current_user.full_name,
    }
    return jsonify(user_data), 200
#2
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
@admin_bp.route('/add_department',methods=["POST"])
@fresh_login_required
def add_department():
    if current_user.role!='admin':
        return jsonify({"error":"Không thành công","message":"Bạn không có quyền truy cập"}), 403
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error":"Lỗi","message":"Chưa có dữ liệu được gửi"}), 404
    id=data.get("id")
    name=data.get("name")
    if not id or not name:
        return jsonify({"error":"Lỗi","message":"Gửi thiếu dữ liệu"}), 400
    department=Department.query.filter_by(id=id).first()
    if not department:
        department=Department(id=id,name=name)
        db.session.add(department)
        db.session.commit()
        return jsonify({"Thêm một khoa mới thành công"}), 200
    else :
        return jsonify({"error":"Lỗi","message":"Khoa đã tồn tại"}), 403

@admin_bp.route('upload-excel-department',methods=["POST"])
@fresh_login_required
def upload_excel_department():
    if current_user.role!='admin':
        return jsonify({"error":"Không thành công","message":"Bạn không có quyền truy cập"}), 403
    if 'file' not in request.files:
        return jsonify({"error":"Lỗi","message":"Chưa có file nào được tải lên."}), 400
    file=request.files['file']
    if file.filename == '':
        return jsonify({"error": "Lỗi", "message": "Chưa có file nào được chọn."}), 400
    if not file.filename.endswith(('.xlsx','.xls')):
        return jsonify({"error":"Lỗi định dạng","message":"Chỉ chấp nhận file Excel (.xlsx, .xls)"}), 400
    try:
        df=pd.read_excel(file)
        department_list= df.to_dict('records')
    except Exception as e:
        return jsonify({"error": "Lỗi đọc file", "message": f"Không thể đọc file Excel. Lỗi: {str(e)}"}), 400
    added_count = 0
    for department in department_list:
        id=department.get("id")
        name=department.get('name')
        if not id or not name:
            continue
        if not Department.query.filter_by(id=id).first():
            new_department=Department(id=id,name=name)
            db.session.add(new_department)
            added_count+=1
    db.session.commit()
    return jsonify({"message": f"Thêm thành công {added_count} khoa mới!"}), 200
@admin_bp.route('/update-department/<department_id>',methods=["PUT"])
@fresh_login_required
def update_department(department_id):
    if current_user.role!='admin':
        return jsonify({"error":"Không thành công","message":"Bạn không có quyền truy cập"}), 403
    department=Department.query.filter_by(id=department_id).first()
    if not department:
        return jsonify({"error":"Lỗi"},"message":"Khoa này chưa tồn tại"), 404
    data=request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error":"Lỗi","message":"Dữ liệu chưa được gửi lên"}), 400
    department.name=data.get("name")
    db.session.commit()
    return jsonify({"message":"Sửa Khoa thành công"}),200
@admin_bp.route('/delete-department/<department_id>',methods=["DELETE"])
@fresh_login_required
def delete_department(department_id):
    if current_user.role!='admin':
        return jsonify({"error":"Không thành công","message":"Bạn không có quyền truy cập"}), 403
    department=Department.query.filter_by(id=department_id).first()
    if not department:
        return jsonify({"error":"Lỗi","message":"Khoa này chưa tồn tại"}), 404
    db.session.delete(department)
    db.session.commit()
    return jsonify({"message":"Xóa khoa thành công"}), 200 

#3
@admin_bp.route('/lecturers/<department_id>',methods=["GET"])
@fresh_login_required
def lecturers(department_id):
    if current_user.role!='admin':
        return jsonify({"error":"Không thành công","message":"Bạn không có quyền truy cập"}), 403
    lecturers_id=Lecturer.query.filter(Lecturer.department_id==department_id).all()
    user_data=[]
    for id in lecturers_id:
        user=User.query.filter(User.id==id.user_id).first()
        user_data.append({
            "id":id.user_id,
            "email":user.email,
            "full_name":user.full_name,
            "birthday":user.date_of_birth.strftime("%d-%m-%Y") if user.date_of_birth else None
        })
    return jsonify(user_data),200# Sửa hàm lecturers
@admin_bp.route('/lecturers/<department_id>',methods=["GET"])
@fresh_login_required
def lecturers(department_id):
    if current_user.role!='admin':
        return jsonify({"error":"Không thành công","message":"Bạn không có quyền truy cập"}), 403

    # Dùng JOIN để lấy cả Lecturer và User info trong 1 query
    results = db.session.query(
        User.id,
        User.email,
        User.full_name,
        User.date_of_birth,
        Lecturer.position # Thêm bất cứ trường nào bạn cần từ bảng Lecturer
    ).join(
        Lecturer, User.id == Lecturer.user_id
    ).filter(
        Lecturer.department_id == department_id
    ).all()

    user_data = []
    for id, email, full_name, date_of_birth, position in results:
        user_data.append({
            "id": id,
            "email": email,
            "full_name": full_name,
            "birthday": date_of_birth.strftime("%d-%m-%Y") if date_of_birth else None,
            "position": position # Thêm trường ví dụ
        })

    return jsonify(user_data), 200
@admin_bp.route('/add_lecturer',methods=["POST"])
@fresh_login_required
def add_lecturer():
    if current_user.role!='admin':
        return jsonify({"error":"Không thành công","message":"Bạn không có quyền truy cập"}), 403
    