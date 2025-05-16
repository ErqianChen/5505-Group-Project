let currentDate = new Date().toISOString().split('T')[0];  // Today

document.addEventListener('DOMContentLoaded', () => {
    loadPlans();
});

function loadPlans() {
    fetch(`/api/plans?date=${currentDate}`)
        .then(res => res.json())
        .then(plans => {
            const list = document.getElementById('plan-list');
            list.innerHTML = '';
            const chartLabels = [];
            const chartData = [];

            plans.forEach(plan => {
                const div = document.createElement('div');
                div.className = 'plan-card';
                const start = new Date(plan.start_time);
                const end = new Date(plan.end_time);
                const durationMin = (end - start) / 60000;
                chartLabels.push(plan.activity);
                chartData.push(durationMin);

                div.innerHTML = `
                    <img src="jogging.jpg" />
                    <div class="plan-info">
                        <p>${start.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})} - ${end.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}</p>
                        <h3>${plan.activity}</h3>
                        <button class="start-btn">Start Now</button>
                        <button class="edit-btn" onclick="editPlan(${plan.id}, '${plan.activity}', '${plan.start_time}', '${plan.end_time}')">Edit</button>
                        <button class="cancel-btn" onclick="cancelPlan(${plan.id})">Cancel</button>
                    </div>`;
                list.appendChild(div);
            });

            renderChart(chartLabels, chartData);
            updateDateLabel();
        });
  
    fetch('/api/record/aeroAnaerobic')
    .then(res => res.json())
    .then(data => {
      renderPieChart(data.aerobic, data.anaerobic);
    });
      
}

function renderChart(labels, data) {
    const canvas = document.getElementById('activityChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: ['#6ab7ff', '#9575cd', '#ffcc80', '#81c784'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' },
            }
        }
    });
}

function renderPieChart(aerobic, anaerobic) {
  const pieCtx = document.getElementById('aerobicPieChart').getContext('2d');

  new Chart(pieCtx, {
    type: 'doughnut',
    data: {
      labels: ['Aerobic (≥6.0 METs)', 'Anaerobic (<6.0 METs)'],
      datasets: [{
        data: [aerobic, anaerobic],
        backgroundColor: ['#42a5f5', '#ef5350'],
        borderWidth: 1
      }]
    },
    options: {
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.label}: ${context.raw} hr`;
            }
          }
        }
      }
    }
  });
}

function cancelPlan(id) {
    fetch(`/api/plans/${id}`, { method: 'DELETE' })
        .then(() => loadPlans());
}

function editPlan(id, activity, start, end) {
    document.getElementById('activityInput').value = activity;
    document.getElementById('startInput').value = start.slice(0, 16);
    document.getElementById('endInput').value = end.slice(0, 16);
    document.getElementById('planForm').dataset.editingId = id;
    document.getElementById('planModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('planModal').style.display = 'none';
    delete document.getElementById('planForm').dataset.editingId;
    document.getElementById('planForm').reset();
}

document.querySelector('.add-plan-btn').addEventListener('click', () => {
    document.getElementById('planModal').style.display = 'block';
});

document.getElementById('planForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const activity = document.getElementById('activityInput').value;
    const start = document.getElementById('startInput').value;
    const end = document.getElementById('endInput').value;

    // 简单前端校验
    if (!activity || !start || !end) {
        alert("Please fill in all fields.");
        return;
    }
    if (new Date(end) <= new Date(start)) {
        alert("End time must be after start time.");
        return;
    }

    // 清空表单
    document.getElementById('planForm').reset();

    // 显示提示
    let msg = document.getElementById('plan-success-msg');
    msg.textContent = 'Plan added successfully!';
    msg.style.display = 'block';

    // 2秒后自动关闭弹窗和提示
    setTimeout(() => {
        closeModal();
        msg.style.display = 'none';
    }, 2000);
});

// date change
document.getElementById('prev-day').addEventListener('click', () => {
    const date = new Date(currentDate);
    date.setDate(date.getDate() - 1);
    currentDate = date.toISOString().split('T')[0];
    updateDateLabel();
    loadPlans();
});

document.getElementById('next-day').addEventListener('click', () => {
    const date = new Date(currentDate);
    date.setDate(date.getDate() + 1);
    currentDate = date.toISOString().split('T')[0];
    updateDateLabel();
    loadPlans();
});

function updateDateLabel() {
    const dateObj = new Date(currentDate);
    const today = new Date();
    const label = document.getElementById('date-label');

    const isToday =
        dateObj.getFullYear() === today.getFullYear() &&
        dateObj.getMonth() === today.getMonth() &&
        dateObj.getDate() === today.getDate();

    if (isToday) {
        label.textContent = "Today";
    } else {
        // 
        const month = String(dateObj.getMonth() + 1).padStart(2, '0');
        const day = String(dateObj.getDate()).padStart(2, '0');
        label.textContent = `${month}.${day}`;
    }
}