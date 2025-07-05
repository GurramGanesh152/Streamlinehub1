from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import jwt
import os
from werkzeug.utils import secure_filename
from functools import wraps

# Set up the app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///video.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Secret key for JWT
SECRET_KEY = "your_secret_key"

# Ensure the uploads directory exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Define the video model
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    video_path = db.Column(db.String, nullable=False)
    caption = db.Column(db.String, nullable=True)

@app.before_first_request
def create_tables():
    db.create_all()

def token_required(f):
    """Decorator to check for valid JWT token."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({"message": "Token is missing!"}), 403
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 403
        return f(current_user_id, *args, **kwargs)
    return decorated_function

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/feed', methods=['GET'])
@token_required
def feed(current_user_id):
    videos = Video.query.all()
    all_videos = [{"id": video.id, "user_id": video.user_id, "video_path": video.video_path, "caption": video.caption} for video in videos[::-1]]
    return render_template('feed.html', videos=all_videos, user_id=current_user_id)

@app.route('/videos', methods=['POST'])
@token_required
def create_video(current_user_id):
    data = request.form
    caption = data.get('caption')
    video = request.files.get('video')

    if not video:
        return jsonify({"message": "video is required!"}), 400

    # Create a secure filename to prevent directory traversal attacks
    video_filename = secure_filename(video.filename)
    save_path = os.path.join(UPLOAD_FOLDER, video_filename)

    try:
        video.save(save_path)  # Save the video to the uploads directory
    except Exception as e:
        return jsonify({"message": f"Error saving video: {str(e)}"}), 500

    new_video = Video(user_id=current_user_id, video_path=video_filename, caption=caption)
    db.session.add(new_video)
    db.session.commit()

    return jsonify({"message": "video uploaded successfully!"}), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
