from flask import Blueprint, request, jsonify, session, make_response
from flask_login import login_user, logout_user, login_required, current_user
from .. import db
from ..models import User
from .. import login_manager

"""
Đăng nhập : POST http://127.0.0.1:5000/api/auth/login
Đăng xuất : GET/POST http://127.0.0.1:5000/api/auth/logout
Lấy thông tin current_user: GET http://127.0.0.1:5000/api/auth/current_user
Đổi mật khẩu : POST http://127.0.0.1:5000/api/auth/set_password
"""

# Tạo blueprint cho module auth
auth_bp = Blueprint('auth', __name__)

# # Khai báo login_manager
# from flask_login import LoginManager
# login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# ------------------- LOGIN -------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or request.form
    user_id = data.get("id")
    password = data.get("password")

    if not user_id or not password:
        return jsonify({"error": "ID và mật khẩu không được để trống"}), 400

    user = User.query.get(user_id)
    if not user or not user.check_password(password):
        return jsonify({"error": "ID hoặc mật khẩu không đúng"}), 401

    # Đăng nhập và tạo session
    login_user(user, remember=True)  # remember=True để lưu cookie lâu dài
    session['user_id'] = user.id     # lưu user_id vào session

    resp = make_response(jsonify({
        "message": "Đăng nhập thành công",
        "user": user.id,
        "full_name": user.full_name,
        "role": user.role
    }), 200)

    # Đặt cookie (tùy chỉnh thêm, ví dụ 1h)
    resp.set_cookie("user_id", user.id, max_age=3600, httponly=True, samesite='Lax')

    return resp


# ------------------- LOGOUT -------------------
@auth_bp.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
    """API đăng xuất"""
    logout_user()
    session.pop("user_id", None)

    resp = make_response(jsonify({"message": "Đăng xuất thành công"}), 200)
    resp.delete_cookie("user_id")
    return resp


# ------------------- CURRENT USER -------------------
@auth_bp.route('/current_user', methods=["GET"])
@login_required
def get_current_user():
    if current_user.is_authenticated:
        return jsonify({
            "id": current_user.id,
            "fullname": current_user.full_name,
            "role": current_user.role
        }), 200
    return jsonify({"error": "Chưa đăng nhập"}), 401


# ------------------- SET PASSWORD -------------------
@auth_bp.route('/set_password', methods=["POST"])
@login_required
def set_password():
    data = request.get_json(silent=True) or request.form
    password = data.get("password")
    new_password = data.get("new_password")

    if not password or not new_password:
        return jsonify({"error": "Mật khẩu cũ và mật khẩu mới không được để trống"}), 400

    if not current_user.check_password(password):
        return jsonify({"error": "Mật khẩu cũ không đúng"}), 401

    current_user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Đổi mật khẩu thành công"}), 200
