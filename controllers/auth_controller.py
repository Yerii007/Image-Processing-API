from flask import request, jsonify
from services.auth_service import AuthService
from schemas.user_schema import UserRegistrationSchema, UserLoginSchema

class AuthController:
    def __init__(self, db):
        self.db = db
        self.auth_service = AuthService(db.session)
        self.registration_schema = UserRegistrationSchema()
        self.login_schema = UserLoginSchema()
    
    def register(self):
        try:
            data = request.get_json()
            errors = self.registration_schema.validate(data)
            if errors:
                return jsonify({"error": "Validation failed", "details": errors}), 400
            
            name = data.get("name")
            password = data.get("password")
            
            user, access_token = self.auth_service.register_user(name, password)
            
            if not user:
                return jsonify({"error": "User already exists"}), 409
            
            return jsonify({
                "message": "User created",
                "access_token": access_token,
                "user": user.to_dict()
            }), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def login(self):
        try:
            data = request.get_json()
            errors = self.login_schema.validate(data)
            if errors:
                return jsonify({"error": "Validation failed", "details": errors}), 400
            
            name = data["name"]
            password = data["password"]
            
            user, access_token = self.auth_service.authenticate_user(name, password)
            
            if not user:
                return jsonify({"error": "Invalid credentials"}), 401
            
            return jsonify({
                "message": "Login successful",
                "access_token": access_token,
                "user": user.to_dict()
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500