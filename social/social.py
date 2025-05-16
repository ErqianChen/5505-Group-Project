from flask import Blueprint, jsonify, request, session
from models import db, Post, Comment, Like, Bookmark, User
from datetime import datetime

social_bp = Blueprint('social', __name__)

@social_bp.route('/api/posts', methods=['GET'])
def get_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    current_user_id = session.get('user_id')
    
    result = []
    for post in posts:
        post_data = {
            'id': post.id,
            'username': post.user.username,
            'content': post.content,
            'timestamp': post.created_at.strftime('%Y-%m-%d %H:%M'),
            'likes': len(post.likes),
            'comments': [{
                'username': comment.user.username,
                'text': comment.content
            } for comment in post.comments],
            'bookmarks': len(post.bookmarks),
            'is_liked': any(like.user_id == current_user_id for like in post.likes),
            'is_bookmarked': any(bookmark.user_id == current_user_id for bookmark in post.bookmarks)
        }
        result.append(post_data)
    return jsonify(result)

@social_bp.route('/api/posts', methods=['POST'])
def create_post():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    content = data.get('content')
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    post = Post(user_id=user_id, content=content)
    db.session.add(post)
    db.session.commit()
    return jsonify({'success': True})

@social_bp.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({'error': 'Comment text is required'}), 400
    
    comment = Comment(user_id=user_id, post_id=post_id, content=text)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'success': True})

@social_bp.route('/api/posts/<int:post_id>/like', methods=['POST'])
def toggle_like(post_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    if like:
        db.session.delete(like)
    else:
        like = Like(user_id=user_id, post_id=post_id)
        db.session.add(like)
    db.session.commit()
    return jsonify({'success': True})

@social_bp.route('/api/posts/<int:post_id>/bookmark', methods=['POST'])
def toggle_bookmark(post_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    bookmark = Bookmark.query.filter_by(user_id=user_id, post_id=post_id).first()
    if bookmark:
        db.session.delete(bookmark)
    else:
        bookmark = Bookmark(user_id=user_id, post_id=post_id)
        db.session.add(bookmark)
    db.session.commit()
    return jsonify({'success': True})

@social_bp.route('/api/posts/bookmarked')
def get_bookmarked_posts():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    bookmarks = Bookmark.query.filter_by(user_id=user_id).all()
    posts = [bm.post for bm in bookmarks]
    result = []
    for post in posts:
        post_data = {
            'id': post.id,
            'username': post.user.username,
            'content': post.content,
            'timestamp': post.created_at.strftime('%Y-%m-%d %H:%M'),
            'likes': len(post.likes),
            'comments': [{
                'username': comment.user.username,
                'text': comment.content
            } for comment in post.comments],
            'bookmarks': len(post.bookmarks),
            'is_liked': any(like.user_id == user_id for like in post.likes),
            'is_bookmarked': True
        }
        result.append(post_data)
    return jsonify(result)