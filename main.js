$.getJSON('/api/csrf-token').done(function(res) {
  $.ajaxSetup({
    beforeSend: function(xhr) {
      xhr.setRequestHeader('X-CSRFToken', res.csrf_token);
    }
  });
});
// main.js: handle tab switching, chart initialization, and data loading with user selection
let lineChart, pieChart, radarChart;

$(document).ready(function() {
    // Initialize charts once
    initCharts();

    // Populate user dropdown for viewing records of any user
    $.getJSON('/api/users', function(users) {
        const $sel = $('#user-select').empty();
        users.forEach(u => {
            $sel.append(`<option value="${u.id}">${u.username}</option>`);
        });
        // After user list is ready, load records if on Record tab
        if ($('#tab-record').hasClass('active')) {
            loadRecord();
        }
    });

    // When time range changes, reload record data
    $('#record-range-select').on('change', loadRecord);
    // When user selection changes, reload record data
    $('#user-select').on('change', loadRecord);

    // Navigation tab click handler
    $('.nav-item').on('click', function() {
        const tab = $(this).text().trim().toLowerCase();
        switchTab(tab);
    });

    // Toggle leaderboard view (full vs top-3)
    $('#toggle-leaderboard-btn').on('click', function() {
        const $cont = $('#leaderboard-container');
        if ($cont.hasClass('collapsed')) {
            $cont.removeClass('collapsed');
            $(this).text('Show Top 3 Only');
        } else {
            $cont.addClass('collapsed');
            $(this).text('Show All Rankings');
        }
    });

    $('#logout-btn').on('click', function() {
    $.ajax({
      url: '/api/logout',
      type: 'POST',
      success: function() {
        window.location.href = '/';
      },
      error: function() {
        alert('Logout failed.');
      }
    });
  });
});


function switchTab(tab) {
    // Activate the selected tab
    $('.tab').removeClass('active');
    $('#tab-' + tab).addClass('active');
    // Update nav items
    $('.nav-item').removeClass('active');
    $('.nav-item').filter(function() {
        return $(this).text().trim().toLowerCase() === tab;
    }).addClass('active');
    // Load content for the selected tab
    if (tab === 'record') {
        loadRecord();
    } else if (tab === 'social') {
        loadPosts();
    }
}

function initCharts() {
    // Initialize line chart: You vs Average daily hours
    const ctx = document.getElementById('line-chart')?.getContext('2d');
    if (ctx) {
        lineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    { label: 'You', data: [], tension: 0.4, fill: true },
                    { label: 'Average', data: [], tension: 0.4, fill: true }
                ]
            },
            options: { scales: { y: { beginAtZero: true } }, plugins: { legend: { position: 'top' } } }
        });
    }
    // Initialize pie chart: Aerobic vs Anaerobic
    const pieCtx = document.getElementById('pie-chart')?.getContext('2d');
    if (pieCtx) {
        pieChart = new Chart(pieCtx, {
            type: 'doughnut',
            data: { labels: ['Aerobic', 'Anaerobic'], datasets: [{ data: [0, 0] }] },
            options: { plugins: { legend: { position: 'bottom' } } }
        });
    }
    // Initialize radar chart: Difficulty comparison
    const radarCtx = document.getElementById('radar-chart')?.getContext('2d');
    if (radarCtx) {
        radarChart = new Chart(radarCtx, {
            type: 'radar',
            data: { labels: [], datasets: [ { label: 'You', data: [], fill: false }, { label: 'Average', data: [], fill: false } ] },
            options: { scales: { r: { beginAtZero: true, max: 5 } }, plugins: { legend: { position: 'top' } } }
        });
    }
}

function loadRecord() {
    // Read current time range and selected user
    const range = $('#record-range-select').val();
    const userId = $('#user-select').val();
    // Fetch all record data endpoints with both parameters
    fetchMetrics(range, userId);
    fetchTrend(range, userId);
    fetchAeroAnaerobic(range, userId);
    fetchCategoryComparison(range, userId);
    fetchLeaderboard(range);
}

// Fetch and display metrics (streak, calories, hours, percentile)
function fetchMetrics(range, userId) {
    $.getJSON(`/api/record/metrics?range=${range}&user_id=${userId}`, function(data) {
        $('#streak-count').text(data.current_streak);
        $('#total-calories').text(data.total_calories);
        $('#total-hours').text(data.total_hours);
        $('#percentile').text(data.percentile + '%');
    }).fail(function(xhr) {
        if (xhr.status === 401) {
            alert('Please login first');
            window.location.href = '/';
        }
    });
}

