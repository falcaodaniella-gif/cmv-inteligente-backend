from flask import Blueprint, request, jsonify
from ..main import db
from ..models.user import User

user_bp = Blueprint(\'user_bp\', __name__)

@user_bp.route(\'/\', methods=[\'POST\
])
def create_user():
    data = request.get_json()
    new_user = User(username=data[\'username\
'], email=data[\'email\
'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({\'message\': \'User created successfully!\'}), 201

@user_bp.route(\'/\', methods=[\'GET\
])
def get_users():
    users = User.query.all()
    output = []
    for user in users:
        output.append({\'id\': user.id, \'username\': user.username, \'email\': user.email})
    return jsonify(output)
