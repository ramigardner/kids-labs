const socket = io();

// Elementos DOM
const animalsContainer = document.getElementById('animals-container');
const extTempSpan = document.getElementById('ext-temp');
const realitySpan = document.getElementById('reality-value');
const chainContainer = document.getElementById('chain-container');
const simulateBtn = document.getElementById('simulate-round-btn');

// Mapeo de animales a emojis
const animalEmojis = {
    buho: '🦉',
    zorro: '🦊',
    topo: '🐭',
    abeja: '🐝'
};

socket.on('connect', () => {
    console.log('Conectado al jardín');
    socket.emit('request_update');
});

socket.on('garden_update', (data) => {
    updateGardenUI(data);
});

socket.on('chain_update', (blocks) => {
    updateChainUI(blocks);
});

function updateGardenUI(data) {
    const animals = data.animals;
    extTempSpan.textContent = data.external_temp.toFixed(1);
    realitySpan.textContent = data.reality.toFixed(3);

    let html = '';
    for (let [key, animal] of Object.entries(animals)) {
        const karmaPercent = (animal.karma * 100).toFixed(0);
        html += `
            <div class="animal-card">
                <div class="animal-emoji">${animalEmojis[key] || '🐾'}</div>
                <div class="animal-name">${animal.name}</div>
                <div class="karma-bar">
                    <div class="karma-fill" style="width: ${karmaPercent}%;"></div>
                </div>
                <div class="animal-stats">
                    ✨ Brillo: ${animal.karma.toFixed(2)}<br>
                    ⏱️ Latencia: ${animal.latency.toFixed(2)}
                </div>
            </div>
        `;
    }
    animalsContainer.innerHTML = html;
}

function updateChainUI(blocks) {
    let html = '';
    blocks.slice(-8).reverse().forEach(block => {
        html += `
            <div class="chain-block">
                <span class="index">Bloque #${block.index}</span><br>
                <span class="hash">🔒 ${block.hash}</span><br>
                <span class="hash-prev">◀ ${block.prev_hash}</span><br>
                <span>📦 ${JSON.stringify(block.data).substring(0, 50)}...</span>
            </div>
        `;
    });
    chainContainer.innerHTML = html;
}

simulateBtn.addEventListener('click', () => {
    socket.emit('simulate_round');
});

// Pestañas
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.add('active');
        if (btn.dataset.tab === 'chain') {
            socket.emit('request_update');
        }
    });
});