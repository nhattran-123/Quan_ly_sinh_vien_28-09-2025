from flask import Blueprint, jsonify, request, send_file
from flask_login import fresh_login_required, current_user
from .. import db
from io import BytesIO
# Giả sử bạn đã import các model này ở đâu đó, ví dụ: from ..models import User, Department, Lecturer
from ..models import User, Department, Lecturer 
from collections import Counter
from .. import login_manager
import pandas as pd
from sqlalchemy.exc import IntegrityError # Cần import để bắt lỗi CSDL

admin_bp = Blueprint('admin', __name__)
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

# 1. THÔNG TIN CHUNG
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@admin_bp.route('/userinfor', methods=["GET"])
@fresh_login_required
def userinfor():
    if current_user.role != 'admin':
        return jsonify({
            "error": "Không thành công",
            "message": "Bạn không phải là admin" 
        }), 403
    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "full name": current_user.full_name,
    }
    return jsonify(user_data), 200

# 2. QUẢN LÝ KHOA
@admin_bp.route('/list_department', methods=["GET"])
@fresh_login_required
def list_department():
    if current_user.role != 'admin':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403
    
    try:
        departments = Department.query.all()
        # Chuyển sang kiểm tra ở đây
        if not departments: 
            return jsonify({"message": "Không tìm thấy khoa nào."}), 404
        
        list_departments = [{"id": x.id, "name": x.name} for x in departments]
        return jsonify(list_departments), 200
    except Exception as e:
        return jsonify({"error": "Lỗi máy chủ", "message": str(e)}), 500

@admin_bp.route('/add_department', methods=["POST"])
@fresh_login_required
def add_department():
    if current_user.role != 'admin':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403
    
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error": "Lỗi", "message": "Chưa có dữ liệu được gửi"}), 400
    
    id = data.get("id")
    name = data.get("name")
    
    if not id or not name:
        return jsonify({"error": "Lỗi", "message": "Thiếu ID hoặc Name"}), 400
    
    # Kiểm tra tồn tại
    if Department.query.filter_by(id=id).first():
        # SỬA MÃ LỖI: 403 -> 409 (Conflict)
        return jsonify({"error": "Xung đột", "message": f"ID Khoa '{id}' đã tồn tại"}), 409

    try:
        new_department = Department(id=id, name=name)
        db.session.add(new_department)
        db.session.commit()
        # SỬA MÃ THÀNH CÔNG: 200 -> 201 (Created)
        return jsonify({"message": f"Thêm khoa '{name}' thành công"}), 201
    except Exception as e:
        db.session.rollback() # Rất quan trọng
        return jsonify({"error": "Lỗi CSDL", "message": str(e)}), 500

