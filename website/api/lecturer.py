from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from .. import db
from ..models import Lecturer,User,ClassSection,Enrollment,Student,Room,Course,Terms,Grade,Assignment,AssignmentType,AssignmentWeight
from flask import jsonify
from collections import Counter
import json
#,Department,Exam
# from datetime import date
from .. import login_manager

lecturer_bp=Blueprint('lecturer',__name__)
"""
    Lấy thông tin giảng viên :http://127.0.0.1:5000/api/lecturer/userinfor
    Danh sách các lớp mà giảng viên giảng dạy:http://127.0.0.1:5000/api/lecturer/classSections
    Danh sách sinh viên từng lớp:http://127.0.0.1:5000/api/lecturer/list_student/<class_id>
    Danh sách điểm của sinh viên thuộc lớp nào đó : http://127.0.0.1:5000/api/lecturer/grades/<class_id> (Get là lấy ra điểm còn post sẽ là cập nhật điểm)
    Nhập điểm bằng danh sách 1 list nhé kiểu như này 
    [
        {
        "Chuyên cần": "8",
        "Cuối kì": "9.5",
        "Kiểm tra 1": "10",
        "student_id": "SV002"
        }
    ]
    Lấy ra biết đồ tròn điểm :http://127.0.0.1:5000/api/lecturer/grades/distribution/<class_id>
"""

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# --- KHU VỰC HÀM TRỢ GIÚP TÍNH ĐIỂM ---

def calculate_letter_grade(final_score):
    """
    Hàm chuyển đổi điểm số (0-10) sang điểm chữ.
    """
    if final_score is None:
        return "N/A"
    
    # Giả định thang điểm 10
    if final_score >= 9.0:
        return "A"
    elif final_score >= 8.0:
        return "B+"
    elif final_score >= 7.0:
        return "B"
    elif final_score >= 6.5:
        return "C+"
    elif final_score >= 5.5:
        return "C"
    elif final_score >= 5.0:
        return "D+"
    elif final_score >= 4.0:
        return "D"
    else:
        return "F"

def calculate_enrollment_final_grade(enrollment, weight_map):
    """
    Tính toán điểm cuối cùng (final_grade) và điểm chữ (letter_grade) cho một bản ghi Enrollment.
    Hàm này không commit vào DB.
    """
    grades = Grade.query.filter_by(enrollment_id=enrollment.id).all()
    
    type_grades = {atype: [] for atype in weight_map.keys()}
    final_grade = 0.0
    total_weight = 0.0
    has_zero_grade = False 

    # 1. Phân loại điểm
    for g in grades:
        if g.assignment and g.assignment.assignment_type:
            atype = g.assignment.assignment_type.name
            if atype in type_grades and g.grade is not None:
                type_grades[atype].append(g.grade)
    
    # 2. Tính điểm trung bình từng loại và tính điểm cuối cùng
    for atype, weight in weight_map.items():
        if atype in type_grades and type_grades[atype]:
            avg_grade = sum(type_grades[atype]) / len(type_grades[atype])
            
            # Kiểm tra nếu có điểm trung bình thành phần là 0.0
            if avg_grade == 0.0:
                has_zero_grade = True
            
            final_grade += avg_grade * weight
            total_weight += weight

    letter_grade = "N/A"
    final_grade_rounded = None
    
    if total_weight > 0:
        final_grade_rounded = round(final_grade, 2)
        letter_grade = calculate_letter_grade(final_grade_rounded)
        
        # LOGIC BỔ SUNG: Nếu có bất kỳ điểm 0 nào trong điểm thành phần, ghi đè thành 'F'
        if has_zero_grade:
             letter_grade = "F"
             
    elif not any(v for v in type_grades.values() if v):
        # Chưa nhập bất kỳ điểm nào
        final_grade_rounded = None
        letter_grade = "N/A"
    else:
        # Trường hợp total_weight=0 nhưng có điểm (Lỗi cấu hình trọng số)
        final_grade_rounded = None
        letter_grade = "N/A"
        
    return final_grade_rounded, letter_grade


