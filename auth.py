from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'name' not in data or 'password' not in data:
        return jsonify({'error': 'Faltan nombre o contraseña'}), 400

    if User.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'El usuario ya existe'}), 409

    user = User(name=data['name'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Usuario creado', 'user_id': user.id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(name=data.get('name')).first()
    if not user or not user.check_password(data.get('password', '')):
        return jsonify({'error': 'Credenciales inválidas'}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({'access_token': access_token}), 200
