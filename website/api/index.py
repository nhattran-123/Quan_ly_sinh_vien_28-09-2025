from flask import Blueprint,request,jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .. import db
from ..models import User

"""
Đăng nhập : http://127.0.0.1:5000/api/auth/login
Đăng xuất : http://127.0.0.1:5000/api/auth/logout
Lấy thông tin curent_user: curl http://127.0.0.1:5000/api/auth/current_user
Đổi mật khẩu :http://127.0.0.1:5000/api/auth/set_password
"""
# tao blueprint cho module auth
auth_bp=Blueprint('auth',__name__)

# ham load user cho flask-login
from flask_login import LoginManager
login_manager=LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@auth_bp.route('/login',methods=['POST'])
def login():
    data = request.get_json(silent=True)  or request.form
    user_id = data.get("id")
    password = data.get("password")


    if not user_id or not password:
        return jsonify({"error": " ID và mật khẩu không được để trống"}), 400
    user =User.query.get(user_id)

    if not user or user.check_password(password)==False:
        return jsonify({"error": "ID hoặc mật khẩu không đúng" }), 401
    login_user(user)
    return jsonify({
        "messager": "Đăng nhập thành công",
        "user": user.id,
        "full_name": user.full_name,
        "role": user.role
    }), 200
@auth_bp.route('/logout',methods=["POST","GET"])
@login_required
def logout():
    """API đăng xuất"""
    logout_user()
    return jsonify({"message": "đăng xuất thành công"}),200
@auth_bp.route('/current_user',methods=["GET"])
@login_required
def get_current_user():
    if current_user.is_authenticated:
        return jsonify({
            "id": current_user.id,
            "fullname": current_user.full_name,
            "role":current_user.role
            }), 200
    return jsonify({"error": "chưa đăng nhập"}), 401
@auth_bp.route('/set_password',methods=["POST"])
@login_required
def set_password():
    data = request.get_json(silent=True) or request.form
    password=data.get("password")
    new_password=data.get("new_password")

    if not password or not new_password:
        return jsonify({"error":"Mật khẩu cũ và mật khẩu mới không được để trống"}),400
    if not current_user.check_password(password):
        return jsonify({"error":"Mật khẩu cũ không đúng"}),401
    current_user.set_password(new_password)
    db.session.commit()
    return jsonify({"messager":"Đổi mật khẩu thành công"}),200