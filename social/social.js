// Fetch CSRF token for AJAX POST requests
let csrfToken = '';
fetch('/api/csrf-token').then(res => res.json()).then(data => {
    csrfToken = data.csrf_token;
});

// Load posts from backend
function loadPosts() {
    fetch('/api/posts')
        .then(res => res.json())
        .then(posts => {
            // Render posts
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
    }).then(res => res.json()).then(data => {
        if (data.success) loadPosts();
    });
}

// Submit a comment
function submitComment(postId, text) {
    fetch(`/api/posts/${postId}/comments`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ text })
    }).then(res => res.json()).then(data => {
        if (data.success) loadPosts();
    });
}

// Like or unlike a post
function likePost(postId) {
    fetch(`/api/posts/${postId}/like`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        }
    }).then(res => res.json()).then(data => {
        loadPosts();
    });
}