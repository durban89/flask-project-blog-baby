#! _*_ coding: utf-8 _*_
#

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    jsonify
)

from werkzeug.security import check_password_hash, generate_password_hash
from baby.db import get_db


bp = Blueprint('api_auth', __name__, url_prefix='/api')


@bp.route('auth', methods=['POST'])
def auth():
    json_data = request.get_json()
    email = json_data['email']
    password = json_data['password']
    return jsonify(token=generate_password_hash(password))
