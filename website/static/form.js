/* Các hàm:
1. Xử lý ẩn/hiện đối với các form đăng nhập, đăng xuất, đổi mk
2. Đăng nhập - login
3. Đăng xuất - logout
4. Đổi mật khẩu - set password
5. Quên mật khẩu (chưa có API) - BỎ QUA
6. Lấy thông tin sinh viên - trang chủ
7. Sửa thông tin sinh viên - newInfor
8. Lấy các kỳ đã và đang học - term GET - !!! CHUA CO .HTML
9. Lấy ra các lớp đã đăng ký trong Kỳ học - lớp tín chỉ
10. Lấy danh sách sinh viên cùng lớp - lớp tín chỉ/ds_banHoc
11. Lấy file execl danh sách sinh viên
12. lấy thông tin các môn đã đăng ký
13. Lấy thông tin chi tiết về điểm của 1 môn học
*/
//1. Hàm sử lý ẩn/hiện
function showForm(formName){
    // Nếu không phải ở trang index.html thì bỏ qua
    if (!window.location.pathname.includes("index.html")) return;
    if(!formName){
        return; // Nếu không có formName thì bỏ qua
    }
    // Ẩn tất cả các form - ở trang .html nào
    document.querySelectorAll("form").forEach(form => form.hidden =true);
    // Hiện form theo tên truyền vào
    const formToShow = document.getElementById(formName + 'Form');
    if(formToShow){
        formToShow.hidden=false;
    }
}
// Xử lý tính năng liên kết với trang khác
window.addEventListener('DOMContentLoaded', () => {
    const hash = window.location.hash;
    showForm('setInformationForm');
    if (hash) {
        const formId = hash.replace('#', ''); // bỏ dấu #
        showForm(formId);
    }
    else{
        showForm('login');
    }
    /*    if (formElement) {
            // Ẩn tất cả form trước
            ['loginForm', 'resetForm', 'forgotForm', 'logoutForm'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.hidden=true;
            });
            // Hiện form có id tương ứng với hash
            formElement.hidden= false;
        }*/
});
//2. Đăng nhập
function login() {
    const lg = document.getElementById('loginForm');
    if(!lg)
        return;

    lg.addEventListener('submit', function(e){
        e.preventDefault();

        const id = document.getElementById("id").value.trim();
        const password = document.getElementById("password").value;

        fetch("http://127.0.0.1:5000/api/auth/login",{
            method: 'POST',
            credentials: "include",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({id: id, password: password})
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                alert(data.message || "Đăng nhập thất bại!");
                return;
            }
            // Lưu thông tin người dùng
            sessionStorage.setItem("userRole", data.user.role);
            sessionStorage.setItem("userId", data.user.id);
            sessionStorage.setItem("userName", data.user.name);
            // Điều hướng theo vai trò
            switch (data.user.role) {
                case "student":
                    window.location.href = "templates/student_html/trangChu.html";
                    break;
                case "teacher":
                    window.location.href = "templates/teacher_html/trangChu.html";
                    break;
                case "admin":
                    window.location.href = "templates/admin_html/dashboard.html";
                    break;
                default:
                    alert("Không xác định vai trò người dùng!");
                    break;
            }
        })
        .catch((err) => {
            console.error("Lỗi đăng nhập:", err);
            alert("Không thể kết nối đến máy chủ!");
        });
    });
}
//3. Đăng xuất 
function Logout() {
    const out = document.getElementById('logoutForm');
    if (!out) return;
    out.addEventListener("submit", function(e){
        e.preventDefault();

        fetch("/api/auth/logout", {method: "POST", credentials: "include"})
        .then(response => {
            if(!response.ok) throw new Error("Logout không thành công");
            return response.json();
        })
        .then(data => {
            alert(data.message || "Đăng xuất thành công");
            window.location.href="../templates/index.html";
        })
        .catch(error => {
            console.error("Lỗi:",error);
            alert("Lỗi khi đăng xuất, thử lại sau.");
        });
    });
}
//4. Đổi mật khẩu
function passReset() {
    const form = document.getElementById('resetForm');
    if(!form){
        return;
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();// Ngan form submit mac dinh

        // lấy giá trị từ các ô input
        const oldP =document.getElementById('oldP').value;
        const newMK=document.getElementById('newP').value;
        const xacnhan = document.getElementById('xacnhan').value;
        
        if(newMK.length < 6){
            alert("Mật khẩu nên có ít nhất 6 ký tự.");
            return;
        }
        if(newMK !== xacnhan){
            alert("Mật khẩu mới và xác nhận không khớp!");
            return;
        }
        // Gửi POST request đến Flask backend
        fetch('/api/auth/set_password',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                password: oldP,
                new_password: newMK
            })
        })
        .then(response => response.json())
        .then(data =>{
            if(data.message){
                alert(data.message); // Đổi mật khẩu thành công
                window.location.href = "index.html"; // Chuyển về trang đăng nhập
            } else if(data.error){
                alert("Lỗi: "+data.error);// Thông báo trả về từ backend
            }
        })
        .catch(error => {
            console.error('Lỗi kết nối:',error);
            alert("Có lỗi khi gửi yêu cầu. Vui lòng thử lại.");
        });
    });
}
//5. Quên mật khẩu
function forgotPass(){
    const forgot = document.getElementById('forgotForm');
    if(!forgot)
        return;
    forgot.addEventListener('submit', function(e){
        e.preventDefault();

        // Lấy giá trị từ các ô input
        const email = document.getElementById('email').value;
        const fnewP = document.getElementById('f-newP').value;
        const fxacnhan = document.getElementById('f-xacnhan').value;

        // Kiểm tra định dạng mật khẩu
        if(fnewP.length<6){
            alert("Mật khẩu nên có ít nhất 6 kí tự.");
            return;
        }
        if(fnewP !== fxacnhan){
            alert("Mật khẩu mới và xác nhận không khớp!");
            return;
        }

        fetch('/forgot_password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                new_password: fnewP
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.message){
                alert(data.message);
                window.location.href = "log_SV.html";
            } else if(data.error){
                alert("Lỗi: " + data.error);
            }
        })
        .catch(error => {
            console.error("Lỗi khi gửi yêu cầu:", error);
            alert("Không thể kết nối tới server.");
        });
    });
}
//6. Lấy thông tin sinh viên
function getProfile(){
    fetch('http://127.0.0.1:5000/api/student/profile', {method: 'get', credentials: 'include'}) //gửi cookie để xác thực
    .then(function(response){
        if(!response.ok){
            return response.json().then(function(err){
                throw new Error(err.message || 'Lỗi tải dữ liệu');
            });
        }
        return response.json();
    })
    .then(function(data){
        document.getElementById('full_name').textContent = data["Họ và tên"] || '';
        document.getElementById('student_id').textContent = data["Mã sinh viên"] || '';
        document.getElementById('gender').textContent = '';
        document.getElementById('date_of_birth').textContent = data["Ngày sinh"] || '';
        document.getElementById('email').textContent = data["Email"] || '';
        document.getElementById('hometown').textContent = '';
        document.getElementById('address').textContent = '';
        document.getElementById('cccd').textContent = '';
        var status = data["Thông tin khóa học"] && data["Thông tin khóa học"]["Trạng thái"];
        document.getElementById('status').textContent = status || '';

        var course = datadata["Thông tin khóa học"] || {};
        document.getElementById('department').textContent = course["Tên khoa"] || '';
        document.getElementById('faculty').textContent = ''; // API chưa có trường này
        document.getElementById('education_level').textContent = ''; // API chưa có trường này
        document.getElementById('entry_year').textContent = course["Năm bắt đầu"] || '';
    })
    .catch(function(error){
        alert('Lỗi khi tải thông tin sinh viên: ' + error.message);
    });

}
//7. Sửa thông tin sinh viên gồm get và put
function setProfile(){
    const apiUrl = 'http://127.0.0.1:5000/api/student/profile';
    const set = document.getElementById('setInformationForm');
    if(!set){
        return;
    }
    
    const nameInput = document.getElementById("name");
    const maSVInput = document.getElementById('maSV');
    const emailInput = document.getElementById('mail');
    const nganhInput = document.getElementById('nganh');
    const phoneInput = document.getElementById('phone');

    // GỌI API GET /profile để hiển thị thông tin hiện tại
    fetch(apiUrl, {method: "GET", credentials: "include"})
    .then(response => {
        if(!response.ok){
            return response.json().then(err => {
                throw new Error(err.message);
            });
        }
        return response.json();
    })
    .then(data => {
        // Đổ dữ liệu từ user_data (giữ nguyên key như backend trả)
        // Nếu backend trả user_data = {...} trực tiếp
        nameInput.value = data["Họ và tên"] || "";
        maSVInput.value = data["Mã sinh viên"] || "";
        emailInput.value = data["Email"] || "";
        phoneInput.value = data["Số điện thoại"] || "";

        // Dữ liệu trong object lồng "Thông tin khóa học"
        if (data["Thông tin khóa học"]) {
            const khoaHoc = data["Thông tin khóa học"];
            nganhInput.value = khoaHoc["Tên khoa"] || "";
        }
    })
    .catch(err => {
        console.error("Lỗi khi tải thông tin:", err);
        alert("Không thể tải thông tin sinh viên: " + err.message);
    })

    // PUT /profile khi dùng nhấn “Lưu”
    set.addEventListener('submit', function(event){
        event.preventDefault();

        const newInfor = {
            email: emailInput.value.trim(),
            phone: phoneInput.value.trim()
        };
        fetch(apiUrl, {
            method: 'put',
            headers: {"Content-Type": "application/json"},
            credentials: "include",
            body: JSON.stringify(newInfor)
        })
        .then(response => response.json())
        .then(data => {
            if(data.error){
                alert(data.message || "Cập nhật thất bại!");
                return;
            }
            alert(data.message || "Cập nhật thành công!");
        })
        .catch(err => {
            console.error("Lỗi khi cập nhật:", err);
            alert("Không thể gửi dữ liệu đến API."+ err.message);
        });
    });
}
//8. Lấy các kỳ đã và đang học
function getTerms(){
    const termSelect = document.getElementById('termSelect');
    if (!termSelect) return; // Chỉ chạy nếu có select trong trang

    fetch('/api/student/terms', { method: 'GET', credentials: 'include' })
    .then(res => res.json())
    .then(data => {
        if (!Array.isArray(data) || data.length === 0){
            termSelect.innerHTML = '<option>Không có kỳ học nào</option>';
            return;
        }
      // Xóa dữ liệu cũ
        termSelect.innerHTML = '';
      // Thêm tùy chọn kỳ học
        data.forEach(term => {
            const opt = document.createElement('option');
            opt.value = term["Mã kỳ học"];
            opt.textContent = `${term["Tên kỳ học"]} (${term["Ngày bắt đầu"]} - ${term["Ngày kết thúc"]})`;
            termSelect.appendChild(opt);
        });

      // Gọi luôn lớp của kỳ đầu tiên (gọi Hàm 9)
        if (data[0]) {
            getEnrollments(data[0]["Mã kỳ học"]);
        }
    })
    .catch(err => {
        console.error("Lỗi khi tải kỳ học:", err);
        alert("Không thể tải danh sách kỳ học: " + err.message);
    });

    // Khi người dùng chọn kỳ khác
    termSelect.addEventListener('change', function () {
        const termId = this.value;
        getEnrollments(termId);
    });
}
//9. Lấy ra các lớp đã đăng ký trong Kỳ học
function getEnrollments(termId) {
    const classList = document.getElementById('classList');
    if (!classList) return;

    fetch(`/api/student/enrollments/${termId}`, { method: 'GET', credentials: 'include' })
    .then(res => res.json())
    .then(data => {
        classList.innerHTML = ''; // Xóa nội dung cũ

        if (!Array.isArray(data) || data.length === 0) {
            classList.innerHTML = '<li>Không có lớp học nào trong kỳ này.</li>';
            return;
        }

        data.forEach(cls => {
            const li = document.createElement('li');
            // Tạo liên kết sang trang chi tiết môn (monA.html)
            const a = document.createElement('a');
            a.href = `monA.html?course_id=${cls["Mã Môn"]}&class_id=${cls["Mã lớp"]}&term_id=${termId}`;
            a.textContent = `${cls["Tên Môn"]} - ${cls["Giảng viên phụ trách"]}`;
            li.appendChild(a);
            classList.appendChild(li);
        });
    })
    .catch(err => {
        console.error("Lỗi khi tải danh sách lớp:", err);
        alert("Không thể tải danh sách lớp: " + err.message);
    });
} 
//12. lấy thông tin các môn đã đăng ký
//13. Lấy thông tin chi tiết về điểm của 1 môn học
// trang monA.html
function loadCourseDetail() {
    // Kiểm tra xem đang ở trang monA.html không
    if (!window.location.pathname.includes("monA.html")) return;

    // Lấy course_id, class_id, term_id từ URL
    const params = new URLSearchParams(window.location.search);
    const courseId = params.get("course_id");
    const classId = params.get("class_id");
    const termId = params.get("term_id");

    if (!courseId || !classId || !termId) {
        alert("Thiếu thông tin môn học trong URL!");
        return;
    }

    // Gọi API lấy điểm của môn học 
    fetch(`/api/student/grade/${courseId}`, { method: 'GET', credentials: 'include' })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.message || "Không thể tải điểm môn học");
            return;
        }

        // Hiện thông tin cơ bản
        document.getElementById('courseName').textContent = data["Tên môn học"] || "";
        document.getElementById('termName').textContent = data["Kỳ học"] || "";

        // Điểm của môn học này
        let gradeHTML = "";
        if (Array.isArray(data["Điểm thành phần"])) {
            gradeHTML += "<ul>";
            data["Điểm thành phần"].forEach(g => {
            gradeHTML += `<li>${g["Tên điểm"]}: ${g["Điểm"]}</li>`;
            });
            gradeHTML += "</ul>";
        }
        gradeHTML += `<strong>Tổng kết:</strong> ${data["Tổng kết"]["Điểm số"]} (${data["Tổng kết"]["Điểm chữ"]})`;
        document.getElementById('grade').innerHTML = gradeHTML;
    })
    .catch(err => {
        console.error("Lỗi khi tải điểm môn:", err);
        alert("Không thể tải điểm: " + err.message);
    });

    // Gọi API lấy chi tiết lớp học trong kỳ
    fetch(`/api/student/enrollments/${termId}`, { method: 'GET', credentials: 'include' })
    .then(res => res.json())
    .then(classes => {
        if (!Array.isArray(classes)) return;

        // Tìm lớp tương ứng
        const cls = classes.find(c => c["Mã lớp"] == classId);
        if (!cls) return;

        // Đổ thông tin vào bảng
        document.getElementById('lecturer').textContent = cls["Giảng viên phụ trách"] || "";
        document.getElementById('room').textContent = cls["Phòng học"] || "";
        document.getElementById('schedule').textContent =
            `${cls["Ngày bắt đầu"]} - ${cls["Ngày kết thúc"]}`;

        // Cập nhật liên kết "Danh sách sinh viên"
        const listLink = document.getElementById('studentListLink');
        listLink.href = `ds_banHoc.html?class_id=${classId}&term_id=${termId}`;

        // Liên kết điểm danh (sẽ thêm khi có API)
        const attendanceLink = document.getElementById('attendanceLink');
        attendanceLink.href = `dienmanh.html?class_id=${classId}&term_id=${termId}`;
    })
    .catch(err => {
        console.error("Lỗi khi tải thông tin lớp:", err);
    });
}
//10. Lấy danh sách sinh viên cùng lớp
function studentList() {
    // Chỉ chạy nếu đang ở trang ds_banHoc.html
    if (!window.location.pathname.includes("ds_banHoc.html")) return;

    const params = new URLSearchParams(window.location.search);
    const classId = params.get("class_id");
    const termId = params.get("term_id");

    if (!classId || !termId) {
        alert("Thiếu thông tin lớp hoặc kỳ học trong URL!");
        return;
    }

    const tbody = document.getElementById("classmate");
    tbody.dataset.class = classId;
    tbody.dataset.term = termId;

    // --- Gọi API lấy danh sách sinh viên ---
    fetch(`/api/student/list-student/${classId}/${termId}`, {method: "GET", credentials: "include"})
    .then(res => res.json())
    .then(data => {
        tbody.innerHTML = "";

        if (!Array.isArray(data) || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5">Không có sinh viên nào trong lớp này.</td></tr>`;
            return;
        }

        data.forEach(st => {
            const row = `
            <tr>
                <td>${st.STT}</td>
                <td>${st["Họ và tên"]}</td>
                <td>${st.id}</td>
                <td>${st.email}</td>
                <td>${st["Ngày sinh"]}</td>
            </tr>
            `;
            tbody.innerHTML += row;
        });
    })
    .catch(err => {
        console.error("Lỗi khi tải danh sách sinh viên:", err);
        alert("Không thể tải danh sách sinh viên: " + err.message);
    });
}
//11. Lấy file execl danh sách sinh viên
function excelList() {
    const tbody = document.getElementById("classmate");
    if (!tbody) return;

    const classId = tbody.dataset.class;
    if (!classId) {
        alert("Không tìm thấy mã lớp.");
        return;
    }

    fetch(`/api/student/list_student/export-excel/${classId}`, {method: "GET",credentials: "include"})
    .then(res => {
        if (!res.ok) throw new Error("Không thể tải file Excel");
        return res.blob(); // chuyển response thành dạng nhị phân (Blob)
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);   // Tạo đường dẫn URL tạm cho file Excel
        const a = document.createElement("a");          // Tạo 1 thẻ <a> ảo (chưa nằm trong DOM).
        a.href = url;                                   // Gán link file vào thẻ <a>
        a.download = `Danh_sach_SV_Lop_${classId}.xlsx`; // Gán tên file khi tải
        a.click();                                      // Giả lập click để trình duyệt tải file
        window.URL.revokeObjectURL(url);                // Giải phóng URL tạm sau khi tải xong
    })
    .catch(err => {
        console.error("Lỗi tải Excel:", err);
        alert("Không thể tải file Excel: " + err.message);
    });
}
function loadGrades() {
    // Chỉ chạy nếu đang ở trang diem.html
    if (!window.location.pathname.includes("diem.html")) return;

    const termSelect = document.getElementById("termSelect");
    const tbody = document.getElementById("gradeTableBody");

    // --- Gọi API lấy danh sách kỳ học ---
    fetch("/api/student/terms", { method: "GET", credentials: "include" })
    .then(res => res.json())
    .then(terms => {
        termSelect.innerHTML = "";

        if (!Array.isArray(terms) || terms.length === 0) {
            termSelect.innerHTML = "<option>Không có kỳ học</option>";
            return;
        }

        // Hiển thị danh sách kỳ học
        terms.forEach(term => {
            const opt = document.createElement("option");
            opt.value = term["Mã kỳ học"];
            opt.textContent = term["Tên kỳ học"];
            termSelect.appendChild(opt);
        });

        // Gọi loadCourses cho kỳ đầu tiên
        loadCourses(termSelect.value);
    });

    //Khi người dùng đổi kỳ học
    termSelect.addEventListener("change", () => {
        const termId = termSelect.value;
        loadCourses(termId);
    });

    //Hàm con: lấy danh sách môn học & điểm
    function loadCourses(termId) {
        fetch(`/api/student/courses/${termId}`, { method: "GET", credentials: "include" })
        .then(res => res.json())
        .then(courses => {
            tbody.innerHTML = "";

            if (!Array.isArray(courses) || courses.length === 0) {
                tbody.innerHTML = "<tr><td colspan='4'>Không có môn học nào trong kỳ này.</td></tr>";
                return;
            }

            // Duyệt từng môn học
            courses.forEach(course => {
            const courseId = course["Mã môn học"];

            // Gọi API lấy điểm của từng môn
            fetch(`/api/student/grade/${courseId}`, { method: "GET", credentials: "include" })
                .then(res => res.json())
                .then(gradeData => {
                    const row = document.createElement("tr");

                    row.innerHTML = `
                        <td>${course["Tên môn học"]}</td>
                        <td>${gradeData["Điểm giữa kỳ"] ?? "-"}</td>
                        <td>${gradeData["Điểm cuối kỳ"] ?? "-"}</td>
                        <td>${gradeData["Tổng kết"]?.["Điểm số"] ?? "-"}</td>
                    `;

                    tbody.appendChild(row);
                })
                .catch(err => console.error("Lỗi tải điểm:", err));
            });
        })
        .catch(err => console.error("Lỗi tải danh sách môn học:", err));
    }
}
//Điểm danh
function attendanceList() {
    // Chỉ chạy khi đang ở trang dienmanh.html
    if (!window.location.pathname.includes("dienmanh.html")) return;

    const params = new URLSearchParams(window.location.search);
    const classId = params.get("class_id");
    const termId = params.get("term_id");

    const tbody = document.getElementById("diemDanh");
    tbody.innerHTML = "";

    if (!classId || !termId) {
        tbody.innerHTML = `<tr><td colspan="3">Thiếu thông tin lớp hoặc kỳ học.</td></tr>`;
        return;
    }

    fetch(`/api/student/attendance/${classId}/${termId}`, {method: "GET", credentials: "include"})
        .then(res => {
            if (!res.ok) throw new Error("Không thể tải dữ liệu điểm danh");
            return res.json();
        })
        .then(data => {
            tbody.innerHTML = "";

            if (!Array.isArray(data) || data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="3">Chưa có dữ liệu điểm danh.</td></tr>`;
                return;
            }

            data.forEach(session => {
                const date = session["Ngày học"] || session["date"] || "-";
                const course = session["Tên môn học"] || session["course"] || "-";
                const status = session["Trạng thái"] || session["status"] || "Không rõ";

                let color = "";
                if (status.toLowerCase().includes("vắng")) color = "style='color:red;'";
                else if (status.toLowerCase().includes("có mặt")) color = "style='color:green;'";
                else if (status.toLowerCase().includes("sáng") || status.toLowerCase().includes("chiều"))
                color = "style='color:blue;'";

                const row = `
                <tr>
                    <td>${date}</td>
                    <td>${course}</td>
                    <td ${color}>${status}</td>
                </tr>
                `;
                tbody.innerHTML += row;
            });
        })
        .catch(err => {
            console.warn("API /attendance chưa có hoặc bị lỗi:", err);
            tbody.innerHTML = `<tr><td colspan="3">Dữ liệu điểm danh chưa khả dụng.</td></tr>`;
        });
}


// Gọi tất cả các hàm 1 lần khi DOM sẵn sàng
document.addEventListener('DOMContentLoaded',function(){
    //Chỉ chạy showForm() nếu đang ở index.html
    if (window.location.pathname.includes("index.html")) {
        showForm();
    }
    passReset();
    login();
    forgotPass();
    Logout();
    getProfile();
    setProfile();
    getTerms();
    loadCourseDetail();

    studentList();
    // Gắn sự kiện nút xuất Excel
    const btn = document.getElementById("excel_out");
    if (btn) btn.addEventListener("click", excelList);

    loadGrades();
    attendanceList();
});