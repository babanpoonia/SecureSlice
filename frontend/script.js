async function fetchThreats() {
    const res = await fetch('http://localhost:5000/api/threats');
    const data = await res.json();
    const container = document.getElementById('threats');
    container.innerHTML = '';
    data.forEach(t => {
        container.innerHTML += `<p>${t.timestamp} - ${t.source_ip} -> ${t.dest_ip} [${t.protocol}]</p>`;
    });
}

setInterval(fetchThreats, 2000);
fetchThreats();
