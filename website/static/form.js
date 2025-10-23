/* Các hàm:
1. Xử lý ẩn/hiện đối với các form đăng nhập, đăng xuất, đổi mk
2. Đăng nhập - login
3. Đăng xuất - logout
4. Đổi mật khẩu - set password
5. Quên mật khẩu (chưa có API)
*/
//1. Hàm sử lý ẩn/hiện
function showForm(formName){
    // Ẩn tất cả các form - ở trang index.html nào
    if(window.location.pathname.endsWith('index.html')){
        if(!formName) return; // Nếu không có formName thì bỏ qua
        document.querySelectorAll("form").forEach(form => form.hidden =true);
        // Hiện form theo tên truyền vào
        const formToShow = document.getElementById(formName + 'Form');
        if(formToShow){
            formToShow.hidden=false;
        }
    }
}
// Xử lý tính năng liên kết với trang khác
window.addEventListener('DOMContentLoaded', () => {
    const hash = window.location.hash;

    if (hash) {
        const formId = hash.replace('#', ''); // bỏ dấu #
        const formElement = document.getElementById(formId);

        if (formElement) {
            // Ẩn tất cả form trước
            ['loginForm', 'resetForm', 'forgotForm', 'logoutForm'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.hidden=true;
            });
            // Hiện form có id tương ứng với hash
            formElement.hidden= false;
        }
    }
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
//3. Đăng xuất 
function setupLogout() {
    const out = document.getElementById('logoutForm');
    if (!out) return;
    out.addEventListener("submit", function(e){
        e.preventDefault();

        fetch("/logout", {method: "POST"})
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            window.location.href="index.html";
        })
        .catch(error => {
            console.error("Lỗi:",error);
        })
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

// Gọi tất cả các hàm 1 lần khi DOM sẵn sàng
document.addEventListener('DOMContentLoaded',function(){
    passReset();
    login();
    forgotPass();
    setupLogout();

    if (!window.location.hash) {
        showForm('login'); // Chỉ hiện đăng nhập nếu không có hash
    }
});