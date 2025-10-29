from flask import Blueprint, jsonify, request,send_file
from flask_login import fresh_login_required, current_user
from .. import db
from io import BytesIO
from ..models import User,ClassSection,Enrollment,Student,Course,Terms,Grade,Assignment,AssignmentType
from sqlalchemy.orm import joinedload
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
-Lấy ra danh sách sinh viên lớp bạn thuộc trong kỳ đó: http://127.0.0.1:5000/api/student/list-student/<class_id>/<term_id>(GET)
-Lấy ra  file excel danh sách sinh viên lớp bạn thuộc trong kỳ đó: http://127.0.0.1:5000/api/student/list_student/export-excel/<class_id>(GET)
-Lấy ra thông tin chi tiết các môn bạn đã đăng ký (trong kỳ): http://127.0.0.1:5000/api/student/courses/<term_id>(GET)
-Lấy ra thông tin chi tiết và điểm một môn của bạn: http://127.0.0.1:5000/api/student/grade/<course_id>(GET)

"""

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
# lấy thông tin sinh viên
@student_bp.route('/profile',methods=['GET'])
@fresh_login_required
def get_profile():
    if current_user.role!='student' :
        return jsonify({"error":"Lỗi","message":"Bạn không phải là sinh viên"}), 403
    user_data = {
        "Mã sinh viên":current_user.id,
        "Họ và tên":current_user.full_name,
        "Ngày sinh":current_user.date_of_birth.strftime("%d-%m-%Y") if current_user.date_of_birth else None,
        "Email":current_user.email,
        "Chức Danh":"Sinh viên"
    }
    user_data["Thông tin khóa học"]={
        "Tên khoa":current_user.student.department.name,
        "Năm bắt đầu":current_user.student.entry_year,
        "Trạng thái":"Đang học" if current_user.student.status else "Thôi học"
    }
    return jsonify(user_data), 200
# Sửa thông tin sinh viên
@student_bp.route('/profile',methods=['PUT'])
@fresh_login_required
def update_profile():
    if current_user.role!='student' :
        return jsonify({"error":"Lỗi","message":"Bạn không phải là sinh viên"}), 403
    data=request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error": "Lỗi", "message": "Không có dữ liệu nào được gửi"}), 400
    try:
        current_user.full_name=data.get('full_name',current_user.full_name)
        new_email=data.get('email')
        if new_email and new_email != current_user.email:
            if User.query.filter_by(email=new_email).first():
                return jsonify({"error": "Xung đột", "message": f"Email '{new_email}' đã được sử dụng"}), 409
            current_user.email=new_email
        dob=data.get('date_of_birth')
        if dob:
            try:
                current_user.date_of_birth = datetime.strptime(dob, "%d-%m-%Y")
            except ValueError:
                return jsonify({"error": "Lỗi định dạng", "message": "Ngày sinh phải theo định dạng dd-mm-YYYY"}), 400
        db.session.commit()
        return jsonify({"message": "Cập nhật thông tin sinh viên thành công"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Lỗi CSDL", "message": str(e)}), 500
# Lấy ra các kỳ đã và đang học
@student_bp.route('/terms',methods=['GET'])
@fresh_login_required
def terms():
    if current_user.role!='student' :
        return jsonify({"error":"Lỗi","message":"Bạn không phải là sinh viên"}), 403
    semesters = db.session.query(Terms)\
    .join(ClassSection, Terms.id == ClassSection.term_id) \
    .join(Enrollment, ClassSection.id == Enrollment.class_id) \
    .filter(Enrollment.student_id == current_user.id) \
    .distinct() \
    .all()
    user_data=[]
    for sem in semesters:
        user_data.append({"Mã kỳ học":sem.id,
                          "Tên kỳ học":sem.name,
                          "Ngày bắt đầu":sem.start_date.strftime("%d-%m-%Y"),
                          "Ngày kết thúc":sem.end_date.strftime("%d-%m-%Y")
                          })
    return jsonify(user_data), 200        
# Lấy ra các lớp đã đăng ký (Trong Kỳ)
@student_bp.route('/enrollments/<term_id>',methods=['GET'])
@fresh_login_required
def enrollments(term_id):
    if current_user.role!='student' :
        return jsonify({"error":"Lỗi","message":"Bạn không phải là sinh viên"}), 403
    term=Terms.query.get(term_id)
    if not term:
        return jsonify({
            "error":"Lỗi",
            "message":"Không có học kỳ nào như vậy"
        }), 404
    classSections=db.session.query(ClassSection)\
    .join(Enrollment,ClassSection.id==Enrollment.class_id)\
    .filter(Enrollment.student_id==current_user.id ,
             ClassSection.term_id==term_id)\
    .all()
    user_data=[]
    for c in classSections:
        user_data.append({
            "Mã lớp":c.id,
            "Mã Môn":c.course_id,
            "Tên Môn":c.course.name,
            "Giảng viên phụ trách":c.lecturer_ref.user.full_name,
            "Phòng học":c.room.name,
            "Học sinh tối đa":c.max_students,
            "Ngày bắt đầu": c.start_date.strftime("%d-%m-%Y") if c.start_date else None,
            "Ngày kết thúc": c.end_date.strftime("%d-%m-%Y") if c.end_date else None
        })
    if not user_data:
        return jsonify({
            "error":"Lỗi",
            "message":"Không có lớp nào được đăng ký"
        }), 404
    return jsonify(user_data),200

# Lấy ra danh sách sinh viên một lớp bạn thuộc trong kỳ đó
@student_bp.route('/list-student/<class_id>/<term_id>',methods=['GET'])
@fresh_login_required
def list_student(class_id,term_id):
    if current_user.role!='student' :
        return jsonify({"error":"Lỗi","message":"Bạn không có quyền truy cập"}), 403
    if not Enrollment.query.filter_by(student_id=current_user.id , class_id=class_id).first():
        return jsonify({
            "error":"lỗi",
            "message":"Bạn không thuộc lớp này hoặc lớp bản gửi không tồn tại"
        }), 403
    if not ClassSection.query.filter_by(id=class_id,term_id=term_id).first():
        return jsonify({
            "error":"lỗi",
            "message":"Lớp này không tồn tại hoặc học kỳ bạn gửi sai"
        }), 404
    user_data=[]
    dem = 1
    students = db.session.query(
    User.id,
    User.full_name,
    User.date_of_birth,
    User.email
    ).join(
    Student, User.id == Student.user_id
    ).join(
    Enrollment, Student.user_id == Enrollment.student_id
    ).join(
    ClassSection, Enrollment.class_id == ClassSection.id  
    ).filter(
    Enrollment.class_id == class_id,                   
    ClassSection.term_id == term_id                    
    ).all()
    for student_id, full_name, date_of_birth, email in students:
        birth_day_str = date_of_birth.strftime("%d-%m-%Y") if date_of_birth else None
        user_data.append({
            "STT":dem,
            "Họ và tên": full_name,
            "id": student_id,
            "email": email,
            "Ngày sinh": birth_day_str
        })
        dem+=1
    if not user_data:
        return jsonify({"message": "Không có sinh viên nào trong lớp này hoặc ID lớp không hợp lệ."}), 404
    else:
        return jsonify(user_data), 200
@student_bp.route("/list_student/export-excel/<class_id>", methods=["GET"])
@fresh_login_required
def export_student_list_excel(class_id):
    """
    API để xuất danh sách sinh viên của một lớp ra file Excel.
    (Đã sửa lỗi logic bảo mật)
    """
    
    # --- BƯỚC 1: KIỂM TRA QUYỀN VÀ LỚP HỌC ---

    # Check 1: Phải là sinh viên
    if current_user.role != 'student':
        return jsonify({"error": "Không thành công", "message": "Bạn không có quyền truy cập"}), 403

    # Check 2: (SỬA LỖI) Sinh viên phải là thành viên của lớp này
    enrollment = Enrollment.query.filter_by(
        student_id=current_user.id,
        class_id=class_id
    ).first()

    if not enrollment:
        return jsonify({"error": "Không thành công", "message": "Bạn không thuộc lớp học này"}), 403

    # Check 3: Lấy thông tin lớp học (an toàn vì đã xác thực SV ở trên)
    class_section = ClassSection.query.get(class_id)
    if not class_section:
         # Check này gần như thừa, nhưng để cho an toàn
        return jsonify({"error": "Lỗi", "message": "Không tìm thấy lớp học."}), 404

    # --- BƯỚC 2: TRUY VẤN DỮ LIỆU (Code gốc của bạn đã đúng) ---
    students_in_class = db.session.query(
        User.id, 
        User.full_name, 
        User.email,
        User.date_of_birth
    ).join(
        Student, User.id == Student.user_id
    ).join(
        Enrollment, Student.user_id == Enrollment.student_id
    ).filter(
        Enrollment.class_id == class_id
    ).order_by(User.id).all()

    if not students_in_class:
        return jsonify({"message": "Lớp học này chưa có sinh viên."}), 404

    # --- BƯỚC 3: CHUẨN BỊ DỮ LIỆU CHO EXCEL (Code gốc của bạn đã đúng) ---
    data_for_excel = []
    stt = 1
    for student_id, full_name, email, date_of_birth in students_in_class:
        data_for_excel.append({
            "STT": stt,
            "Mã SV": student_id,
            "Họ và Tên": full_name,
            "Email": email,
            "Ngày Sinh": date_of_birth.strftime("%d-%m-%Y") if date_of_birth else ""
        })
        stt += 1
    
    # --- BƯỚC 4: TẠO VÀ GỬI FILE EXCEL (Code gốc của bạn đã đúng) ---
    try:
        df = pd.DataFrame(data_for_excel)
        output_buffer = BytesIO()
        
        # Tạo tên file
        filename = f"Danh_sach_SV_Lop_{class_section.id}.xlsx"

        df.to_excel(output_buffer, index=False, sheet_name=f"Lop_{class_section.id}")
        output_buffer.seek(0)
        
        return send_file(
            output_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"error": "Lỗi hệ thống khi tạo file Excel", "message": str(e)}), 500
@student_bp.route('/courses/<term_id>',methods=['GET'])
@fresh_login_required
def courses(term_id):
    if current_user.role!='student' :
        return jsonify({"error":"Lỗi","message":"Bạn không có quyền truy cập"}), 403
    if not Terms.query.get(term_id):
        return jsonify({
            "error":"Lỗi",
            "message":"Không có học kỳ nào như vậy"
        }), 404
    list_course = db.session.query(Course)\
    .join(ClassSection, Course.id == ClassSection.course_id) \
    .join(Enrollment, ClassSection.id == Enrollment.class_id) \
    .filter(
        Enrollment.student_id == current_user.id,
        ClassSection.term_id == term_id
    )\
    .all()
    user_data=[]
    for c in list_course:
        user_data.append({
            "Mã Môn Học":c.id,
            "Tên Môn học":c.name,
            "Số tín":c.credits,
            "Số tiết lý thuyết":c.theory_hours,
            "Số tiết thực hành":c.practice_hours
        })
    if not user_data:
        return jsonify({
                "message": "Không có danh sách môn nào."
        }), 404
    return jsonify(user_data)

# Lấy ra thông tin chi tiết và điểm một môn của bạn
@student_bp.route('/grade/<course_id>', methods=['GET'])
@fresh_login_required
def grade(course_id):
    if current_user.role != 'student':
        return jsonify({"error": "Lỗi", "message": "Bạn không có quyền truy cập"}), 403

    enrollment = db.session.query(Enrollment)\
        .join(ClassSection, Enrollment.class_id == ClassSection.id)\
        .filter(
            Enrollment.student_id == current_user.id,
            ClassSection.course_id == course_id
        )\
        .options(
            # Tải luôn relationship 'class_section' để dùng ở dưới
            joinedload(Enrollment.class_section).joinedload(ClassSection.course),
            joinedload(Enrollment.class_section).joinedload(ClassSection.term)
        )\
        .first() # Lấy bản ghi đầu tiên tìm thấy

    if not enrollment:
        return jsonify({
            "error": "lỗi",
            "message": "Bạn không đăng ký môn học này, hoặc môn học không tồn tại."
        }), 404

    # Bây giờ ta đã có 'enrollment' chính xác
    # Và có thể truy cập 'class_section' qua relationship
    class_section = enrollment.class_section 

    # --- Phần code này của bạn đã đúng ---
    component_grades_query = db.session.query(
        AssignmentType.name,
        Grade.grade
    ).join(
        Assignment, Assignment.assignment_type_id == AssignmentType.id
    ).join(
        Grade, Grade.assignment_id == Assignment.id
    ).filter(
        Grade.enrollment_id == enrollment.id
    ).all()

    grade_details = []
    for name, score in component_grades_query:
        grade_details.append({
            "Tên điểm": name,
            "Điểm": score
        })

    # --- Phần này của bạn bây giờ sẽ hoạt động ---
    return jsonify({
        "MSV": current_user.id,
        "Họ và tên": current_user.full_name,
        "Tên môn học": class_section.course.name, # Đã hoạt động
        "Mã lớp": class_section.id,           # Đã hoạt động
        "Kỳ học": class_section.term.name,     # Đã hoạt động
        "Điểm thành phần": grade_details,
        "Tổng kết": {
            "Điểm số": enrollment.final_grade,
            "Điểm chữ": enrollment.letter_grade
        }
    }), 200