@admin_bp.route('/upload-excel-department', methods=["POST"]) # Sửa: Thêm / ở đầu
@fresh_login_required
def upload_excel_department():
    if current_user.role != 'admin':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403
    
    if 'file' not in request.files:
        return jsonify({"error": "Lỗi", "message": "Chưa có file nào được tải lên."}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Lỗi", "message": "Chưa có file nào được chọn."}), 400
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({"error": "Lỗi định dạng", "message": "Chỉ chấp nhận file Excel (.xlsx, .xls)"}), 400
    
    try:
        df = pd.read_excel(file)
        department_list = df.to_dict('records')
    except Exception as e:
        return jsonify({"error": "Lỗi đọc file", "message": f"Không thể đọc file Excel. Lỗi: {str(e)}"}), 400

    # --- SỬA LỖI HIỆU NĂNG N+1 ---
    try:
        # 1. Lấy tất cả ID khoa hiện có vào một Set (để tra cứu nhanh)
        existing_ids = {d.id for d in Department.query.with_entities(Department.id).all()}
    except Exception as e:
         return jsonify({"error": "Lỗi CSDL", "message": str(e)}), 500
         
    new_departments_to_add = []
    skipped_count = 0
    
    for department in department_list:
        id = department.get("id")
        name = department.get('name')
        
        if not id or not name:
            skipped_count += 1
            continue
            
        # 2. Kiểm tra ID trong Set (nhanh) thay vì query CSDL (chậm)
        if id not in existing_ids:
            new_department = Department(id=id, name=name)
            new_departments_to_add.append(new_department)
            existing_ids.add(id) # Thêm vào set để tránh trùng lặp từ chính file Excel
        else:
            skipped_count += 1
    # --- HẾT SỬA LỖI HIỆU NĂNG ---

    if not new_departments_to_add:
         return jsonify({"message": f"Không có khoa nào mới để thêm. Bỏ qua {skipped_count} bản ghi."}), 200

    # 3. Thêm tất cả vào CSDL 1 lần
    try:
        db.session.add_all(new_departments_to_add)
        db.session.commit()
        added_count = len(new_departments_to_add)
        return jsonify({
            "message": f"Thêm thành công {added_count} khoa mới!",
            "skipped": skipped_count
        }), 201 # SỬA MÃ THÀNH CÔNG: 200 -> 201
    except Exception as e:
        db.session.rollback() # Rất quan trọng
        return jsonify({"error": "Lỗi khi ghi CSDL", "message": str(e)}), 500

@admin_bp.route('/update-department/<department_id>', methods=["PUT"])
@fresh_login_required
def update_department(department_id):
    if current_user.role != 'admin':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403
    
    data = request.get_json(silent=True) or request.form
    if not data or 'name' not in data:
        return jsonify({"error": "Lỗi", "message": "Dữ liệu 'name' chưa được gửi lên"}), 400

    new_name = data.get("name")
    if not new_name:
         return jsonify({"error": "Lỗi", "message": "Tên (name) không được để trống"}), 400

    try:
        department = Department.query.filter_by(id=department_id).first()
        if not department:
            return jsonify({"error": "Lỗi", "message": "Khoa này không tồn tại"}), 404
        
        department.name = new_name
        db.session.commit()
        return jsonify({"message": "Sửa tên khoa thành công"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Lỗi CSDL", "message": str(e)}), 500

@admin_bp.route('/delete-department/<department_id>', methods=["DELETE"])
@fresh_login_required
def delete_department(department_id):
    if current_user.role != 'admin':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403
    
    try:
        department = Department.query.filter_by(id=department_id).first()
        if not department:
            return jsonify({"error": "Lỗi", "message": "Khoa này không tồn tại"}), 404
        
        db.session.delete(department)
        db.session.commit()
        # SỬA MÃ THÀNH CÔNG: 200 -> 204 (No Content)
        return '', 204
    except IntegrityError: # Bắt lỗi khóa ngoại cụ thể
        db.session.rollback()
        return jsonify({"error": "Xung đột", "message": "Không thể xóa khoa này vì vẫn còn giảng viên/lớp học liên kết."}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Lỗi CSDL", "message": str(e)}), 500

# 3. QUẢN LÝ GIẢNG VIÊN
@admin_bp.route('/lecturers/<department_id>', methods=["GET"])
@fresh_login_required
def lecturers(department_id):
    if current_user.role != 'admin':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403

    # Kiểm tra xem khoa có tồn tại không
    if not Department.query.get(department_id):
        return jsonify({"error": "Lỗi", "message": "Khoa này không tồn tại"}), 404

    # Dùng JOIN để lấy cả Lecturer và User info trong 1 query (Code của bạn đã sửa đúng)
    try:
        results = db.session.query(
            User.id,
            User.email,
            User.full_name,
            User.date_of_birth,
            Lecturer.position
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
                "position": position
            })
        
        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({"error": "Lỗi máy chủ", "message": str(e)}), 500

@admin_bp.route('/add_lecturer', methods=["POST"])
@fresh_login_required
def add_lecturer():
    if current_user.role != 'admin':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403
    
    