// Fetch and update line chart
function fetchTrend(range, userId) {
    $.getJSON(`/api/record/trend?range=${range}&user_id=${userId}`, function(data) {
        lineChart.data.labels = data.labels;
        lineChart.data.datasets[0].data = data.you;
        lineChart.data.datasets[1].data = data.average;
        lineChart.update();
    });
}

// Fetch and update pie chart
function fetchAeroAnaerobic(range, userId) {
    $.getJSON(`/api/record/aeroAnaerobic?range=${range}&user_id=${userId}`, function(data) {
        pieChart.data.datasets[0].data = [data.aerobic, data.anaerobic];
        pieChart.update();
    });
}

// Fetch and update radar chart
function fetchCategoryComparison(range, userId) {
    $.getJSON(`/api/record/categoryComparison?range=${range}&user_id=${userId}`, function(data) {
        radarChart.data.labels = data.categories;
        radarChart.data.datasets[0].data = data.you;
        radarChart.data.datasets[1].data = data.average;
        radarChart.update();
    });
}

// Fetch and render leaderboard table (no user param needed)
function fetchLeaderboard(range) {
    $.getJSON(`/api/record/leaderboard?range=${range}`, function(list) {
        const tbody = $('#leaderboard-table tbody').empty();
        list.forEach(item => {
            tbody.append(
                `<tr><td>${item.rank}</td><td>${item.username}</td>` +
                `<td>${item.total_calories}</td><td>${item.total_hours}</td></tr>`
            );
        });
    });
}

// Fetch and render post of main account page
function showAccountMain() {
  $.get('/api/account/info', function(data) {
    $('#account-avatar').attr('src', data.avatar || '/uploads/default.jpg');
    $('#account-username').text(data.username);
    $('#account-coins').text(data.coins || 0);
    $('#account-main-view').show();
    $('#account-info-view').hide();
    $('#account-edit-view').hide();
  }).fail(function() {
    alert('Failed to load user information.');
  });
}

// Fetch and render post of 'my' page
function showMyInfo() {
    $.get('/api/account/info', function(data) {
        $('#info-avatar').attr('src', data.avatar || '/uploads/default.jpg');
        $('#info-username').text(data.username);
        $('#info-username-detail').text(data.username);
        $('#info-nickname').text(data.nickname || 'Not set');
        $('#info-email').text(data.email || 'Not set');
        $('#info-address').text(data.address || 'Not set');
        $('#info-coins').text(data.coins || 0);

        $('#account-main-view').hide();
        $('#account-info-view').show();
        $('#account-edit-view').hide();
    }).fail(function() {
        alert('Failed to load user information.');
    });
}

// Fetch and render post of update page
function showEditInfo() {
    $('#edit-avatar-preview').attr('src', $('#account-avatar').attr('src'));
    $('#edit-username').text($('#account-username').text());
    $('#edit-coins').text($('#account-coins').text());

    $('#account-main-view').hide();
    $('#account-info-view').hide();
    $('#account-edit-view').show();
}
// 
// Handle avatar upload and preview
$('#edit-avatar').on('change', function() {
    console.log('File input changed');
    const file = this.files[0];
    if (!file) {
        console.log('No file selected');
        return;
    }

    console.log(`Selected file: ${file.name}`);

    // Type and size check
    const allowedTypes = ['image/jpeg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
        alert('Only JPG/PNG formats are allowed.');
        this.value = '';
        return;
    }
    if (file.size > 5 * 1024 * 1024) {
        alert('File size cannot exceed 5MB.');
        this.value = '';
        return;
    }

    // Preview the image
    const reader = new FileReader();
    reader.onload = e => $('#edit-avatar-preview').attr('src', e.target.result);
    reader.readAsDataURL(file);
});

$('#edit-info-form').on('submit', function(e) {
    e.preventDefault();

    const formData = new FormData();
    formData.append('nickname', $('#edit-nickname').val());
    formData.append('address', $('#edit-address').val());
    const file = $('#edit-avatar')[0].files[0];
    if (file) formData.append('avatar', file);

    console.log('FormData content:');
    for (let pair of formData.entries()) {
        console.log(pair[0] + ': ' + pair[1]);
    }

    $.ajax({
        url: '/api/account/edit',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function() {
            alert('Information updated successfully.');
            showMyInfo(); // Refresh the info view
        },
        error: function(xhr) {
            console.error(`Failed to update information: ${xhr.responseText}`);
            alert('Failed to update information.');
        }
    });
});