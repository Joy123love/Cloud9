from flask import Flask, request, jsonify
from model_database import db, User
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allows access from PyQt

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def create_tables():
    with app.app_context():
        db.create_all()

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email, password=password).first()
    if user:
        return jsonify({"message": "Login successful", "username": user.username, "points": user.points})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    users = User.query.order_by(User.points.desc()).all()
    leaderboard = []
    for rank, user in enumerate(users, start=1):
        leaderboard.append({
            'rank': rank,
            'username': user.username,
            'points': user.points
        })
    return jsonify({'leaderboard': leaderboard}), 200

@app.route('/update_points', methods=['POST'])
def update_points():
    data = request.get_json()
    email = data.get('email')
    new_points = data.get('points')

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404


    if new_points > user.points:
        user.points = new_points
        db.session.commit()

    return jsonify({'message': 'Points updated'}), 200

if __name__ == "__main__":
    create_tables()
    app.run(port=5000, debug=True)
