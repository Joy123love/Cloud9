import random
from flask import Flask, Response, request, jsonify
from model_database import CodingChallenges, CodingChallengesChecks, CodingChallengesStatements, db, User
from flask_cors import CORS
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Validate fields
    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    hashed_password = generate_password_hash(password)
    user = User(username=username, email=email, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return jsonify({
            "message": "Login successful",
            "username": user.username,
            "id": user.id,
            "points": user.points
        })
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        limit = int(request.args.get('limit', 50))
    except ValueError:
        limit = 50

    users = User.query.order_by(User.points.desc()).limit(limit).all()
    leaderboard = []
    for rank, user in enumerate(users, start=1):
        leaderboard.append({
            'rank': rank,
            'username': user.username,
            'points': user.points
        })
    return jsonify({'leaderboard': leaderboard}), 200

@app.route('/points', methods=['POST'])
def update_points():
    data = request.get_json()
    user_id = data.get('id')
    email = data.get('email')
    new_points = data.get('points')

    if new_points is None:
        return jsonify({'error': 'Points field is required'}), 400

    return update_users_points(new_points, user_id, email)

def get_username(id=None, email=None) -> Optional[str]:
    if not id and not email:
        return None
    user = User.query.filter_by(email=email).first() if email else User.query.filter_by(id=id).first()
    return user.username if user else None

def update_users_points(new_points: int, id=None, email=None) -> tuple[Response, int]:
    if not id and not email:
        return jsonify({'error': 'User ID or email required'}), 400

    user = User.query.filter_by(email=email).first() if email else User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if new_points > user.points:
        user.points = new_points
        db.session.commit()

    return jsonify({'message': 'Points updated'}), 200

if __name__ == "__main__":
    print("Starting Flask server on http://localhost:5000")
    app.run(port=5000, debug=True)
