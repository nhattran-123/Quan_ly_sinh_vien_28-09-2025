from flask import Blueprint, jsonify, request, send_file
from flask_login import fresh_login_required, current_user
from .. import db
from io import BytesIO
from werkzeug.security import generate_password_hash
from datetime import datetime
from ..models import User, Department, Lecturer, Student
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
-Lấy ra danh sách giảng viên 1 khoa(file):http://127.0.0.1:5000/api/admin/lecturers-excel/<department_id> (GET)
-Thêm giáo viên bằng nhập thủ công:http://127.0.0.1:5000/api/admin/add_lecturer/<department_id> (POST)
-Thêm giáo viên bằng file excel:http://127.0.0.1:5000/api/admin/upload_excel_lecturer/<department_id> (POST)
-Sửa thông tin của một giảng viên:http://127.0.0.1:5000/api/admin/update_lecturer/<lecturer_id> (PUT)
  4.SINH VIÊN THEO TỪNG KHOA
-Lấy ra danh sách sinh viên theo khoa:http://127.0.0.1:5000/api/admin/students/<department_id>(GET)
-Lấy ra danh sách sinh viên 1 khoa(file):http://127.0.0.1:5000/api/admin/students-excel/<department_id> (GET)
-Thêm sinh viên bằng nhập thủ công:http://127.0.0.1:5000/api/admin/add_student/<department_id> (POST)
-Thêm sinh viên bằng file excel:http://127.0.0.1:5000/api/admin/upload_excel_student/<department_id> (POST)
-Sửa thông tin của một sinh viên:http://127.0.0.1:5000/api/admin/update_student/<student_id> (PUT)
"""

# 1. THÔNG TIN CHUNG
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@admin_bp.route('/userinfo', methods=["GET"])
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
        "Chức danh": current_user.role,
        "Họ và Tên": current_user.full_name,
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
        if not departments: 
            return jsonify({"message": "Không tìm thấy khoa nào."}), 404
        
        list_departments = [{"id": x.id, "Tên Khoa": x.name} for x in departments]
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
    
    if Department.query.filter_by(id=id).first():
        return jsonify({"error": "Xung đột", "message": f"ID Khoa '{id}' đã tồn tại"}), 409

    try:
        new_department = Department(id=id, name=name)
        db.session.add(new_department)
        db.session.commit()
        return jsonify({"message": f"Thêm khoa '{name}' thành công"}), 201
    except Exception as e:
        db.session.rollback() # Rất quan trọng
        return jsonify({"error": "Lỗi CSDL", "message": str(e)}), 500

@admin_bp.route('/upload-excel-department', methods=["POST"])
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
        # === SỬA LỖI BUG: Thêm dtype=str để giữ ID (ví dụ: "001") ===
        df = pd.read_excel(file, dtype=str) 
        department_list = df.to_dict('records')
    except Exception as e:
        return jsonify({"error": "Lỗi đọc file", "message": f"Không thể đọc file Excel. Lỗi: {str(e)}"}), 400

    try:
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
            
        if id not in existing_ids:
            new_department = Department(id=id, name=name)
            new_departments_to_add.append(new_department)
            existing_ids.add(id)
        else:
            skipped_count += 1

    if not new_departments_to_add:
        return jsonify({"message": f"Không có khoa nào mới để thêm. Bỏ qua {skipped_count} bản ghi."}), 200

    try:
        db.session.add_all(new_departments_to_add)
        db.session.commit()
        added_count = len(new_departments_to_add)
        return jsonify({
            "message": f"Thêm thành công {added_count} khoa mới!",
            "skipped": skipped_count
        }), 201
    except Exception as e:
        db.session.rollback()
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
        return '', 204
    except IntegrityError: 
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

    if not Department.query.get(department_id):
        return jsonify({"error": "Lỗi", "message": "Khoa này không tồn tại"}), 404

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
                "Họ và Tên": full_name,
                "Ngày Sinh": date_of_birth.strftime("%d-%m-%Y") if date_of_birth else None,
                "Chức vụ": position
            })
        
        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({"error": "Lỗi máy chủ", "message": str(e)}), 500

@admin_bp.route('/lecturers-excel/<department_id>', methods=["GET"])
@fresh_login_required
def lecturer_excel(department_id):
    if current_user.role != 'admin':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403

    if not Department.query.get(department_id):
        return jsonify({"error": "Lỗi", "message": "Khoa này không tồn tại"}), 404
    
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
        
    if not results:
        return jsonify({"message": "Không tìm thấy giảng viên nào trong khoa này."}), 404
        
    user_data = []
    for id, email, full_name, date_of_birth, position in results:
        user_data.append({
            "id": id,
            "email": email,
            "Họ và Tên": full_name,
            "Ngày sinh": date_of_birth.strftime("%d-%m-%Y") if date_of_birth else None,
            "Chức vụ": position
        })
        
    try: 
        df = pd.DataFrame(user_data)
        output_buffer = BytesIO()
        df.to_excel(output_buffer, index=False)
        output_buffer.seek(0)
        filename = f"Danh_sach_giang_vien_{department_id}.xlsx"
        
        return send_file(
            output_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        return jsonify({"error": "Lỗi máy chủ", "message": str(e)}), 500

@admin_bp.route('/add_lecturer/<department_id>', methods=["POST"])
@fresh_login_required
def add_lecturer(department_id): 
    if current_user.role != 'admin':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403
    
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error": "Lỗi", "message": "Chưa có dữ liệu được gửi"}), 400

    id = data.get("id")
    password = data.get("password")
    full_name = data.get("fullname")
    birthday_str = data.get("date_of_birth")
    email = data.get("email")
    role = 'lecturer'
    position = data.get("position")
    
    if not all([id, birthday_str, full_name, email, position, password]):
        return jsonify({
            "error": "Thiếu thông tin",
            "message": "Vui lòng nhập đủ thông tin (id, password, fullname, date_of_birth, email, position)"
        }), 400
        
    if not Department.query.get(department_id):
        return jsonify({"error": "Không tìm thấy", "message": f"Khoa với ID '{department_id}' không tồn tại"}), 404
    if User.query.get(id):
        return jsonify({"error": "Xung đột", "message": f"ID '{id}' đã tồn tại"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Xung đột", "message": f"Email '{email}' đã tồn tại"}), 409

    try:
        hashed_password = generate_password_hash(password)
        
        birthday_obj = None
 #       try:
 #           birthday_obj = datetime.strptime(birthday_str, "%d-%m-%Y").date()
 #       except ValueError:
 #           return jsonify({"error": "Lỗi định dạng", "message": "Ngày sinh phải theo định dạng dd-mm-YYYY"}), 400
        try:
            birthday_obj = datetime.strptime(birthday_str, "%d-%m-%Y")  #không dùng .date() — giữ nguyên kiểu datetime.datetime như trong User ở models.py
        except ValueError:
            return jsonify({"error": "Lỗi định dạng", "message": "Ngày sinh phải theo định dạng dd-mm-YYYY"}), 400

        new_user = User(
            id=id,
            email=email,
            full_name=full_name,
 #           password=hashed_password, # thuộc tính password không tồn tại trong class User của models.py, chỉ có password_hash
            role=role,
            date_of_birth=birthday_obj
        )
        new_user.set_password(password)  # ← dùng setter có sẵn
        db.session.add(new_user)

        new_lecturer = Lecturer(
            user_id=id, 
            department_id=department_id,
            position=position
        )
        db.session.add(new_lecturer)
        
        db.session.commit()
        
        return jsonify({
            "message": f"Tạo giảng viên thành công cho khoa {department_id}",
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Lỗi CSDL", "message": str(e)}), 500

@admin_bp.route('/upload_excel_lecturer/<department_id>', methods=["POST"])
@fresh_login_required
def upload_excel_lecturer(department_id):
    if current_user.role != 'admin':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403
    
    department = Department.query.get(department_id)
    if not department:
        return jsonify({"error": "Lỗi", "message": "Không tìm thấy khoa này"}), 404

    if 'file' not in request.files:
        return jsonify({"error": "Lỗi", "message": "Không có file nào được tải lên"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Lỗi", "message": "Chưa chọn file để tải lên."}), 400
    if not file.filename.endswith(('.xlsx', 'xls')):
        return jsonify({"error": "Lỗi định dạng", "message": "Chỉ chấp nhận file Excel (.xlsx, .xls)."}), 400

    try:
        df = pd.read_excel(file, dtype=str) 
        lecturer_list = df.to_dict('records')
    except Exception as e:
        return jsonify({"error": "Lỗi đọc file", "message": f"Không thể đọc file Excel. Lỗi: {str(e)}"}), 400

    try:
        set_id = {u.id for u in User.query.with_entities(User.id).all()}
        set_email = {u.email for u in User.query.with_entities(User.email).all()}
    except Exception as e:
        return jsonify({"error": "Lỗi CSDL", "message": str(e)}), 500

    users_to_add = []
    lecturers_to_add = []
    errors = []
    skipped_count = 0

    for idx, row in enumerate(lecturer_list, start=2):
        id = row.get("id")
        email = row.get('email')
        password = row.get('password')
        full_name = row.get('full_name')
        dob_str = row.get('date_of_birth')
        position = row.get('position')

        if not all([id, email, password, full_name, dob_str, position]):
            errors.append(f"Hàng {idx}: Thiếu thông tin.")
            continue 
        
        if id in set_id:
            errors.append(f"Hàng {idx}: id '{id}' đã tồn tại.")
        if email in set_email:
            errors.append(f"Hàng {idx}: Email '{email}' đã tồn tại.")
        if id in set_id or email in set_email:
            skipped_count+=1
            continue

        try:
            date_of_birth_obj = pd.to_datetime(dob_str, format="%d-%m-%Y").date()
        except (ValueError, TypeError):
            errors.append(f"Hàng {idx}: Ngày sinh '{dob_str}' sai định dạng (phải là dd-mm-YYYY).")
            continue
            
        hashed_password = generate_password_hash(password)
        
        new_user = User(
            id=id,
            email=email,
            password=hashed_password,
            role='lecturer',
            full_name=full_name,
            date_of_birth=date_of_birth_obj
        )
        
        new_lecturer = Lecturer(
            user_id=id,
            department_id=department_id,
            position=position
        )
        
        users_to_add.append(new_user)
        lecturers_to_add.append(new_lecturer)
        
        set_id.add(id)
        set_email.add(email)

    if errors:
        return jsonify({
            "error": "Dữ liệu file không hợp lệ",
            "messages": errors,
            "added_count": 0,
            "skipped_count": skipped_count
        }), 400
        
    if not users_to_add:
        return jsonify({
            "message": "Không có giảng viên nào mới để thêm.",
            "skipped_count": skipped_count
        }), 200

    try:
        db.session.add_all(users_to_add)
        db.session.add_all(lecturers_to_add)
        db.session.commit()
        
        added_count = len(users_to_add)
        return jsonify({
            "message": f"Thêm thành công {added_count} giảng viên.",
            "added_count": added_count,
            "skipped_count": skipped_count
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Lỗi khi ghi CSDL", "message": str(e)}), 500

@admin_bp.route('/update_lecturer/<lecturer_id>', methods=["PUT"])
@fresh_login_required
def update_lecturer(lecturer_id):
    if current_user.role != 'admin':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403
    
    user = User.query.get(lecturer_id)
    if not user:
        return jsonify({
            "error": "Lỗi",
            "message": "Không tìm thấy người dùng (giảng viên)"
        }), 404
        
    if user.role != 'lecturer':
        return jsonify({"error": "Lỗi", "message": "ID này không phải của giảng viên"}), 400
        
    lecturer = Lecturer.query.filter_by(user_id=lecturer_id).first()
    if not lecturer:
        return jsonify({"error": "Lỗi CSDL", "message": "Dữ liệu giảng viên không đồng nhất"}), 500
        
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error": "Lỗi", "message": "Không có dữ liệu nào được gửi"}), 400
        
    try:
        user.full_name = data.get('full_name', user.full_name)
        
        new_email = data.get('email')
        if new_email and new_email != user.email:
            if User.query.filter(User.email == new_email, User.id != user.id).first():
                return jsonify({"error": "Xung đột", "message": f"Email '{new_email}' đã được sử dụng"}), 409
            user.email = new_email
            
        dob_str = data.get('date_of_birth')
        if dob_str:
            try:
                user.date_of_birth = datetime.strptime(dob_str, "%d-%m-%Y").date()
            except ValueError:
                return jsonify({"error": "Lỗi định dạng", "message": "Ngày sinh phải theo định dạng dd-mm-YYYY"}), 400

        lecturer.position = data.get('position', lecturer.position)

        new_dept_id = data.get('department_id')
        if new_dept_id and new_dept_id != lecturer.department_id:
            if not Department.query.get(new_dept_id):
                return jsonify({"error": "Không tìm thấy", "message": f"Khoa với ID '{new_dept_id}' không tồn tại"}), 404
            lecturer.department_id = new_dept_id

        db.session.commit()
        
        return jsonify({"message": "Cập nhật thông tin giảng viên thành công"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Lỗi CSDL", "message": str(e)}), 500
4,
@admin_bp.route('/students/<department_id>',methods=["GET"])
@fresh_login_required
def students(department_id):
    if current_user.role != 'admin':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403

    if not Department.query.get(department_id):
        return jsonify({"error": "Lỗi", "message": "Khoa này không tồn tại"}), 404
    try:
        results = db.session.query(
            User.id,
            User.email,
            User.full_name,
            User.date_of_birth,
            Student.entry_year,
            Student.status
        ).join(
            Student, User.id==Student.user_id
        ).filter(
            Student.department_id==department_id
        ).all()
        if not results:
            return jsonify({"message": "Không tìm thấy sinh viên nào trong khoa này."}), 404
        user_data=[]
        for id, email, full_name,date_of_birth,entry_year,status in results:
            user_data.append({
                "id": id,
                "email": email,
                "Họ và Tên": full_name,
                "Ngày sinh":date_of_birth.strftime("%d-%m-%Y") if date_of_birth else None,
                "Trạng thái":"Đang học" if status else "Thôi học",
                "Khóa học":entry_year
            })
        return jsonify(user_data)
    except Exception as e:
        return jsonify({"error":"Lỗi máy chủ","message": str(e)}),500
@admin_bp.route('/students-excel/<department_id>',methods=["GET"])
@fresh_login_required
def students_excel(department_id):
    if current_user.role != 'admin':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403

    if not Department.query.get(department_id):
        return jsonify({"error": "Lỗi", "message": "Khoa này không tồn tại"}), 404
    try:
        results = db.session.query(
            User.id,
            User.email,
            User.full_name,
            User.date_of_birth,
            Student.entry_year,
            Student.status
        ).join(
            Student, User.id==Student.user_id
        ).filter(
            Student.department_id==department_id
        ).all()
        if not results:
            return jsonify({"message": "Không tìm thấy sinh viên nào trong khoa này."}), 404
        user_data=[]
        for id, email, full_name,date_of_birth,entry_year,status in results:
            user_data.append({
                "id": id,
                "email": email,
                "Họ và Tên": full_name,
                "Ngày Sinh":date_of_birth.strftime("%d-%m-%Y") if date_of_birth else None,
                "Trạng thái":"Đang học" if status else "Thôi học",
                "Khóa học":entry_year
            })
    except Exception as e:
        return jsonify({"error":"Lỗi máy chủ","message": str(e)}),500
    try:
        df = pd.DataFrame(user_data)
        output_buffer =BytesIO()
        df.to_excel(output_buffer,index=False)
        output_buffer.seek(0)
        filename=f"Danh_sach_sinh_vien_{department_id}.xlsx"
        return send_file(
            output_buffer,as_attachment=True,
            download_name=filename,
             mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"error": "Lỗi máy chủ", "message": str(e)}), 500
@admin_bp.route('/add_student/<department_id>', methods=["POST"])
@fresh_login_required
def add_student(department_id): 
    if current_user.role != 'admin':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403
    
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error": "Lỗi", "message": "Chưa có dữ liệu được gửi"}), 400

    # Lấy dữ liệu từ JSON payload
    id = data.get("id")
    password = data.get("password")
    full_name = data.get("fullname") # Giả sử frontend gửi 'fullname'
    birthday_str = data.get("date_of_birth")
    email = data.get("email")
    role = 'student' # Gán role là 'student'
    entry_year = data.get("entry_year")
    status = data.get("status")
    
    # Kiểm tra thiếu thông tin
    required_fields = [id, password, full_name, birthday_str, email, entry_year, status]
    if not all(required_fields):
        return jsonify({
            "error": "Thiếu thông tin",
            "message": "Vui lòng nhập đủ: id, password, fullname, date_of_birth, email, entry_year, status"
        }), 400
        
    # Kiểm tra khoa tồn tại (từ URL)
    if not Department.query.get(department_id):
        return jsonify({"error": "Không tìm thấy", "message": f"Khoa với ID '{department_id}' không tồn tại"}), 404
        
    # Kiểm tra trùng lặp ID và Email
    if User.query.get(id):
        return jsonify({"error": "Xung đột", "message": f"ID '{id}' đã tồn tại"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Xung đột", "message": f"Email '{email}' đã tồn tại"}), 409

    try:
        # Xử lý mật khẩu và ngày sinh
        hashed_password = generate_password_hash(password)
        birthday_obj = None
 #       try:
 #           birthday_obj = datetime.strptime(birthday_str, "%d-%m-%Y").date()
 #       except ValueError:
 #           return jsonify({"error": "Lỗi định dạng", "message": "Ngày sinh phải theo định dạng dd-mm-YYYY"}), 400
        try:
            birthday_obj = datetime.strptime(birthday_str, "%d-%m-%Y")  #không dùng .date() — giữ nguyên kiểu datetime.datetime như trong User ở models.py
        except ValueError:
            return jsonify({"error": "Lỗi định dạng", "message": "Ngày sinh phải theo định dạng dd-mm-YYYY"}), 400

        # Tạo bản ghi User
        new_user = User(
            id=id,
            email=email,
            full_name=full_name,
 #           password=hashed_password,  # thuộc tính password không tồn tại trong class User của models.py, chỉ có password_hash
            role=role, # Role là 'student'
            date_of_birth=birthday_obj
        )
        new_user.set_password(password)  # ← dùng setter có sẵn
        db.session.add(new_user)

        # Tạo bản ghi Student
        new_student = Student(
            user_id=id, 
            department_id=department_id, # Lấy từ URL
            entry_year=entry_year,
            status=status
        )
        db.session.add(new_student)
        
        db.session.commit()
        
        return jsonify({
            "message": f"Tạo sinh viên thành công cho khoa {department_id}",
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Lỗi CSDL", "message": str(e)}), 500


# --- API THÊM SINH VIÊN BẰNG FILE EXCEL ---
@admin_bp.route('/upload_excel_student/<department_id>', methods=["POST"])
@fresh_login_required
def upload_excel_student(department_id):
    if current_user.role != 'admin':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403
    
    # Kiểm tra khoa tồn tại
    department = Department.query.get(department_id)
    if not department:
        return jsonify({"error": "Lỗi", "message": "Không tìm thấy khoa này"}), 404

    # Kiểm tra file upload
    if 'file' not in request.files:
        return jsonify({"error": "Lỗi", "message": "Không có file nào được tải lên"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Lỗi", "message": "Chưa chọn file để tải lên."}), 400
    if not file.filename.endswith(('.xlsx', 'xls')):
        return jsonify({"error": "Lỗi định dạng", "message": "Chỉ chấp nhận file Excel (.xlsx, .xls)."}), 400

    # Đọc file Excel
    try:
        df = pd.read_excel(file, dtype=str) # Đọc mọi thứ là chuỗi
        student_list = df.to_dict('records')
    except Exception as e:
        return jsonify({"error": "Lỗi đọc file", "message": f"Không thể đọc file Excel. Lỗi: {str(e)}"}), 400

    # Lấy set ID và Email hiện có
    try:
        set_id = {u.id for u in User.query.with_entities(User.id).all()}
        set_email = {u.email for u in User.query.with_entities(User.email).all()}
    except Exception as e:
        return jsonify({"error": "Lỗi CSDL", "message": str(e)}), 500

    # Khởi tạo list để thêm hàng loạt và list lỗi
    users_to_add = []
    students_to_add = []
    errors = []
    skipped_count = 0

    # Duyệt qua từng hàng trong file Excel
    for idx, row in enumerate(student_list, start=2):
        id = row.get("id")
        email = row.get('email')
        password = row.get('password')
        full_name = row.get('full_name') # Giả sử tên cột là 'full_name'
        dob_str = row.get('date_of_birth')
        entry_year = row.get('entry_year')
        status = row.get('status')

        # 1. Kiểm tra thiếu thông tin
        required_cols = [id, email, password, full_name, dob_str, entry_year, status]
        if not all(required_cols):
            errors.append(f"Hàng {idx}: Thiếu thông tin.")
            continue 

        # 2. Kiểm tra trùng lặp ID và Email
        if id in set_id:
            skipped_count += 1
            continue 
        if email in set_email:
            errors.append(f"Hàng {idx}: Email '{email}' đã tồn tại.")
            continue

        # 3. Xử lý ngày sinh
        try:
            date_of_birth_obj = pd.to_datetime(dob_str, format="%d-%m-%Y").date()
        except (ValueError, TypeError):
            errors.append(f"Hàng {idx}: Ngày sinh '{dob_str}' sai định dạng (phải là dd-mm-YYYY).")
            continue
            
        # 4. Chuẩn bị thêm vào CSDL
        hashed_password = generate_password_hash(password)
        
        new_user = User(
            id=id, email=email, password=hashed_password,
            role='student', full_name=full_name, date_of_birth=date_of_birth_obj
        )
        new_student = Student(
            user_id=id, department_id=department_id, 
            entry_year=entry_year, status=status
        )
        
        users_to_add.append(new_user)
        students_to_add.append(new_student)
        
        # Thêm vào set để kiểm tra trùng lặp ngay trong file
        set_id.add(id)
        set_email.add(email)

    # 5. Xử lý kết quả sau khi duyệt xong
    if errors:
        return jsonify({
            "error": "Dữ liệu file không hợp lệ", "messages": errors,
            "added_count": 0, "skipped_count": skipped_count
        }), 400
        
    if not users_to_add:
        return jsonify({"message": "Không có sinh viên nào mới để thêm.", "skipped_count": skipped_count}), 200

    # 6. Commit vào CSDL nếu không có lỗi
    try:
        db.session.add_all(users_to_add)
        db.session.add_all(students_to_add)
        db.session.commit()
        
        added_count = len(users_to_add)
        return jsonify({
            "message": f"Thêm thành công {added_count} sinh viên.",
            "added_count": added_count, "skipped_count": skipped_count
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Lỗi khi ghi CSDL", "message": str(e)}), 500


# --- API SỬA THÔNG TIN SINH VIÊN ---
@admin_bp.route('/update_student/<student_id>', methods=["PUT"])
@fresh_login_required
def update_student(student_id):
    if current_user.role != 'admin':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403
    
    # Tìm User và Student
    user = User.query.get(student_id)
    if not user:
        return jsonify({"error": "Lỗi", "message": "Không tìm thấy người dùng (sinh viên)"}), 404
    if user.role != 'student':
        return jsonify({"error": "Lỗi", "message": "ID này không phải của sinh viên"}), 400
    student = Student.query.filter_by(user_id=student_id).first()
    if not student:
        return jsonify({"error": "Lỗi CSDL", "message": "Dữ liệu sinh viên không đồng nhất"}), 500
        
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error": "Lỗi", "message": "Không có dữ liệu nào được gửi"}), 400
        
    try:
        # Cập nhật User
        user.full_name = data.get('full_name', user.full_name)
        
        new_email = data.get('email')
        if new_email and new_email != user.email:
            if User.query.filter(User.email == new_email, User.id != user.id).first():
                return jsonify({"error": "Xung đột", "message": f"Email '{new_email}' đã được sử dụng"}), 409
            user.email = new_email
            
        dob_str = data.get('date_of_birth')
        if dob_str:
            try:
                user.date_of_birth = datetime.strptime(dob_str, "%d-%m-%Y").date()
            except ValueError:
                return jsonify({"error": "Lỗi định dạng", "message": "Ngày sinh phải theo định dạng dd-mm-YYYY"}), 400

        # Cập nhật Student
        student.entry_year = data.get('entry_year', student.entry_year)
        student.status = data.get('status', student.status)

        new_dept_id = data.get('department_id')
        if new_dept_id and new_dept_id != student.department_id:
            if not Department.query.get(new_dept_id):
                return jsonify({"error": "Không tìm thấy", "message": f"Khoa với ID '{new_dept_id}' không tồn tại"}), 404
            student.department_id = new_dept_id

        db.session.commit()
        
        return jsonify({"message": "Cập nhật thông tin sinh viên thành công"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Lỗi CSDL", "message": str(e)}), 500
    