# --- KHU VỰC ROUTES ---

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
    ).all()
    danh_sach = []
    dem = 1
    
    for student_id, full_name, date_of_birth, email in students_in_class:
        # Kiểm tra và định dạng ngày sinh
        birth_day_str = date_of_birth.strftime("%d-%m-%Y") if date_of_birth else None

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

    # Lấy thông tin assignment IDs
    assignments = Assignment.query.filter_by(class_id=class_id).all()
    assignment_map = {a.assignment_type.name: a.id for a in assignments}
    
    updated_enrollments = [] # Danh sách các đối tượng enrollment cần tính lại điểm cuối cùng

    for g in grade_list:
        student_id = g.get("student_id")

        # Tìm enrollment tương ứng
        enrollment = Enrollment.query.filter_by(student_id=student_id, class_id=class_id).first()
        if not enrollment:
            print(f"Bỏ qua: Sinh viên {student_id} không đăng ký lớp {class_id}")
            continue
        
        # Thêm vào danh sách cần tính lại điểm cuối cùng
        if enrollment not in updated_enrollments:
            updated_enrollments.append(enrollment)

        # Duyệt qua các loại điểm thô và cập nhật
        for key, assignment_id in assignment_map.items():
            raw_score = g.get(key)
            
            # Xử lý trường hợp không nhập điểm
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

            # Kiểm tra phạm vi điểm (0 đến 10)
            if not (0 <= score <= 10):
                db.session.rollback()
                return jsonify({
                    "error": "Lỗi giá trị",
                    "message": f"Điểm '{key}' của sinh viên {student_id} phải nằm trong khoảng 0-10."
                }), 400

            # 2. THỰC HIỆN CẬP NHẬT/TẠO MỚI GRADE (Điểm thô)
            grade = Grade.query.filter_by(enrollment_id=enrollment.id, assignment_id=assignment_id).first()
            if not grade:
                grade = Grade(enrollment_id=enrollment.id, assignment_id=assignment_id, grade=score)
                db.session.add(grade)
            else:
                grade.grade = score

    # 3. TÍNH VÀ CẬP NHẬT ĐIỂM CUỐI CÙNG VÀO ENROLLMENT (final_grade, letter_grade)
    weights_query = AssignmentWeight.query.filter_by(class_id=class_id).all()
    weight_map = {w.assignment_type.name: w.weight / 10.0 for w in weights_query}
    
    try:
        for e in updated_enrollments:
            # TÍNH TOÁN ĐIỂM CUỐI CÙNG VÀ ĐIỂM CHỮ
            final_grade, letter_grade = calculate_enrollment_final_grade(e, weight_map) 
            
            # Cập nhật Enrollment chỉ khi có thay đổi
            if e.final_grade != final_grade or e.letter_grade != letter_grade:
                e.final_grade = final_grade
                e.letter_grade = letter_grade
                db.session.add(e)

        # 4. COMMIT DỮ LIỆU CẢ ĐIỂM THÔ VÀ ĐIỂM CUỐI CÙNG
        db.session.commit()
        return jsonify({"message": "Cập nhật điểm thô và tính toán/lưu điểm cuối cùng thành công!"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Lỗi hệ thống khi tính điểm cuối cùng", "message": str(e)}), 500


@lecturer_bp.route("/grades/<class_id>", methods=["GET"])
# @login_required # Tùy chọn: nếu chỉ giảng viên mới được xem, hãy bật lại dòng này
def get_class_grades(class_id):
    """
    Chỉ lấy ra (READ) các điểm thô, điểm trung bình thành phần và điểm cuối cùng (đã được tính và lưu trước đó).
    """
    
    # 1. Lấy thông tin trọng số điểm của lớp học (Chỉ để biết các cột điểm cần hiển thị)
    weights_query = AssignmentWeight.query.filter_by(class_id=class_id).all()
    weight_map = {w.assignment_type.name: w.weight / 10.0 for w in weights_query}
    
    # 2. Lấy danh sách sinh viên đăng ký lớp này
    enrollments = Enrollment.query.filter_by(class_id=class_id).all()
    result = []

    for e in enrollments:
        student = e.student_ref
        grades = Grade.query.filter_by(enrollment_id=e.id).all()
        
        # Khởi tạo dữ liệu điểm thành phần (sẽ hiển thị điểm trung bình)
        grade_data = {atype: "" for atype in weight_map.keys()}
        type_grades_list = {atype: [] for atype in weight_map.keys()}
        
        # Phân loại điểm thô
        for g in grades:
            if g.assignment and g.assignment.assignment_type:
                atype = g.assignment.assignment_type.name
                if atype in type_grades_list and g.grade is not None:
                    type_grades_list[atype].append(g.grade)
                    
        # Tính điểm trung bình thành phần để hiển thị
        for atype in weight_map.keys():
             if type_grades_list[atype]:
                avg_grade = sum(type_grades_list[atype]) / len(type_grades_list[atype])
                grade_data[atype] = round(avg_grade, 2)
             else:
                grade_data[atype] = ""

        # LẤY KẾT QUẢ ĐIỂM CUỐI CÙNG ĐÃ ĐƯỢC LƯU SẴN TỪ ENROLLMENT
        final_grade_db = e.final_grade
        letter_grade_db = e.letter_grade if e.letter_grade is not None else ""
            
        # 3. Cập nhật kết quả
        result.append({
            "student_id": student.user_id,
            "student_name": student.user.full_name,
            **grade_data,
            "final_grade": final_grade_db if final_grade_db is not None else "", 
            "letter_grade": letter_grade_db
        })
    
    # 4. Trả về kết quả (KHÔNG CÓ COMMIT)
    return jsonify(result)

@lecturer_bp.route("/grades/distribution/<class_id>", methods=["GET"])
def get_grade_distribution(class_id):
    # 1. Lấy tất cả các bản ghi Enrollment cho lớp học này
    enrollments = Enrollment.query.filter_by(class_id=class_id).all()

    if not enrollments:
        return jsonify({"message": "Không tìm thấy sinh viên nào đăng ký lớp học này."}), 404

    # 2. Lấy danh sách tất cả các điểm chữ đã được tính và lưu
    letter_grades = [
        e.letter_grade 
        for e in enrollments 
        if e.letter_grade is not None and e.letter_grade != "N/A" # Chỉ đếm các điểm đã được tính
    ]

    # 3. Đếm số lượng sinh viên cho mỗi loại điểm chữ
    grade_counts = Counter(letter_grades)

    # 4. Chuyển đổi dữ liệu sang định dạng phù hợp cho biểu đồ tròn
    chart_data = []
    
    # Định nghĩa màu sắc cố định cho các loại điểm
    color_map = {
        "A": "#4CAF50",      # Green (Tốt)
        "B+": "#8BC34A",     # Light Green
        "B": "#CDDC39",      # Lime
        "C+": "#FFEB3B",     # Yellow (Trung bình)
        "C": "#FFC107",      # Amber
        "D+": "#FF9800",     # Orange
        "D": "#FF5722",      # Deep Orange
        "F": "#F44336",      # Red (Rớt)
    }

    total_graded_students = len(letter_grades)
    
    for grade, count in grade_counts.items():
        chart_data.append({
            "name": grade,
            "value": count,
            "percentage": round((count / total_graded_students) * 100, 1) if total_graded_students > 0 else 0,
            "color": color_map.get(grade, "#B0BEC5")
        })

    # 5. Trả về JSON
    return jsonify({
        "class_id": class_id,
        "total_graded_students": total_graded_students,
        "distribution": chart_data
    })
