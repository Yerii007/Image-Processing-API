from flask_jwt_extended import create_access_token
from models.users import User
from sqlalchemy import select

class AuthService:
    def __init__(self, db_session):
        self.db_session = db_session
    
    def register_user(self, name, password):
        # Check if user already exists
        existing_user = self.db_session.execute(
            select(User).where(User.name == name)
        ).scalar()
        
        if existing_user:
            return None, "User already exists"
        
        # Create new user
        new_user = User(name=name)
        new_user.set_password(password)
        self.db_session.add(new_user)
        self.db_session.commit()
        
        # Generate access token
        access_token = create_access_token(identity=str(new_user.id))
        return new_user, access_token
    
    def authenticate_user(self, name, password):
        user = self.db_session.execute(
            select(User).where(User.name == name)
        ).scalar()
        
        if user and user.check_password(password):
            access_token = create_access_token(identity=str(user.id))
            return user, access_token
        
        return None, None