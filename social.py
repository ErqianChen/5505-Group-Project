from flask import Blueprint, jsonify, request, session
from models import db, User, Post, Comment, Like
from datetime import datetime

social_bp = Blueprint('social', __name__)

def get_current_user_id():
    return session.get('user_id')

@social_bp.route('/api/posts', methods=['GET'])
def get_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    result = []
    for post in posts:
        user = User.query.get(post.user_id)
        comments = Comment.query.filter_by(post_id=post.id).all()
        likes = Like.query.filter_by(post_id=post.id).count()
        result.append({
            'id': post.id,
            'username': user.username,
            'timestamp': post.created_at.strftime('%Y-%m-%d %H:%M'),
            'content': post.content,
            'likes': likes,
            'comments': [
                {'username': User.query.get(c.user_id).username, 'text': c.content}
                for c in comments
            ]
        })
    return jsonify(result)

@social_bp.route('/api/posts', methods=['POST'])
def create_post():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.get_json()
    content = data.get('content')
    if not content:
        return jsonify({'error': 'Content required'}), 400
    post = Post(user_id=user_id, content=content, created_at=datetime.now())
    db.session.add(post)
    db.session.commit()
    return jsonify({'success': True})

@social_bp.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({'error': 'Empty comment'}), 400
    comment = Comment(user_id=user_id, post_id=post_id, content=text)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'success': True})

@social_bp.route('/api/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'liked': False})
    else:
        new_like = Like(user_id=user_id, post_id=post_id)
        db.session.add(new_like)
        db.session.commit()
        return jsonify({'liked': True})