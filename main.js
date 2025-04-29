function navigateTo(page) {
    let content = document.getElementById('main-content');
    
    if (page === 'home') {
        content.innerHTML = '<h1>Home Page</h1>';
    } else if (page === 'game') {
        content.innerHTML = '<h1>Game Page</h1>';
    } else if (page === 'social') {
        content.innerHTML = '<h1>Social Page</h1>';
    } else if (page === 'my') {
        content.innerHTML = `
            <div class="profile-header">
                <img src="your_avatar_url.png" alt="Avatar">
                <div class="username">Username</div>
                <div class="coins">coins = 66</div>
            </div>

            <div class="profile-body">
                <div class="profile-item">My Information <span>></span></div>
                <div class="profile-item">My plan <span>></span></div>
                <div class="profile-item">My collection <span>></span></div>
                <div class="profile-item">Browsing history <span>></span></div>
            </div>
        `;
    }
}