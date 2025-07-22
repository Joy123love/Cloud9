import random
from flask import Flask, Response, request, jsonify
from model_database import CodingChallenges, CodingChallengesChecks, CodingChallengesStatements, db, User
from flask_cors import CORS

from ..server import app, db, update_users_points, get_username

@app.route('/coding/completed', methods=['POST'])
def completed_coding_challenge():
    data = request.get_json()
    challenge_id = data.get('id')
    challenge = CodingChallenges.query.filter_by(id=challenge_id).first();
    
    if not challenge:
        return jsonify({'message': 'Challenge not found'}), 404

    return update_users_points(challenge.points, data.get('user_id'), data.get('email'))

@app.route('/coding/list', methods=['GET'])
def get_coding_challenges():
    challenges = CodingChallenges.query.all();
    
    challenges_json = [];
    
    for challenge in challenges:
        challenges_json.append({"id" : challenge.id, "user_id" : challenge.user_id, "username" : get_username(id=challenge.user_id), "points" : challenge.points})
    
    return jsonify({'challenges': challenges_json}), 200

@app.route("/coding", methods=["POST"])
def create_coding_challenge():
    data = request.get_json()
    name = data.get("name")
    user_id = data.get("user_id")
    description = data.get("description")
    starting = data.get("starting")
    statements_json = data.get("statements")
    checks_json = data.get("checks")

    if CodingChallenges.query.filter_by(name=name, user_id=user_id).count() > 0:
        return jsonify({"error": "User has already created this challenge"}), 409

    db.session.add(CodingChallenges(name=name, user_id=user_id, description=description, starting=starting, points=0))
    db.session.commit()

    challenge = CodingChallenges.query.filter_by(user_id=user_id, name=name).first();

    if not challenge:
        return jsonify({'message': 'Unable to add challenge.'}), 404
    
    statements = [];
    for statement in statements_json:
        statements.append(CodingChallengesStatements(challenge_id=challenge.id, keyword=statement.keyword, amount=statement.amount));
    
    checks = [];
    for check in checks_json:
        checks.append(CodingChallengesChecks(challenge_id=challenge.id, check=check));

    db.session.add_all(statements);
    db.session.add_all(checks);
    db.session.commit();

    return jsonify({"message": "Challenge successfully created"}), 201

@app.route('/coding', methods=['GET'])
def get_coding_challenge():
    data = request.get_json()
    id = data.get('id')
    challenge = CodingChallenges.query.filter_by(id=id).first();
    statements = CodingChallengesStatements.query.filter_by(challenge_id=id).all()
    checks = CodingChallengesChecks.query.filter_by(challenge_id=id).all()
    
    if not challenge:
        return jsonify({'message': 'Challenge not found'}), 404
    
    statements_json = [];
    for statement in statements:
        statements_json.append(jsonify({"keyword" : statement.keyword, "amount" : statement.amount}))
    
    checks_json = [];
    for check in checks:
        checks_json.append(check.check)


    return jsonify({'name': challenge.name, "user_id" : challenge.user_id, "username" : get_username(id=id), "description" : challenge.user_id, "starting" : challenge.starting, "statements" : statements_json, "checks" : checks_json}), 200
