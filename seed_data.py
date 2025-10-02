import random
from zoneinfo import available_timezones

from website import create_app, db
from website.models import User, Lecturer, Student, Department, Terms, Room, Course, ClassSection, Enrollment, Exam, Grade
from datetime import date, datetime, timedelta
from random import choice, randint, uniform, sample
from sqlalchemy import Numeric 

app = create_app()

PASSWORD_DEFAULT = '123456'
DEPARTMENT_IDS_EXISTING = ["CNTT1", "KVT1", "KTDT1", "QTKT1", "ATTT", "TTNT", "TCKT", "DPT"]
POSITION_EXISTING = ["Giảng viên", "Giảng viên", "Trưởng bộ môn", "Trưởng khoa"]

data_to_add = []

first_names_male = ["An", "Bảo", "Cường", "Đạt", "Giang", "Huy", "Khoa", "Minh", "Nam", "Quang"]
first_names_female = ["Anh", "Chi", "Hà", "Hương", "Linh", "Mai", "Ngọc", "Thảo", "Trang", "Yến"]
last_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Vũ", "Đặng", "Bùi", "Đỗ", "Mai", "Đinh"]

# Tao 1 admin -------------------------------------------------------------------------------------------
admin_users_data = []

def generate_admin():
    user = User(id='ADM001', email='none', role="admin", full_name='Adminstator', date_of_birth=None)
    user.set_password(PASSWORD_DEFAULT)
    admin_users_data.extend([user])
    data_to_add.extend(admin_users_data)
    print("Admin added")

# Tao 100 sinh vien -------------------------------------------------------------------------------------------
student_users_data = []
all_student_ids = []

def generate_student():
    for i in range(1, 101):
        user_id = f"SV{i:03d}"
        all_student_ids.append(user_id)
        email = f"{user_id}@std.ptit.edu.vn"

        is_male = choice([True, False])
        first_name = choice(first_names_male) if is_male else choice(first_names_female)
        full_name = f"{choice(last_names)} {choice(['Văn', 'Thị', 'Đức', 'Thu'])} {first_name}"

        birth_year = randint(2004, 2006)
        date_of_birth = date(birth_year, randint(1, 12), randint(1, 28))

        dept_id = choice(DEPARTMENT_IDS_EXISTING)
        entry_year = 2024

        user = User(id=user_id, email=email, role="student", full_name=full_name, date_of_birth=date_of_birth)
        user.set_password(PASSWORD_DEFAULT)
        student = Student(user_id=user_id, department_id=dept_id, entry_year=entry_year, status=True)

        student_users_data.extend([user, student])

    data_to_add.extend(student_users_data)
    print("100 students created")


# Tao 10 giang vien -------------------------------------------------------------------------------------------
lecturer_users_data = []
all_lecturer_ids = []

def generate_lecturer():
    for i in range(1, 6):
        user_id = f"GV{i:03d}"
        all_lecturer_ids.append(user_id)
        email = f"{user_id}@std.ptit.edu.vn"

        is_male = choice([True, False])
        first_name = choice(first_names_male) if is_male else choice(first_names_female)
        full_name = f"{choice(last_names)} {choice(['Văn', 'Thị', 'Đức', 'Thu'])} {first_name}"

        birth_year = randint(1970, 2000)
        date_of_birth = date(birth_year, randint(1, 12), randint(1, 28))

        dept_id = choice(DEPARTMENT_IDS_EXISTING)

        user = User(id=user_id, email=email, role="lecturer", full_name=full_name, date_of_birth=date_of_birth)
        user.set_password(PASSWORD_DEFAULT)
        lecturer = Lecturer(user_id=user_id, department_id=dept_id, position_id=choice(POSITION_EXISTING))

        lecturer_users_data.extend([user, lecturer])

    data_to_add.extend(lecturer_users_data)
    print("5 lecturers created")


