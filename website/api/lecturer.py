from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from .. import db
from ..models import Lecturer,User,ClassSection,Enrollment,Student,Room,Course,Terms,Grade,Assignment,AssignmentType,AssignmentWeight
#,Department,Exam
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
            "id":i.id,
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
@lecturer_bp.route("/grades/<class_id>", methods=["GET"])
def get_class_grades(class_id):
    # Lấy danh sách assignment (bài kiểm tra) của lớp
    assignments = Assignment.query.filter_by(class_id=class_id).limit(3).all()

    # Map tên loại điểm -> ID assignment
    assignment_map = {}
    for a in assignments:
        assignment_map[a.assignment_type.name] = a.id

    # Lấy danh sách sinh viên đăng ký lớp này
    enrollments = Enrollment.query.filter_by(class_id=class_id).all()
    result = []

    for e in enrollments:
        student = e.student_ref
        grades = Grade.query.filter_by(enrollment_id=e.id).all()

        # Tạo dict chứa 3 loại điểm mặc định rỗng
        grade_data = {atype: "" for atype in assignment_map.keys()}

        for g in grades:
            atype = g.assignment.assignment_type.name
            if atype in grade_data:  # chỉ cập nhật 3 loại điểm đầu tiên
                grade_data[atype] = g.grade if g.grade is not None else ""

        # Ghi chú nếu chưa nhập điểm nào
        if all(v == "" for v in grade_data.values()):
            note = "Chưa nhập điểm"
        else:
            note = ""

        result.append({
            "student_id": student.user_id,
            "student_name": student.user.full_name,
            **grade_data,
            "note": note
        })

    return jsonify(result)
@lecturer_bp.route("/grades/<class_id>", methods=["POST"])
@login_required
def update_class_grades(class_id):
    # 1. KIỂM TRA PHÂN QUYỀN VÀ LỚP HỌC 
    
    # a. Kiểm tra vai trò
    if current_user.role != 'lecturer':
        return jsonify({"error": "Không thành công", "message": "Bạn không phải là giảng viên"}), 403

    # b. Kiểm tra tồn tại và quyền sở hữu lớp
    class_section = ClassSection.query.get(class_id)
    if not class_section:
        return jsonify({"error": "Lỗi", "message": "Không tìm thấy lớp học."}), 404

    if class_section.lecturer_id != current_user.id:
        return jsonify({"error": "Không thành công", "message": "Bạn không phụ trách lớp học này"}), 403

    # Lấy dữ liệu từ request
    data = request.get_json()
    grade_list = data if isinstance(data, list) else data.get("grades", [])

    # Lấy 3 assignment đầu tiên của lớp
    assignments = Assignment.query.filter_by(class_id=class_id).limit(3).all()
    assignment_map = {a.assignment_type.name: a.id for a in assignments}

    for g in grade_list:
        student_id = g.get("student_id")

        # Tìm enrollment tương ứng
        enrollment = Enrollment.query.filter_by(student_id=student_id, class_id=class_id).first()
        if not enrollment:
            print(f"Bỏ qua: Sinh viên {student_id} không đăng ký lớp {class_id}")
            continue

        # Duyệt qua 3 loại điểm
        for key, assignment_id in assignment_map.items():
            raw_score = g.get(key)
            
            # Xử lý trường hợp không nhập điểm (chuỗi rỗng, None)
            if raw_score == "" or raw_score is None:
                continue

            try:
                score = float(raw_score)
            except ValueError:
                # Trả về lỗi nếu điểm không phải là số
                db.session.rollback()
                return jsonify({
                    "error": "Lỗi định dạng",
                    "message": f"Điểm '{key}' của sinh viên {student_id} phải là số."
                }), 400

            # Kiểm tra phạm vi điểm (ví dụ: từ 0 đến 10)
            if not (0 <= score <= 10):
                db.session.rollback()
                return jsonify({
                    "error": "Lỗi giá trị",
                    "message": f"Điểm '{key}' của sinh viên {student_id} phải nằm trong khoảng 0-10."
                }), 400

            # 2. THỰC HIỆN CẬP NHẬT/TẠO MỚI GRADE
            grade = Grade.query.filter_by(enrollment_id=enrollment.id, assignment_id=assignment_id).first()
            if not grade:
                grade = Grade(enrollment_id=enrollment.id, assignment_id=assignment_id, grade=score)
                db.session.add(grade)
            else:
                grade.grade = score

    # 3. COMMIT DỮ LIỆU
    try:
        db.session.commit()
        return jsonify({"message": "Cập nhật điểm cho lớp thành công!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Lỗi hệ thống", "message": str(e)}), 500



