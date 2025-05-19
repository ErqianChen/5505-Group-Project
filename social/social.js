// Fetch CSRF token for AJAX POST requests
let csrfToken = '';
fetch('/api/csrf-token')
    .then(res => res.json())
    .then(data => {
        csrfToken = data.csrf_token;
    })
    .catch(err => console.error('Failed to fetch CSRF token:', err));

// Render posts to #post-list
function renderPosts(posts) {
    const postList = document.getElementById('post-list');
    postList.innerHTML = '';
    posts.forEach(post => {
        const postCard = document.createElement('div');
        postCard.className = 'card post-card';
        postCard.style.marginBottom = '24px';
        postCard.innerHTML = `
            <div class="post-header">
                <strong>${post.username}</strong>
                <small style="margin-left: 8px; color: #777;">${post.timestamp}</small>
            </div>
            <div class="post-content">${post.content}</div>
            <div class="post-actions" style="display: flex; gap: 20px; font-size: 18px;">
                <span class="action-button" onclick="likePost(${post.id})">❤️ ${post.likes}</span>
                <span>💬 ${post.comments.length}</span>
                <span class="action-button" onclick="bookmarkPost(${post.id})">${post.is_bookmarked ? '🔖' : '📑'} ${post.bookmarks}</span>
            </div>
            <div class="post-comments" style="border-top: 1px solid #eee; padding-top: 10px;">
                ${post.comments.map(c => `<p><strong>${c.username}:</strong> ${c.text}</p>`).join('')}
                <input type="text" class="comment-input" placeholder="Add a comment..." onkeydown="if(event.key==='Enter'){submitComment(${post.id}, this.value); this.value='';}">
            </div>
        `;
        postList.appendChild(postCard);
    });
}

// Load posts from backend
function loadPosts() {
    fetch('/api/posts')
        .then(res => {
            if (!res.ok) throw new Error('Failed to load posts');
            return res.json();
        })
        .then(posts => {
            renderPosts(posts);
        })
        .catch(err => {
            console.error('Error loading posts:', err);
            alert('Failed to load posts. Please try again later.');
        });
}

// Submit a new post
function submitPost(content) {
    fetch('/api/posts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ content })
    })
    .then(res => {
        if (!res.ok) throw new Error('Failed to create post');
        return res.json();
    })
    .then(data => {
        if (data.success) {
            loadPosts();
        } else {
            throw new Error(data.error || 'Failed to create post');
        }
    })
    .catch(err => {
        console.error('Error creating post:', err);
        alert('Failed to create post. Please try again later.');
    });
}

// Submit a comment
function submitComment(postId, text) {
    if (!text.trim()) {
        alert('Comment cannot be empty');
        return;
    }

    fetch(`/api/posts/${postId}/comments`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ text })
    })
    .then(res => {
        if (!res.ok) throw new Error('Failed to submit comment');
        return res.json();
    })
    .then(data => {
        if (data.success) {
            loadPosts();
        } else {
            throw new Error(data.error || 'Failed to submit comment');
        }
    })
    .catch(err => {
        console.error('Error submitting comment:', err);
        alert('Failed to submit comment. Please try again later.');
    });
}

// Like or unlike a post
function likePost(postId) {
    fetch(`/api/posts/${postId}/like`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(res => {
        if (!res.ok) throw new Error('Failed to like/unlike post');
        return res.json();
    })
    .then(data => {
        if (data.success) {
            loadPosts();
        } else {
            throw new Error(data.error || 'Failed to like/unlike post');
        }
    })
    .catch(err => {
        console.error('Error liking/unliking post:', err);
        alert('Failed to update like. Please try again later.');
    });
}

// Bind post button event
window.addEventListener('DOMContentLoaded', function() {
    const btn = document.querySelector('.post-button');
    if (btn) {
        btn.onclick = function() {
            const content = document.getElementById('new-post-content').value.trim();
            if (!content) return alert('Content cannot be empty!');
            submitPost(content);
            document.getElementById('new-post-content').value = '';
        };
    }
    loadPosts();
});

// Bookmark or unbookmark a post
function bookmarkPost(postId) {
    fetch(`/api/posts/${postId}/bookmark`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(res => {
        if (!res.ok) throw new Error('Failed to bookmark/unbookmark post');
        return res.json();
    })
    .then(data => {
        if (data.success) {
            loadPosts();
        } else {
            throw new Error(data.error || 'Failed to bookmark/unbookmark post');
        }
    })
    .catch(err => {
        console.error('Error bookmarking/unbookmarking post:', err);
        alert('Failed to update bookmark. Please try again later.');
    });
}