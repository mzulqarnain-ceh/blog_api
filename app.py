from flask import Flask, jsonify, request
from models import init_db, get_db_connection
from auth import hash_password, verify_password, generate_token, verify_token, token_required
# app initialize
app=Flask(__name__)
# Routes
# home route
@app.route("/")
def home():
    return jsonify({"message":"Blog API is running......"})
# Authentication routes
# Signup route
@app.route("/signup",methods=["POST"])
def signup():
    data=request.get_json()
    if not data or "username" not in data or "email" not in data or "password" not in data:
        return jsonify({"error":"every feild must be filled"}),400
    conn=get_db_connection()
    user=conn.execute("SELECT * FROM users WHERE username=? OR email=?",(data["username"],data["email"],)).fetchone()
    if user:
        conn.close()
        return jsonify({"error":"username or email already exists"}),400
    hash=hash_password(data["password"])
    conn.execute("INSERT INTO users (username,email,password_hash) VALUES(?,?,?)",(data["username"],data["email"],hash,))
    conn.commit()
    conn.close()
    return jsonify({"message":"user created successfully"}),201
# Login route
@app.route("/login",methods=["POST"])
def login():
    data=request.get_json()
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error":"username and password are required"}),400
    conn=get_db_connection()
    user=conn.execute("SELECT * FROM users WHERE username=?",(data["username"],)).fetchone()
    if user is None:
        conn.close()
        return jsonify({"error":"no user found"}),404
    password=verify_password(data["password"],user["password_hash"])
    if password is False:
        conn.close()
        return jsonify({"error":"Invalid credentials"}),401
    token=generate_token(user["id"])
    conn.close()
    return jsonify({"message":"login successful","token": token}),200
# Posts routes
# create post route  -protected
@app.route("/posts",methods=["POST"])
@token_required
def create_post(user_id):
    pass
# get all posts route - public
@app.route("/posts",methods=["GET"])
def get_all_posts():
    pass
# get single post route - public
@app.route("/posts/<id>",methods=["GET"])
def get_posts_id(id):
    pass
# update post route - protected, owner only
@app.route("/posts/<id>",methods=["PUT"])
@token_required
def upload_post(user_id,id):
    pass
# delete post route - protected, owner only
@app.route("/posts/<id>",methods=["DELETE"])
@token_required
def delete_post(user_id,id):
    pass
# Comments routes
# post comments - protected
@app.route("/posts/<id>/comments",methods=["POST"])
@token_required
def make_comment(user_id,id):
    pass
# view comments - public
@app.route("/posts/<id>/comments",methods=["GET"])
def get_comments(id):
    pass
# Entry point
if __name__=="__main__":
    init_db()
    app.run(debug=True)