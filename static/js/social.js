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
  
  // Check if the container exists (it may not if we're on a different tab)
  if (!postListContainer) return;
  
  postListContainer.innerHTML = '';
  
  // Sort posts by time (newest first)
  posts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  
  posts.forEach(post => {
    postListContainer.appendChild(createPostElement(post));
  });
  
  // Set up event listeners for the newly created elements
  setupPostEventListeners();
}

// Create post DOM element
function createPostElement(post) {
  const postDiv = document.createElement('div');
  postDiv.className = 'card post-card';
  postDiv.dataset.postId = post.id;
  postDiv.style.marginBottom = '24px';
  
  // User information
  const userInfoDiv = document.createElement('div');
  userInfoDiv.className = 'post-header';
  userInfoDiv.innerHTML = `
    <strong>${post.username}</strong>
    <small style="margin-left: 8px; color: #777;">${post.timestamp}</small>
  `;
  
  // Post content
  const contentDiv = document.createElement('div');
  contentDiv.className = 'post-content';
  contentDiv.textContent = post.content;
  
  // Post image (if any)
  let imageDiv = null;
  if (post.image) {
    imageDiv = document.createElement('div');
    imageDiv.className = 'post-image';
    imageDiv.innerHTML = `<img src="${post.image}" alt="post image" style="width: 100%; border-radius: 10px;" onerror="this.onerror=null; this.src='img/placeholder.jpg'; this.alt='image not available';">`;
  }
  
  // Post action area
  const actionsDiv = document.createElement('div');
  actionsDiv.className = 'post-actions';
  actionsDiv.style.display = 'flex';
  actionsDiv.style.gap = '20px';
  actionsDiv.style.fontSize = '18px';
  
  actionsDiv.innerHTML = `
    <span class="like-button" data-post-id="${post.id}">${post.liked ? '❤️' : '🤍'} ${post.likes}</span>
    <span>💬 ${post.comments.length}</span>
    <span>🔖</span>
  `;
  
  // Comments area
  const commentsDiv = document.createElement('div');
  commentsDiv.className = 'post-comments';
  commentsDiv.style.borderTop = '1px solid #eee';
  commentsDiv.style.paddingTop = '10px';
  
  let commentsHTML = '';
  post.comments.forEach(comment => {
    commentsHTML += `<p><strong>${comment.username}:</strong> ${comment.text}</p>`;
  });
  
  commentsHTML += `<input type="text" placeholder="Add a comment..." class="comment-input" data-post-id="${post.id}">`;
  commentsDiv.innerHTML = commentsHTML;
  
  // Assemble post elements
  postDiv.appendChild(userInfoDiv);
  postDiv.appendChild(contentDiv);
  if (imageDiv) {
    postDiv.appendChild(imageDiv);
  }
  postDiv.appendChild(actionsDiv);
  postDiv.appendChild(commentsDiv);
  
  return postDiv;
}

// Handle post creation
function createNewPost() {
  const contentElement = document.getElementById('new-post-content');
  if (!contentElement) return;
  
  const content = contentElement.value.trim();
  if (!content) {
    alert('Please enter some content for your post.');
    return;
  }
  
  // Read image file (if any)
  const imageFileElement = document.getElementById('new-post-image');
  if (!imageFileElement) return;
  
  const imageFile = imageFileElement.files[0];
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
  contentElement.value = '';
  imageFileElement.value = '';
  
  alert('Post successfully created!');
}

// Handle like functionality
function handleLike(postId) {
  const posts = JSON.parse(localStorage.getItem('posts')) || [];
  const postIndex = posts.findIndex(p => p.id === parseInt(postId));
  
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
  const postIndex = posts.findIndex(p => p.id === parseInt(postId));
  
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

// Set up event listeners for post interactions
function setupPostEventListeners() {
  // Like button click
  const likeButtons = document.querySelectorAll('.like-button');
  likeButtons.forEach(button => {
    button.addEventListener('click', function() {
      const postId = this.dataset.postId;
      handleLike(postId);
    });
  });
  
  // Comment input
  const commentInputs = document.querySelectorAll('.comment-input');
  commentInputs.forEach(input => {
    input.addEventListener('keypress', function(event) {
      if (event.key === 'Enter') {
        const postId = this.dataset.postId;
        addComment(postId, this.value);
        this.value = '';
      }
    });
  });
}

// Initialize event listeners when the document is ready
document.addEventListener('DOMContentLoaded', () => {
  // Only initialize if we're on the social tab
  if (document.getElementById('tab-social').classList.contains('active')) {
    loadPosts();
  }
  
  // Add event listener to the post button
  const postButton = document.querySelector('.post-button');
  if (postButton) {
    postButton.addEventListener('click', createNewPost);
  }
});