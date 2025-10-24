/* Các hàm:
1. Xử lý ẩn/hiện đối với các form đăng nhập, đăng xuất, đổi mk
2. Đăng nhập - login (ĐÃ SỬA LỖI KẾT NỐI API)
3. Đăng xuất - logout
4. Đổi mật khẩu - set password
5. Quên mật khẩu (chưa có API) - BỎ QUA
6. Lấy thông tin sinh viên - trang chủ
7. Sửa thông tin sinh viên - newInfor
8. Lấy các kỳ đã và đang học - term GET
9. Lấy ra các lớp đã đăng ký trong Kỳ học - lớp tín chỉ
10. Lấy danh sách sinh viên cùng lớp - lớp tín chỉ/ds_banHoc
11. Lấy file execl danh sách sinh viên
12. lấy thông tin các môn đã đăng ký (Trong Hàm loadCourseDetail)
13. Lấy thông tin chi tiết về điểm của 1 môn học (Trong Hàm loadCourseDetail)
14. Load chi tiết môn học (monA.html)
15. Load bảng điểm theo kỳ (diem.html)
16. Load điểm danh (diemdanh.html)
*/

//1. Hàm sử lý ẩn/hiện
function showForm(formName){
    // Nếu không phải ở trang index.html thì bỏ qua các form login, forgot,...
    if (!window.location.pathname.includes("index.html") && ['login', 'forgot', 'reset', 'logout'].includes(formName)) {
        return;
    }
     // Nếu không phải ở trang index.html hoặc trang có form setInformationForm thì bỏ qua form đó
    if (!window.location.pathname.includes("index.html") && !document.getElementById('setInformationForm') && formName === 'setInformationForm') {
       return;
    }

    if(!formName){
        // Mặc định hiển thị login nếu ở index.html
         if (window.location.pathname.includes("index.html")) {
            formName = 'login';
         } else {
             return; // Không làm gì nếu không ở index và không có formName
         }
    }
    // Ẩn tất cả các form trên trang hiện tại
    document.querySelectorAll("form").forEach(form => form.hidden =true);

    // Hiện form theo tên truyền vào nếu form đó tồn tại
    const formToShow = document.getElementById(formName + 'Form');
    if(formToShow){
        formToShow.hidden=false;
    }
}

// Xử lý hash (#) trên URL khi tải trang (chủ yếu cho index.html)
window.addEventListener('DOMContentLoaded', () => {
    const hash = window.location.hash;
    if (window.location.pathname.includes("index.html")) {
        if (hash) {
            const formId = hash.replace('#', ''); // bỏ dấu #
            showForm(formId);
        } else {
            showForm('login'); // Mặc định hiển thị form login
        }
    }
    // Gọi các hàm khởi tạo khác nếu cần (ví dụ, gọi hàm load dữ liệu cho các trang khác)
    // Ví dụ: getProfile(); setProfile(); getTerms(); loadCourseDetail(); studentList(); loadGrades(); attendanceList();
});

