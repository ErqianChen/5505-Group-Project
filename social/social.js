// Initialize local storage data
if (!localStorage.getItem('posts')) {
  const initialPosts = [
    {
      id: 1,
      username: 'Username123',
      timestamp: '2025-05-06 14:30',
      content: 'Just finished a killer workout session! 🏋️‍♀️💦 Feeling energized and ready to take on the day. Today\'s focus was on strength training and cardio intervals.',
      image: 'img/lift.jpg',
      likes: 15,
      comments: [
        { username: 'Alice', text: 'Amazing progress!' },
        { username: 'Bob', text: 'Go beast mode!! 💪' }
      ],
      liked: false
    },
    {
      id: 2,
      username: 'EmilyFit',
      timestamp: '2025-05-06 10:15',
      content: 'Tried morning yoga 🧘‍♀️— feel calm and centered. Started my day with a 30-minute flow focusing on flexibility and mindfulness. Highly recommend for stress relief!',
      image: '',
      likes: 7,
      comments: [],
      liked: false
    },
    {
      id: 3,
      username: 'StrongMike',
      timestamp: '2025-05-05 18:45',
      content: 'Pushed my limits on bench press today! 💪🔥 Hit a new personal record of 225lbs for 5 reps. The journey of small improvements is what makes fitness so rewarding.',
      image: 'img/bench.jpg',
      likes: 20,
      comments: [
        { username: 'Tom', text: 'Beast mode!!' },
        { username: 'Jess', text: 'Respect 👏' },
        { username: 'Ella', text: '🔥🔥🔥' }
      ],
      liked: false
    }
  ];
  localStorage.setItem('posts', JSON.stringify(initialPosts));
}

// Current user (static example)
const currentUser = {
  username: 'CurrentUser',
  // More user information would be available in a real application
};

// Load all posts
function loadPosts() {
  const posts = JSON.parse(localStorage.getItem('posts')) || [];
  const postListContainer = document.getElementById('post-list');
  postListContainer.innerHTML = '';
  
  // Sort posts by time (newest first)
  posts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  
  posts.forEach(post => {
    postListContainer.appendChild(createPostElement(post));
  });
}

// Create post DOM element
function createPostElement(post) {
  const postDiv = document.createElement('div');
  postDiv.className = 'post-card';
  postDiv.dataset.postId = post.id;
  
  // User information
  const userInfoDiv = document.createElement('div');
  userInfoDiv.className = 'user-info';
  userInfoDiv.innerHTML = `
    <span class="username">${post.username}</span>
    <span class="user-title">${post.timestamp}</span>
  `;
  
  // Post content
  const contentDiv = document.createElement('div');
  contentDiv.className = 'post-content';
  contentDiv.textContent = post.content;
  
  // Read more button
  const readMoreSpan = document.createElement('span');
  readMoreSpan.className = 'read-more';
  readMoreSpan.textContent = 'Read more';
  
  // Post image (if any)
  let imageDiv = '';
  if (post.image) {
    imageDiv = document.createElement('div');
    imageDiv.className = 'post-image';
    imageDiv.innerHTML = `<img src="${post.image}" alt="post image" onerror="this.onerror=null; this.src='img/placeholder.jpg'; this.alt='image not available';">`;
  }
  
  // Post action area
  const actionsDiv = document.createElement('div');
  actionsDiv.className = 'post-actions';
  
  const likeButtonClass = post.liked ? 'action-button upvote' : 'action-button';
  actionsDiv.innerHTML = `
    <div class="like-button ${likeButtonClass}" data-post-id="${post.id}">
      <span>${post.liked ? '❤️' : '🤍'}</span>
      <span class="action-count">${post.likes}</span>
    </div>
    <div class="action-button">
      <span>💬</span>
      <span class="action-count">${post.comments.length}</span>
    </div>
    <div class="action-button">
      <span>🔖</span>
    </div>
    <div class="action-button">
      <span>...</span>
    </div>
  `;
  
  // Comments area
  const commentsDiv = document.createElement('div');
  commentsDiv.className = 'post-comments';
  
  let commentsHTML = '';
  post.comments.forEach(comment => {
    commentsHTML += `
      <div class="comment">
        <span class="comment-username">${comment.username}:</span>
        <span class="comment-text">${comment.text}</span>
      </div>
    `;
  });
  
  commentsHTML += `
    <div class="comment-form">
      <input type="text" placeholder="Add a comment..." class="comment-input" data-post-id="${post.id}">
    </div>
  `;
  
  commentsDiv.innerHTML = commentsHTML;
  
  // Assemble post elements
  postDiv.appendChild(userInfoDiv);
  postDiv.appendChild(contentDiv);
  postDiv.appendChild(readMoreSpan);
  if (imageDiv) {
    postDiv.appendChild(imageDiv);
  }
  postDiv.appendChild(actionsDiv);
  postDiv.appendChild(commentsDiv);
  
  return postDiv;
}

