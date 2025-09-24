from flask import jsonify
from sqlalchemy import select

class HealthController:
    def __init__(self, db):
        self.db = db
    
    def health_check(self):
        try:
            self.db.session.execute(select(1))
            return jsonify({"status": "healthy", "db": "connected"}), 200
        except Exception as e:
            return jsonify({"status": "unhealthy", "error": str(e)}), 500