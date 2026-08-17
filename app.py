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
    data=request.get_json()
    if "title" not in data:
        return jsonify({"error":"title is required"}),400
    conn=get_db_connection()
    cursor=conn.execute("INSERT INTO posts (title,content,user_id) VALUES(?,?,?)",(data["title"],data["content"],user_id,))
    conn.commit()
    get_post_id=cursor.lastrowid
    conn.close()
    return jsonify({"message":"post created successfully","post_id":get_post_id}),201
# get all posts route - public
@app.route("/posts",methods=["GET"])
def get_all_posts():
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM posts ORDER BY created_at DESC").fetchall()
    conn.close()
    posts_list = [dict(row) for row in posts]
    return jsonify({"posts": posts_list}), 200
# get specific/single post route - public
@app.route("/posts/<id>",methods=["GET"])
def get_posts_id(id):
    conn=get_db_connection()
    post=conn.execute("SELECT * FROM posts WHERE id=?",(id,)).fetchone()
    if post is None:
        conn.close()
        return jsonify({"error":"post not found"}),404
    conn.close()
    return jsonify({"post":dict(post)}),200
# update post route - protected, owner only
@app.route("/posts/<id>",methods=["PUT"])
@token_required
def upload_post(user_id,id):
    conn=get_db_connection()
    post=conn.execute("SELECT * FROM posts WHERE id=?",(id,)).fetchone()
    if post is None:
        conn.close()
        return jsonify({"error":"post not found"}),404
    if post["user_id"] != user_id:
        conn.close()
        return jsonify({"error":"you are not allowed to edit this post"}),403
    data=request.get_json()
    if not data or "title" not in data:
        conn.close()
        return jsonify({"error":"title must be required"}),400
    conn.execute("UPDATE posts SET title=?, content=? WHERE id=?",(data["title"],data.get("content"),id,))
    conn.commit()
    conn.close()
    return jsonify({"message":"post updated successfully"}),200
# delete post route - protected, owner only
@app.route("/posts/<id>",methods=["DELETE"])
@token_required
def delete_post(user_id,id):
    conn=get_db_connection()
    post=conn.execute("SELECT * FROM posts WHERE id=?",(id,)).fetchone()
    if post is None:
        conn.close()
        return jsonify({"error":"post not found"}),404
    if post["user_id"] != user_id:
        conn.close()
        return jsonify({"error":"you are not allowed to delete this post"}),403
    conn.execute("DELETE FROM posts WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return jsonify({"message":"post deleted successfully"}),200
# Comments routes
# post comments - protected
@app.route("/posts/<id>/comments",methods=["POST"])
@token_required
def make_comment(user_id,id):
    conn=get_db_connection()
    post=conn.execute("SELECT * FROM posts WHERE id=?",(id,)).fetchone()
    if post is None:
        conn.close()
        return jsonify({"error":"post not found"}),404
    data=request.get_json()
    if not data or "comment_text" not in data or data["comment_text"]=="":
        conn.close()
        return jsonify({"error":"comment text is required"}),400
    conn.execute("INSERT INTO comments (post_id, user_id, comment_text) VALUES(?,?,?)",(id,user_id,data["comment_text"],))
    conn.commit()
    conn.close()
    return jsonify({"message":"comment added successfully"}),201
# view comments - public
@app.route("/posts/<id>/comments",methods=["GET"])
def get_comments(id):
    conn=get_db_connection()
    post=conn.execute("SELECT * FROM posts WHERE id=?",(id,)).fetchone()
    if post is None:
        conn.close()
        return jsonify({"error":"post not found"}),404
    comments=conn.execute("SELECT * FROM comments WHERE post_id=? ORDER BY created_at DESC",(id,)).fetchall()
    comments_list=[dict(row) for row in comments]
    conn.close()
    return jsonify({"comments":comments_list}),200
# Entry point
if __name__=="__main__":
    init_db()
    app.run(debug=True)