// Handle post creation
function createNewPost() {
  const content = document.getElementById('new-post-content').value.trim();
  if (!content) {
    alert('Please enter some content for your post.');
    return;
  }
  
  // Read image file (if any)
  const imageFile = document.getElementById('new-post-image').files[0];
  let imagePath = '';
  
  // In a real application, image should be uploaded to server
  if (imageFile) {
    // In a real application, this would handle the image upload
    // For demo purposes, we assume it's uploaded and URL is returned
    imagePath = 'img/placeholder.jpg'; // This is just an example path
  }
  
  // Get current time
  const now = new Date();
  const timeString = now.toISOString().slice(0, 10) + ' ' + 
                     now.getHours().toString().padStart(2, '0') + ':' + 
                     now.getMinutes().toString().padStart(2, '0');
  
  // Get current posts and add new post
  const posts = JSON.parse(localStorage.getItem('posts')) || [];
  const newPostId = posts.length > 0 ? Math.max(...posts.map(p => p.id)) + 1 : 1;
  
  const newPost = {
    id: newPostId,
    username: currentUser.username,
    timestamp: timeString,
    content: content,
    image: imagePath,
    likes: 0,
    comments: [],
    liked: false
  };
  
  posts.push(newPost);
  localStorage.setItem('posts', JSON.stringify(posts));
  
  // Refresh post list and clear form
  loadPosts();
  document.getElementById('new-post-content').value = '';
  document.getElementById('new-post-image').value = '';
  
  alert('Post successfully created!');
}

// Handle like functionality
function handleLike(postId) {
  const posts = JSON.parse(localStorage.getItem('posts')) || [];
  const postIndex = posts.findIndex(p => p.id === postId);
  
  if (postIndex !== -1) {
    // Toggle like status
    const post = posts[postIndex];
    post.liked = !post.liked;
    
    // Update like count
    if (post.liked) {
      post.likes++;
    } else {
      post.likes--;
    }
    
    localStorage.setItem('posts', JSON.stringify(posts));
    loadPosts(); // Refresh display
  }
}

// Handle comment functionality
function addComment(postId, commentText) {
  if (!commentText.trim()) return;
  
  const posts = JSON.parse(localStorage.getItem('posts')) || [];
  const postIndex = posts.findIndex(p => p.id === postId);
  
  if (postIndex !== -1) {
    const newComment = {
      username: currentUser.username,
      text: commentText.trim()
    };
    
    posts[postIndex].comments.push(newComment);
    localStorage.setItem('posts', JSON.stringify(posts));
    loadPosts(); // Refresh display
  }
}

// Toggle read more functionality
function toggleReadMore(event) {
  const content = event.target.previousElementSibling;
  if (content.style.webkitLineClamp === 'unset') {
    content.style.webkitLineClamp = '3';
    event.target.textContent = 'Read more';
  } else {
    content.style.webkitLineClamp = 'unset';
    event.target.textContent = 'Show less';
  }
}

// Set up event listeners
document.addEventListener('DOMContentLoaded', () => {
  // Load posts
  loadPosts();
  
  // Post button listener
  document.querySelector('.post-button').addEventListener('click', createNewPost);
  
  // Event delegation
  document.getElementById('post-list').addEventListener('click', event => {
    // Like button
    if (event.target.closest('.like-button')) {
      const likeButton = event.target.closest('.like-button');
      const postId = parseInt(likeButton.dataset.postId);
      handleLike(postId);
    }
    
    // Read more button
    if (event.target.classList.contains('read-more')) {
      toggleReadMore(event);
    }
  });
  
  // Comment input
  document.getElementById('post-list').addEventListener('keypress', event => {
    if (event.key === 'Enter' && event.target.classList.contains('comment-input')) {
      const postId = parseInt(event.target.dataset.postId);
      addComment(postId, event.target.value);
      event.target.value = '';
    }
  });
}); 