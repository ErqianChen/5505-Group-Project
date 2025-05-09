let lineChart, pieChart, radarChart;

$(document).ready(function() {
    initCharts();
    $('#record-range-select').on('change', loadRecord);
    $('.nav-item').on('click', function() {
        const tab = $(this).text().trim().toLowerCase();
        switchTab(tab);
    });
    
    // Initialize active tab on page load
    if ($('#tab-record').hasClass('active')) {
        loadRecord();
    } else if ($('#tab-social').hasClass('active')) {
        // Initialize social tab if it's active on load
        loadPosts();
    }
    
    $('#leaderboard-container').addClass('collapsed');

    // Toggle full / top-3 view
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
});

function switchTab(tab) {
    $('.tab').removeClass('active');
    $('#tab-' + tab).addClass('active');
    
    // Initialize functionality based on active tab
    if (tab === 'record') {
        loadRecord();
    } else if (tab === 'social') {
        // Initialize social functionality when switching to social tab
        loadPosts();
    }
    
    // Add active class to the selected nav item
    $('.nav-item').removeClass('active');
    $('.nav-item').filter(function() {
        return $(this).text().trim().toLowerCase() === tab;
    }).addClass('active');
}

function initCharts() {
    // Line chart: User vs Average daily hours
    const ctx = document.getElementById('line-chart')?.getContext('2d');
    if (!ctx) return;
    
    lineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'You',
                    data: [],
                    borderColor: 'rgba(54,162,235,1)',
                    backgroundColor: 'rgba(54,162,235,0.1)',
                    fill: true,
                    tension: 0.4,
                },
                {
                    label: 'Average',
                    data: [],
                    borderColor: 'rgba(255,99,132,1)',
                    backgroundColor: 'rgba(255,99,132,0.1)',
                    fill: true,
                    tension: 0.4,
                }
            ]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            },
            plugins: {
                legend: { position: 'top' }
            }
        }
    });

    // Pie chart: Aerobic vs Anaerobic
    const pieCtx = document.getElementById('pie-chart')?.getContext('2d');
    if (!pieCtx) return;
    
    pieChart = new Chart(pieCtx, {
        type: 'doughnut',
        data: {
            labels: ['Aerobic', 'Anaerobic'],
            datasets: [{ data: [0, 0] }]
        },
        options: {
            plugins: { legend: { position: 'bottom' } }
        }
    });

    // Radar chart: Difficulty comparison
    const radarCtx = document.getElementById('radar-chart')?.getContext('2d');
    if (!radarCtx) return;
    
    radarChart = new Chart(radarCtx, {
        type: 'radar',
        data: {
            labels: [],
            datasets: [
                { label: 'You', data: [], fill: false },
                { label: 'Average', data: [], fill: false }
            ]
        },
        options: {
            scales: { r: { beginAtZero: true, max: 5 } },
            plugins: { legend: { position: 'top' } }
        }
    });
}

function loadRecord() {
    const range = $('#record-range-select').val();
    fetchMetrics(range);
    fetchTrend(range);
    fetchAeroAnaerobic(range);
    fetchCategoryComparison(range);
    fetchLeaderboard(range);
}

// Fetch and render metrics cards
function fetchMetrics(range) {
    $.getJSON(`/api/record/metrics?range=${range}`, function(data) {
        $('#streak-count').text(data.current_streak);
        $('#total-calories').text(data.total_calories);
        $('#total-hours').text(data.total_hours);
        $('#percentile').text(data.percentile + '%');
    });
}

// Fetch and render line chart with You vs Average
function fetchTrend(range) {
    $.getJSON(`/api/record/trend?range=${range}`, function(data) {
        lineChart.data.labels = data.labels;
        lineChart.data.datasets[0].data = data.you;
        lineChart.data.datasets[1].data = data.average;
        lineChart.update();
    });
}

// Fetch and render pie chart
function fetchAeroAnaerobic(range) {
    $.getJSON(`/api/record/aeroAnaerobic?range=${range}`, function(data) {
        pieChart.data.datasets[0].data = [data.aerobic, data.anaerobic];
        pieChart.update();
    });
}

// Fetch and render radar chart
function fetchCategoryComparison(range) {
    $.getJSON(`/api/record/categoryComparison?range=${range}`, function(data) {
        radarChart.data.labels = data.categories;
        radarChart.data.datasets[0].data = data.you;
        radarChart.data.datasets[1].data = data.average;
        radarChart.update();
    });
}

// Fetch and render leaderboard table
function fetchLeaderboard(range) {
    $.getJSON(`/api/record/leaderboard?range=${range}`, function(list) {
        const tbody = $('#leaderboard-table tbody').empty();
        list.forEach(item => {
            tbody.append(`
                <tr>
                    <td>${item.rank}</td>
                    <td>${item.username}</td>
                    <td>${item.total_calories}</td>
                    <td>${item.total_hours}</td>
                </tr>`);
        });
    });
}