/* Các hàm:
1. Xử lý ẩn/hiện đối với các form đăng nhập, đăng xuất, đổi mk
2. Đăng nhập - login
3. Đăng xuất - logout
4. Đổi mật khẩu - set password
5. Quên mật khẩu (chưa có API)
6. Lấy thông tin sinh viên - profile GET
7. Sửa thông tin sinh viên - profile POST
8. Lấy các kỳ đã và đang học - term GET
9. Lấy ra các lớp đã đăng ký trong Kỳ học - enrollments/<term_id> (GET)
10. Lấy danh sách sinh viên cùng lớp 
11. Lấy file execl danh sách sinh viên
12. lấy thông tin các môn đã đăng ký
13. Lấy thông tin chi tiết về điểm của 1 môn học
*/
//1. Hàm sử lý ẩn/hiện
function showForm(formName){
    
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

        const ten = document.getElementById("id").value.trim();
        const mk = document.getElementById("password").value;

        fetch('/api/auth/login',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: ten,
                password: mk
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.message){
                alert(data.message);// Đăng nhập thành công
                // Có thể lưu thông tin người dùng nếu cần:
                // localStorage.setItem("user_id", data.user);
                // localStorage.setItem("full_name", data.full_name);
                // localStorage.setItem("role", data.role);
                window.location.href = "../templates/student_html/trangChu.html";
            } else if (data.error) {
                alert("Lỗi: " + data.error);
            }
        })
        .catch(error => {
            console.error("Lỗi khi gửi yêu cầu:", error);
            alert("Không thể kết nối tới server.");
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
        document.getElementById('ful_name').textContent = data["Họ và tên"] || '';
        document.getElementById('student_id').textContent = data["Mã sinh viên"] || '';
        document.getElementById('gender').textContent = '';
        document.getElementById('date_of_birth').textContent = data["Ngày sinh"] || '';
        document.getElementById('email').textContent = data["Email"] || '';
        document.getElementById('Hometown').textContent = '';
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
//7. Sửa thông tin sinh viên
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

    // GỌI API GET /profile 
    fetch(apiUrl, {method: "get", credentials: "include"})
    .then(response => response.json())
    .then(data => {
        if(data.error){
            alert(data.message || "Không thể lấy thông tin sinh viên");
            return;
        }

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
        console.error("Lỗi khi gọi GET /profile:", err);
        alert("Không thể kết nối API.");
    });

    // PUT /profile khi nhấn “Lưu”
    set.addEventListener('submit', function(event){
        event.preventDefault();

        const newInfor = {
            email: emailInput.value.trim(),
            phone: phoneInput.value.trim()
        };
        fetch(apiUrl, {
            method: 'put',
            headers: {
                "Content-Type": "application/json"
            },
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
            alert("Không thể gửi dữ liệu đến API.");
        });
    });
}
//8. Lấy các kỳ đã và đang học
//9. Lấy ra các lớp đã đăng ký trong Kỳ học
//10. Lấy danh sách sinh viên cùng lớp 
//11. Lấy file execl danh sách sinh viên
//12. lấy thông tin các môn đã đăng ký
//13. Lấy thông tin chi tiết về điểm của 1 môn học

// Gọi tất cả các hàm 1 lần khi DOM sẵn sàng
document.addEventListener('DOMContentLoaded',function(){
    showForm();
    passReset();
    login();
    forgotPass();
    Logout();

    getProfile();
    setProfile();
});