// ==========================================================
// 2. Đăng nhập (PHIÊN BẢN ĐÃ SỬA LỖI KẾT NỐI API)
// ==========================================================
function login() {
    const lg = document.getElementById('loginForm');
    if(!lg) return; // Chỉ chạy nếu có form login

    lg.addEventListener('submit', function(e){
        e.preventDefault(); // Ngăn form submit theo cách truyền thống

        const id = document.getElementById("id").value.trim();
        const password = document.getElementById("password").value;

        // Gọi API backend
        fetch("http://127.0.0.1:5000/api/auth/login",{
            method: 'POST',
            credentials: "include", // Quan trọng để gửi/nhận cookie session
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({id: id, password: password}) // Dữ liệu gửi đi
        })
        .then(response => {
            // Kiểm tra xem backend có trả về lỗi không (vd: 401 Unauthorized)
            if (!response.ok) {
                // Nếu có lỗi, đọc thông báo lỗi từ JSON backend trả về
                return response.json().then(errData => {
                    throw new Error(errData.error || `Lỗi ${response.status}`);
                });
            }
            // Nếu không lỗi (status 200 OK), đọc dữ liệu thành công
            return response.json();
        })
        .then(data => {
            // Backend trả về JSON thành công, lấy thông tin user
            const userRole = data["role"]; // Lấy từ key "role" backend trả về
            const userId = data["id"];
            const userName = data["Họ và Tên"]; // Lấy từ key "Họ và Tên"

            // Lưu thông tin vào sessionStorage để dùng ở trang khác
            sessionStorage.setItem("userRole", userRole);
            sessionStorage.setItem("userId", userId);
            sessionStorage.setItem("userName", userName);

            // Chuyển hướng dựa trên vai trò
            switch (userRole) { // Dùng biến userRole
                case "student":
                    window.location.href = "student_html/trangChu.html"; // Chuyển đến trang chủ sinh viên
                    break;
                case "lecturer": // Đảm bảo khớp với giá trị backend trả về
                    // *** CHÚ Ý: Đổi đường dẫn này nếu thư mục của giảng viên khác ***
                    window.location.href = "lecturer/trangChu.html";
                    break;
                case "admin":
                     // *** CHÚ Ý: Đổi đường dẫn này nếu thư mục của admin khác ***
                    window.location.href = "admin/dashboard.html";
                    break;
                default:
                    // Vai trò không xác định
                    alert("Vai trò người dùng không xác định!");
                    break;
            }
        })
        .catch((err) => {
            // Bắt lỗi (lỗi mạng hoặc lỗi từ backend đã throw ở trên)
            console.error("Lỗi đăng nhập:", err);
            alert(err.message || "Không thể kết nối đến máy chủ!"); // Hiển thị lỗi cho người dùng
        });
    });
}

// ==========================================================
// 3. Đăng xuất
// ==========================================================
function Logout() {
    const out = document.getElementById('logoutForm');
    // Tìm nút/link đăng xuất trong menu (nếu có, dùng chung cho các trang)
    const logoutLinks = document.querySelectorAll('a[href="#logout"], a[onclick*="logoutForm"]');

    function handleLogout(e) {
        e.preventDefault(); // Ngăn link/form hoạt động mặc định
        if (!confirm("Bạn chắc chắn muốn đăng xuất?")) return; // Hỏi xác nhận

        fetch("/api/auth/logout", {method: "POST", credentials: "include"})
        .then(response => {
            if(!response.ok) throw new Error("Logout không thành công");
            return response.json();
        })
        .then(data => {
            alert(data.message || "Đăng xuất thành công");
            sessionStorage.clear(); // Xóa session storage khi đăng xuất
            // Điều hướng về trang đăng nhập (điều chỉnh đường dẫn nếu cần)
             window.location.href = window.location.pathname.includes('/templates/') ? '../index.html' : 'index.html';
        })
        .catch(error => {
            console.error("Lỗi:",error);
            alert("Lỗi khi đăng xuất, thử lại sau.");
        });
    }

    // Gắn sự kiện cho form (nếu có)
    if (out) {
        out.addEventListener("submit", handleLogout);
    }
    // Gắn sự kiện cho các link đăng xuất trong menu
    logoutLinks.forEach(link => {
        link.addEventListener("click", handleLogout);
         // Thay đổi href để tránh reload trang khi chưa xử lý xong
         link.href = "#";
    });
}


// ==========================================================
// 4. Đổi mật khẩu
// ==========================================================
function passReset() {
    const form = document.getElementById('resetForm');
    if(!form) return; // Chỉ chạy nếu có form reset

    form.addEventListener('submit', function(e) {
        e.preventDefault();

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

        fetch('/api/auth/set_password',{ // URL tương đối hoạt động nếu HTML và API cùng domain/port
            method: 'POST',
            credentials: "include", // Cần gửi cookie để xác thực người dùng
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ password: oldP, new_password: newMK })
        })
        .then(response => response.json().then(data => ({ ok: response.ok, data }))) // Trả về cả status và data
        .then(({ ok, data }) =>{
            if (ok) { // Status 2xx
                alert(data.message); // Đổi mật khẩu thành công
                // Nếu đang ở trang index.html thì quay lại form login
                if (window.location.pathname.includes("index.html")) {
                    showForm('login');
                } else {
                    // Nếu ở trang khác, có thể thông báo thành công và giữ nguyên trang
                     alert("Đổi mật khẩu thành công!");
                }
                form.reset(); // Xóa các trường input
            } else { // Status 4xx, 5xx
                alert("Lỗi: "+ (data.error || "Không rõ lỗi"));// Thông báo lỗi từ backend
            }
        })
        .catch(error => {
            console.error('Lỗi kết nối:',error);
            alert("Có lỗi khi gửi yêu cầu. Vui lòng thử lại.");
        });
    });
}

