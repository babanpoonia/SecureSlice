async function fetchData() {
  const ueRes = await fetch('/api/ue-list');
  const ueList = await ueRes.json();
  const ueContainer = document.getElementById('ue-list');
  ueContainer.innerHTML = '';
  ueList.forEach(ue => {
    ueContainer.innerHTML += `<li class="list-group-item">${ue.imsi}</li>`;
  });

  const threatRes = await fetch('/api/threats');
  const logs = await threatRes.json();
  const logList = document.getElementById('log-list');
  logList.innerHTML = '';
  const reversedLogs = [...logs].reverse();
  reversedLogs.forEach(log => {
    logList.innerHTML += `<li class="list-group-item">${log.time} - ${log.message}</li>`;
  });

  const chartLabels = logs.map(l => l.time);
  const chartData = logs.map(l => l.score);
  threatChart.data.labels = chartLabels;
  threatChart.data.datasets[0].data = chartData;
  threatChart.update();
}

const ctx = document.getElementById('threatChart').getContext('2d');
const threatChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [{
      label: 'Threat Score',
      data: [],
      borderColor: 'red',
      fill: false
    }]
  }
});

fetchData();
setInterval(fetchData, 3000);
