from flask import Blueprint, jsonify, request, session, url_for, render_template, redirect
from models import db, User, Post, Comment, Like, Bookmark
from datetime import datetime

social_bp = Blueprint('social', __name__)

def get_current_user_id():
    return session.get('user_id')

@social_bp.route('/api/posts', methods=['GET'])
def get_posts():
    user_id = get_current_user_id()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    result = []
    for post in posts:
        user = User.query.get(post.user_id)
        comments = Comment.query.filter_by(post_id=post.id).all()
        likes = Like.query.filter_by(post_id=post.id).count()
        bookmarks = Bookmark.query.filter_by(post_id=post.id).count()
        is_bookmarked = False
        if user_id:
            is_bookmarked = Bookmark.query.filter_by(user_id=user_id, post_id=post.id).first() is not None
        result.append({
            'id': post.id,
            'username': user.username,
            'timestamp': post.created_at.strftime('%Y-%m-%d %H:%M'),
            'content': post.content,
            'likes': likes,
            'bookmarks': bookmarks,
            'is_bookmarked': is_bookmarked,
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

@social_bp.route('/api/posts/<int:post_id>/bookmark', methods=['POST'])
def bookmark_post(post_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    bookmark = Bookmark.query.filter_by(user_id=user_id, post_id=post_id).first()
    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        return jsonify({'bookmarked': False})
    else:
        new_bm = Bookmark(user_id=user_id, post_id=post_id)
        db.session.add(new_bm)
        db.session.commit()
        return jsonify({'bookmarked': True})

@social_bp.route('/api/users')
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username} for u in users])

@social_bp.route('/collection')
def collection():
    uid = session.get('user_id')
    if not uid:
        return redirect(url_for('auth_bp.login'))
    return render_template('social_collection.html')

@social_bp.route('/api/posts/bookmarked')
def api_bookmarked_posts():
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error':'Unauthorized'}), 401
    bookmarks = Bookmark.query.filter_by(user_id=uid).all()
    posts = [bm.post for bm in bookmarks]
    data = [{

        'id': p.id,
        'username': p.user.username,
        'timestamp': p.created_at.strftime('%Y-%m-%d %H:%M'),
        'content': p.content,
        'likes': len(p.likes),
        'comments': [{'username':c.user.username, 'text':c.content} for c in p.comments],
        'bookmarks': len(p.bookmarks),
        'is_bookmarked': True
        
    } for p in sorted(posts, key=lambda x: x.created_at, reverse=True)]
    return jsonify(data)