// ==========================================================
// 5. Quên mật khẩu (Chưa có API Backend) - Giữ nguyên
// ==========================================================
function forgotPass(){
    const forgot = document.getElementById('forgotForm');
    if(!forgot) return;

    forgot.addEventListener('submit', function(e){
        e.preventDefault();
        const email = document.getElementById('email').value;
        const fnewP = document.getElementById('f-newP').value;
        const fxacnhan = document.getElementById('f-xacnhan').value;

        if(fnewP.length<6){
            alert("Mật khẩu nên có ít nhất 6 kí tự.");
            return;
        }
        if(fnewP !== fxacnhan){
            alert("Mật khẩu mới và xác nhận không khớp!");
            return;
        }
        alert("Chức năng Quên mật khẩu chưa được cài đặt phía backend!");
        // Tạm thời comment out fetch vì chưa có API
        /*
        fetch('/forgot_password', { // Thay bằng URL API đúng khi có
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ email: email, new_password: fnewP })
        })
        .then(response => response.json())
        .then(data => {
            if(data.message){
                alert(data.message);
                showForm('login');
            } else if(data.error){
                alert("Lỗi: " + data.error);
            }
        })
        .catch(error => {
            console.error("Lỗi khi gửi yêu cầu:", error);
            alert("Không thể kết nối tới server.");
        });
        */
    });
}

// ==========================================================
// CÁC HÀM KHÁC (getProfile, setProfile,...) GIỮ NGUYÊN NHƯ FILE GỐC CỦA BẠN
// Đảm bảo chúng được gọi đúng chỗ trong DOMContentLoaded nếu cần
// ==========================================================

// Ví dụ giữ lại hàm getProfile (bạn cần điều chỉnh các ID element nếu cần)
function getProfile(){
    if (!window.location.pathname.includes("trangChu.html") || !document.getElementById('student_id')) return;
    // ... (code getProfile giữ nguyên) ...
}
// Ví dụ giữ lại hàm setProfile (bạn cần điều chỉnh các ID element nếu cần)
function setProfile(){
     const form = document.getElementById('setInformationForm');
     if(!form) return;
    // ... (code setProfile giữ nguyên) ...
}

// ... (Giữ lại các hàm khác: getTermsAndEnrollments, studentList, excelList, loadCourseDetail, loadGrades, attendanceList) ...
// NHỚ RẰNG: Các hàm này sẽ chỉ hoạt động khi bạn ở đúng trang HTML chứa các element mà chúng cần (ví dụ: getProfile chỉ chạy đúng trên trangChu.html)


// ==========================================================
// GỌI CÁC HÀM KHỞI TẠO KHI TRANG TẢI XONG
// ==========================================================
document.addEventListener('DOMContentLoaded', function(){
    // Các hàm cho trang index.html
    showForm(); // Tự động xác định form dựa trên hash hoặc mặc định là login
    passReset(); // Gắn event cho form đổi mật khẩu (nếu có)
    login();     // Gắn event cho form đăng nhập (nếu có)
    forgotPass();// Gắn event cho form quên mật khẩu (nếu có)
    Logout();    // Gắn event cho form/link đăng xuất (trên mọi trang)

    // Các hàm cho các trang student_html (ví dụ)
    // Các hàm này sẽ tự kiểm tra xem có đúng trang hay không trước khi chạy
    // getProfile();
    // setProfile();
    // getTermsAndEnrollments();
    // loadCourseDetail();
    // studentList();
    // loadGrades();
    // attendanceList();

    // Bạn có thể bỏ comment các hàm trên nếu các trang HTML tương ứng đã sẵn sàng
});