# Tao cac du lieu con lai -------------------------------------------------------------------------------
def generate_other_data():
    # Tao terms
    terms = [
        Terms(id="20241", name="Học kỳ I - Năm Nhất (2024)", start_date=datetime(2024, 9, 5), end_date=datetime(2025, 1, 15)),
    ]
    data_to_add.extend(terms)
    print("terms created")
    
    # Tao 10 phong hoc
    rooms = []
    for building in ['A2', 'A3']:
        max_floor = 8 if building == 'A2' else 6
        for floor in range(1, max_floor + 1):
            for room_num in range(101, 106):
                room_id = f"R{building}{floor}{room_num % 100}" 
                room_name = f"Phòng {room_num} - Tầng {floor}"
                rooms.append(Room(id=room_id, name=room_name, location=f"Tòa {building} Tầng {floor}"))
    
    room_ids_for_class = [r.id for r in rooms[:10]]
    data_to_add.extend(rooms[:10])
    print("10 rooms created")
    
    # Tao 6 khoa hoc
    courses = [
        Course(id="IT101", department_id="CNTT1", name="Nhập môn Lập trình C", credits=3, theory_hours=45, practice_hours=0, description="Cơ bản về ngôn ngữ C."),
        Course(id="IT102", department_id="CNTT1", name="Toán Cao cấp A1", credits=3, theory_hours=45, practice_hours=0, description="Đại số tuyến tính và Hình học giải tích."),
        Course(id="KVT103", department_id="KVT1", name="Vật lý Đại cương", credits=3, theory_hours=30, practice_hours=15, description="Cơ học và Nhiệt học."),
        Course(id="QT201", department_id="QTKT1", name="Kinh tế Chính trị Mác-Lênin", credits=3, theory_hours=45, practice_hours=0, description="Nguyên lý cơ bản."),
        Course(id="AT202", department_id="ATTT", name="Tin học Đại cương", credits=2, theory_hours=30, practice_hours=0, description="Cơ bản về máy tính và Internet."),
        Course(id="TC301", department_id="TCKT", name="Tiếng Anh 1", credits=3, theory_hours=45, practice_hours=0, description="Ngữ pháp và từ vựng cơ bản."),
    ]
    data_to_add.extend(courses)
    course_ids = [c.id for c in courses]
    print("6 courses created")

    # Tao lop hoc phan - classSection
    random.shuffle(all_lecturer_ids)
    term_id = "20241"
    
    class_sections = []
    class_details = [
        ("C101-241A", course_ids[0], all_lecturer_ids[0], term_id, room_ids_for_class[0], 30, 1), # IT101 - Nhóm A
        ("C101-241B", course_ids[0], all_lecturer_ids[1], term_id, room_ids_for_class[1], 30, 2), # IT101 - Nhóm B
        ("C102-241", course_ids[1], all_lecturer_ids[2], term_id, room_ids_for_class[2], 30, 3), # Toán A1
        ("C301-241", course_ids[2], all_lecturer_ids[3], term_id, room_ids_for_class[3], 30, 4), # Vật lý
        ("C401-241", course_ids[3], all_lecturer_ids[4], term_id, room_ids_for_class[4], 30, 5), # KT Chính trị
        ("C501-241", course_ids[4], all_lecturer_ids[0], term_id, room_ids_for_class[5], 30, 6), # Tin học ĐC
        ("C601-241A", course_ids[5], all_lecturer_ids[1], term_id, room_ids_for_class[6], 30, 7), # Tiếng Anh 1 - Nhóm A
        ("C601-241B", course_ids[5], all_lecturer_ids[2], term_id, room_ids_for_class[7], 30, 8), # Tiếng Anh 1 - Nhóm B
        ("C202-241", course_ids[1], all_lecturer_ids[3], term_id, room_ids_for_class[8], 30, 9), # Toán A1 (Nhóm khác)
        ("C302-241", course_ids[2], all_lecturer_ids[4], term_id, room_ids_for_class[9], 30, 10), # Vật lý (Nhóm khác)
    ]
    
    term_20241 = terms[0]
    for class_id, course_id, lecturer_id, _, room_id, max_std, sch in class_details:
        class_sections.append(ClassSection(
            id=class_id, course_id=course_id, lecturer_id=lecturer_id, 
            term_id=term_20241.id, room_id=room_id, max_students=max_std, 
            schedule=sch, start_date=term_20241.start_date, end_date=term_20241.end_date
        ))
    data_to_add.extend(class_sections)
    class_section_ids = [cs.id for cs in class_sections]
    print("10 classSections created")

    # Tao bang dang ki lop hoc - Enrollment
    enrollments = []
    enrollment_id_counter = 1
    slots = {c:40 for c in class_section_ids}

    for student_id in all_student_ids:
        available_class_ids = [c for c in class_section_ids if slots[c] > 0]
        classes_for_student = sample(available_class_ids, 3)
        
        for class_id in classes_for_student:
            slots[class_id] -= 1
            enrollment_id = f"E{enrollment_id_counter:04d}"
            enrollments.append(Enrollment(
                id=enrollment_id, student_id=student_id, class_id=class_id, status=True
            ))
            enrollment_id_counter += 1
            
    data_to_add.extend(enrollments)
    print("enrollments created")
    
    
    # Tao bang Exam va Grade trống
    exams = []
    grades = []
    grade_id_counter = 1
    
    for cls in class_sections:
        exam_mid = Exam(id=f"EXM{cls.id}M", class_id=cls.id, name="Giữa kỳ (40%)", max_score=10, weight=40)
        exam_final = Exam(id=f"EXM{cls.id}F", class_id=cls.id, name="Cuối kỳ (60%)", max_score=10, weight=60)
        exams.extend([exam_mid, exam_final])
        
        # Lấy tất cả các enrollment của lớp này
        class_enrollments = [e for e in enrollments if e.class_id == cls.id]
        
        for enrollment in class_enrollments:
            # TẠO BẢN GHI GRADE TRỐNG CHO ĐIỂM GIỮA KỲ
            grades.append(Grade(
                id=f"G{grade_id_counter:06d}", enrollment_id=enrollment.id, exam_id=exam_mid.id, 
                final_score=0.0, letter_score="", notes="Chờ nhập điểm"
            ))
            grade_id_counter += 1
            
            # TẠO BẢN GHI GRADE TRỐNG CHO ĐIỂM CUỐI KỲ
            grades.append(Grade(
                id=f"G{grade_id_counter:06d}", enrollment_id=enrollment.id, exam_id=exam_final.id, 
                final_score=0.0, letter_score="", notes="Chờ nhập điểm"
            ))
            grade_id_counter += 1

    data_to_add.extend(exams)
    data_to_add.extend(grades)
    print("exams created")

# Ham main -------------------------------------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        try:
            print("--- BẮT ĐẦU SEED DỮ LIỆU MẪU (100 SV, HK 20241, GRADE TRỐNG) ---")
            generate_admin()
            generate_student()
            generate_lecturer()
            generate_other_data()

            db.session.add_all(data_to_add)

            db.session.commit()
            print("Đã khởi tạo thành công toàn bộ dữ liệu mẫu (100 SV, chỉ HK 20241).")

        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi thêm dữ liệu mẫu. Đã rollback: {e}")