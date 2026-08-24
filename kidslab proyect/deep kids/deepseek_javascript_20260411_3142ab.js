let editor;

document.addEventListener('DOMContentLoaded', () => {
    editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
        lineNumbers: true,
        mode: 'python',
        theme: 'default',
        indentUnit: 4,
        tabSize: 4
    });

    const challengeSelect = document.getElementById('challenge-select');
    const challengeDesc = document.getElementById('challenge-desc');
    const runBtn = document.getElementById('run-code-btn');
    const outputDiv = document.getElementById('code-output');

    // Cargar desafío seleccionado
    function loadChallenge(challengeId) {
        fetch(`/static/challenge_files/${challengeId.split('_')[0]}.py`)
            .then(res => res.text())
            .then(code => {
                editor.setValue(code);
            });

        // Descripciones manuales
        const descriptions = {
            'buho_fix': 'El Búho reporta latencia 0.8 pero la realidad es 0.3. Modifica la función reportar() para acercarte.',
            'zorro_speed': 'El Zorro es lento (0.45). Haz que su latencia sea menor a 0.2.'
        };
        challengeDesc.textContent = descriptions[challengeId] || '';
    }

    challengeSelect.addEventListener('change', (e) => {
        loadChallenge(e.target.value);
    });

    loadChallenge('buho_fix');

    runBtn.addEventListener('click', () => {
        const code = editor.getValue();
        const challengeId = challengeSelect.value;
        const animal = challengeId.split('_')[0];

        outputDiv.textContent = '⏳ Ejecutando...';
        socket.emit('run_challenge', {
            animal: animal,
            code: code,
            challenge_id: challengeId
        });
    });

    socket.on('challenge_result', (result) => {
        if (result.success) {
            outputDiv.innerHTML = `✅ ${result.message}<br>✨ Nuevo Karma: ${result.new_karma.toFixed(2)}`;
        } else {
            outputDiv.innerHTML = `❌ ${result.message}`;
        }
    });
});