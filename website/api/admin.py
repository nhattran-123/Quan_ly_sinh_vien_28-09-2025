from flask import Blueprint, jsonify, request
from flask_login import fresh_login_required,current_user
from .. import db
from ..models import User
from collections import Counter
from .. import login_manager

admin_bp=Blueprint('admin',__name__)
"""
Lấy thông tin admin :http://127.0.0.1:5000/api/admin/userinfor
"""
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
@admin_bp.route('userinfor',methods=["GET"])
@fresh_login_required
def userinfor():
    if current_user.role!='admin':
        return jsonify({
            "error":"Không thành công",
            "mesgager":"Bạn không phải là admin"

        }), 403
    user_data={
        "id":current_user.id,
        "email":current_user.email,
        "role":current_user.role,
        "full name":current_user.full_name,
    }
    return jsonify(user_data), 200