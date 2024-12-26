from flask import Flask, request, jsonify
from pymongo import MongoClient
import uuid
from flask import render_template


app = Flask(__name__)


MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["Flask_CRUD"]
users_collection = db["users"]

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/users", methods=["GET"])
def get_users():

    users = list(users_collection.find())
    for user in users:
        user["_id"] = str(user["_id"])  
    return jsonify(users), 200


@app.route("/users/<id>", methods=["GET"])
def get_user(id):
    user = users_collection.find_one({"id": id})
    if user:
        user["_id"] = str(user["_id"])
        return jsonify(user), 200
    return jsonify({"error": "User not found"}), 404


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or not all(k in data for k in ("name", "email", "password")):
        return jsonify({"error": "Invalid data"}), 400
    data["id"] = str(uuid.uuid4())

    user_id = users_collection.insert_one(data).inserted_id
    new_user = users_collection.find_one({"_id": user_id})
    new_user["_id"] = str(new_user["_id"])
    return jsonify(new_user), 201


@app.route("/users/<id>", methods=["PUT"])
def update_user(id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    updated = users_collection.update_one({"id": id}, {"$set": data})
    if updated.matched_count:
        updated_user = users_collection.find_one({"id": id})
        updated_user["_id"] = str(updated_user["_id"])
        return jsonify(updated_user), 200
    return jsonify({"error": "User not found"}), 404


@app.route("/users/<id>", methods=["DELETE"])
def delete_user(id):
    deleted = users_collection.delete_one({"id": id})
    if deleted.deleted_count:
        return jsonify({"message": "User deleted successfully"}), 200
    return jsonify({"error": "User not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
