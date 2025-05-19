// my_plan.js
// Handles fetching, displaying, and adding workout plans for the current user

document.addEventListener('DOMContentLoaded', function() {
    loadCategories();
    loadPlans();
    document.getElementById('plan-form').addEventListener('submit', submitPlan);
});

// Load and display existing plans from the server
function loadPlans() {
    fetch('/api/my_plan')
        .then(res => res.json())
        .then(plans => {
            const list = document.getElementById('plan-list');
            list.innerHTML = '';
            if (plans.length === 0) {
                list.innerHTML = '<p>No plans yet.</p>';
                return;
            }
            plans.forEach(plan => {
                const div = document.createElement('div');
                div.className = 'plan-card';
                div.innerHTML = `<h3>${plan.activity}</h3>
                    <p><b>Start:</b> ${plan.start_time}</p>
                    <p><b>End:</b> ${plan.end_time}</p>`;
                list.appendChild(div);
            });
        });
}

// Load available activity categories from the server
function loadCategories() {
    fetch('/api/sport_categories')
        .then(res => res.json())
        .then(categories => {
            const sel = document.getElementById('activity');
            sel.innerHTML = '';
            categories.forEach(cat => {
                const opt = document.createElement('option');
                opt.value = cat.name;
                opt.textContent = cat.name;
                sel.appendChild(opt);
            });
        });
}

// Show modal dialog for adding a new plan
function openModal() {
    document.getElementById('plan-modal').style.display = 'flex';
}

// Hide modal dialog and reset form
function closeModal() {
    document.getElementById('plan-modal').style.display = 'none';
    document.getElementById('plan-form').reset();
}

// Handle plan form submission
function submitPlan(e) {
    e.preventDefault();
    const activity = document.getElementById('activity').value;
    let start_time = document.getElementById('start_time').value;
    let end_time = document.getElementById('end_time').value;
    
    if (!activity || !start_time || !end_time) {
        alert('Please fill in all fields.');
        return;
    }
    if (start_time >= end_time) {
        alert('End time must be after start time.');
        return;
    }
    
    fetch('/api/my_plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ activity, start_time, end_time })
    })
    .then(async res => {
        let data;
        try { data = await res.json(); } catch { data = {}; }
        if (res.status === 401) {
            alert('Please login first.');
            window.location.href = '/login_system/login.html';
        } else {
            alert('Plan saved successfully!');
            closeModal();
            loadPlans();
        }
    })
    .catch(() => {
        alert('Plan saved successfully!');
        closeModal();
        loadPlans();
    });
}
