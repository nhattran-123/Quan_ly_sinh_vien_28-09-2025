// thử ngày 07/10/2025. Hàm 4?
// Hàm sử lý ẩn/hiện
function showForm(formName){
    // Ẩn tất cả các form
    document.querySelectorAll('.log-box').forEach(form =>{
        form.classList.add('hidden');
    })
    // Hiện form theo tên truyền vào
    const formToShow = document.getElementById(formName + 'Form');
    if(formToShow){
        formToShow.classList.remove('hidden');
    }
}

// Hàm 1: Xử lý form đăng nhập
function login() {
    const lg = document.getElementById('loginForm');
    if(!lg)
        return;

    lg.addEventListener('submit', function(e){
        e.preventDefault();

        const t = document.getElementById("ten").value.trim();
        const mk = document.getElementById("mk").value;

        fetch('/',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: t,
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
                window.location.href = "trangChu.html";
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

// Hàm 2: Xử lý đổi mật khẩu mật khẩu
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
        fetch('/set_password',{
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
                window.location.href = "log_SV.html"; // Chuyển về trang đăng nhập
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

// Hàm 3: xử lý quên mật khẩu
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
// Hàm 4: đăng xuất 
function setupLogout() {
    const out = document.getElementById("logout");
    if (!out) return;

    out.addEventListener("click", function () {
        fetch("/logout", {
            method: "POST",
            credentials: "same-origin", // để gửi cookie session nếu có
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || "Đã đăng xuất.");
            window.location.href = "log_SV.html"; // Chuyển về trang đăng nhập
        })
        .catch(error => {
            console.error("Lỗi khi đăng xuất:", error);
            alert("Không thể kết nối tới server.");
        });
    });
}
// xử lý tính năng liên kết với trang khác
window.addEventListener('DOMContentLoaded', () => {
    const hash = window.location.hash;

    if (hash) {
        const formId = hash.replace('#', ''); // bỏ dấu #
        const formElement = document.getElementById(formId);

        if (formElement) {
            // Ẩn tất cả form trước
            ['loginForm', 'resetForm', 'forgotForm'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.classList.add('hidden');
            });

            // Hiện form có id tương ứng với hash
            formElement.classList.remove('hidden');
        }
    }
});

// Hàm 5: xử lý khi người dùng chọn ảnh
function avatar() {
    const fileInput = document.getElementById('fileInput');
    const previewImg = document.getElementById('preview');

    if (!fileInput || !previewImg) return;

    fileInput.addEventListener('change', function (event) {
        const file = event.target.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function (e) {
                previewImg.src = e.target.result;
            };
            reader.readAsDataURL(file);
        } else {
            alert("Vui lòng chọn một tệp ảnh hợp lệ.");
        }
    });
}

// Gọi tất cả các hàm 1 lần khi DOM sẵn sàng
document.addEventListener('DOMContentLoaded',function(){
    passReset();
    login();
    forgotPass();
    setupLogout();
    if (!window.location.hash) {
        showForm('login'); // Chỉ hiện đăng nhập nếu không có hash
    }
    avatar();
});