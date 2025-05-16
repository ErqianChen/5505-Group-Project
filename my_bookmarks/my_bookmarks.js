// my_bookmarks.js
// 只显示当前用户的bookmarks

document.addEventListener('DOMContentLoaded', function() {
    loadBookmarkedPosts();
});

function loadBookmarkedPosts() {
    fetch('/api/posts/bookmarked')
        .then(res => res.json())
        .then(posts => {
            if (posts.error) {
                document.getElementById('post-list').innerHTML = '<p>请先登录。</p>';
                return;
            }
            renderPosts(posts);
        });
}

// 复用social.js的renderPosts函数，如果未引入可复制一份
function renderPosts(posts) {
    const postList = document.getElementById('post-list');
    postList.innerHTML = '';
    if (!posts.length) {
        postList.innerHTML = '<p>暂无收藏。</p>';
        return;
    }
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
                <span>❤️ ${post.likes}</span>
                <span>💬 ${post.comments.length}</span>
                <span>🔖 ${post.bookmarks}</span>
            </div>
            <div class="post-comments" style="border-top: 1px solid #eee; padding-top: 10px;">
                ${post.comments.map(c => `<p><strong>${c.username}:</strong> ${c.text}</p>`).join('')}
            </div>
        `;
        postList.appendChild(postCard);
    });
}
