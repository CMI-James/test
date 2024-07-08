from flask import Blueprint, request, jsonify
from .models import db, User, Organisation, UserOrganisation
from .utils import hash_password, verify_password, create_access_token
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

bp = Blueprint('auth', __name__)

@bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    errors = validate_user_data(data)
    if errors:
        return jsonify({"errors": errors}), 422

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"errors": [{"field": "email", "message": "Email already exists"}]}), 422

    user = User(
        firstName=data['firstName'],
        lastName=data['lastName'],
        email=data['email'],
        password=hash_password(data['password']),
        phone=data.get('phone')
    )
    db.session.add(user)
    db.session.commit()

    org = Organisation(
        name=f"{user.firstName}'s Organisation"
    )
    db.session.add(org)
    db.session.commit()

    user_org = UserOrganisation(user_id=user.userId, org_id=org.orgId)
    db.session.add(user_org)
    db.session.commit()

    access_token = create_access_token(identity=user.userId)
    return jsonify({"status": "success", "message": "Registration successful", "data": {"accessToken": access_token, "user": {"userId": str(user.userId), "firstName": user.firstName, "lastName": user.lastName, "email": user.email, "phone": user.phone}}}), 201

@bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and verify_password(data['password'], user.password):
        access_token = create_access_token(identity=user.userId)
        return jsonify({"status": "success", "message": "Login successful", "data": {"accessToken": access_token, "user": {"userId": str(user.userId), "firstName": user.firstName, "lastName": user.lastName, "email": user.email, "phone": user.phone}}}), 200

    return jsonify({"status": "Bad request", "message": "Authentication failed", "statusCode": 401}), 401

@bp.route('/api/users/<uuid:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"status": "Bad request", "message": "User not found", "statusCode": 404}), 404

    return jsonify({"status": "success", "message": "User retrieved successfully", "data": {"userId": str(user.userId), "firstName": user.firstName, "lastName": user.lastName, "email": user.email, "phone": user.phone}}), 200

@bp.route('/api/organisations', methods=['GET'])
@jwt_required()
def get_organisations():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    orgs = user.organisations

    return jsonify({"status": "success", "message": "Organisations retrieved successfully", "data": {"organisations": [{"orgId": str(org.orgId), "name": org.name, "description": org.description} for org in orgs]}}), 200

@bp.route('/api/organisations/<uuid:orgId>', methods=['GET'])
@jwt_required()
def get_organisation(orgId):
    org = Organisation.query.get(orgId)
    if not org:
        return jsonify({"status": "Bad request", "message": "Organisation not found", "statusCode": 404}), 404

    return jsonify({"status": "success", "message": "Organisation retrieved successfully", "data": {"orgId": str(org.orgId), "name": org.name, "description": org.description}}), 200

@bp.route('/api/organisations', methods=['POST'])
@jwt_required()
def create_organisation():
    data = request.get_json()
    if not data.get('name'):
        return jsonify({"errors": [{"field": "name", "message": "Name is required"}]}), 422

    org = Organisation(
        name=data['name'],
        description=data.get('description')
    )
    db.session.add(org)
    db.session.commit()

    current_user_id = get_jwt_identity()
    user_org = UserOrganisation(user_id=current_user_id, org_id=org.orgId)
    db.session.add(user_org)
    db.session.commit()

    return jsonify({"status": "success", "message": "Organisation created successfully", "data": {"orgId": str(org.orgId), "name": org.name, "description": org.description}}), 201

@bp.route('/api/organisations/<uuid:orgId>/users', methods=['POST'])
@jwt_required()
def add_user_to_organisation(orgId):
    data = request.get_json()
    user = User.query.get(data['userId'])
    if not user:
        return jsonify({"errors": [{"field": "userId", "message": "User not found"}]}), 422

    user_org = UserOrganisation(user_id=user.userId, org_id=orgId)
    db.session.add(user_org)
    db.session.commit()

    return jsonify({"status": "success", "message": "User added to organisation successfully"}), 200
