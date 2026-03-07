document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('hider-form');
    const commandSelect = document.getElementById('command-select');
    const modeSelect = document.getElementById('mode-select');
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const loader = submitBtn.querySelector('.loader');
    const resultArea = document.getElementById('result-area');
    const downloadLink = document.getElementById('download-link');

    const config = {
        universal: {
            modes: ['hide', 'extract', 'hta-polyglot'],
            labels: { hide: 'Data to hide', 'hta-polyglot': 'Script Template' },
            showObfuscate: ['hta-polyglot']
        },
        pdf: {
            modes: ['view', 'edit', 'open-action'],
            labels: { edit: 'Value', 'open-action': 'JS Payload' },
            showObfuscate: ['open-action']
        },
        office: {
            modes: ['view', 'edit'],
            labels: { edit: 'Value' },
            showObfuscate: []
        },
        dll: {
            modes: ['view', 'hide', 'extract'],
            labels: { hide: 'Data to hide' },
            showObfuscate: []
        },
        video: {
            modes: ['view', 'edit'],
            labels: { edit: 'Value' },
            showObfuscate: []
        },
        lsb: {
            modes: ['hide', 'extract'],
            labels: { hide: 'Data to hide' },
            showObfuscate: []
        },
        shortcut: {
            modes: ['generate'],
            labels: { generate: 'Command to execute' },
            showObfuscate: []
        }
    };

    function updateModes() {
        const cmd = commandSelect.value;
        const modes = config[cmd].modes;
        modeSelect.innerHTML = modes.map(m => `<option value="${m}">${m.charAt(0).toUpperCase() + m.slice(1)}</option>`).join('');
        updateInputs();
    }

    function updateInputs() {
        const cmd = commandSelect.value;
        const mode = modeSelect.value;
        const labels = config[cmd].labels;
        const dataGroup = document.getElementById('data-group');
        const obfuscateGroup = document.getElementById('obfuscate-group');
        const dataLabel = document.getElementById('data-label');

        if (labels[mode]) {
            dataGroup.classList.remove('hidden');
            dataLabel.textContent = labels[mode];
        } else {
            dataGroup.classList.add('hidden');
        }

        if (config[cmd].showObfuscate.includes(mode)) {
            obfuscateGroup.classList.remove('hidden');
        } else {
            obfuscateGroup.classList.add('hidden');
        }
    }

    commandSelect.addEventListener('change', updateModes);
    modeSelect.addEventListener('change', updateInputs);

    // Initial load
    updateModes();

    // Drop zone handling
    dropZone.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            dropZone.querySelector('.drop-zone__prompt').textContent = fileInput.files[0].name;
        }
    });

    ['dragover', 'dragleave', 'drop'].forEach(evt => {
        dropZone.addEventListener(evt, e => {
            e.preventDefault();
            if (evt === 'dragover') dropZone.classList.add('drop-zone--over');
            else dropZone.classList.remove('drop-zone--over');
        });
    });

    dropZone.addEventListener('drop', e => {
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            dropZone.querySelector('.drop-zone__prompt').textContent = fileInput.files[0].name;
        }
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        btnText.classList.add('hidden');
        loader.classList.remove('hidden');
        submitBtn.disabled = true;
        resultArea.classList.add('hidden');

        const formData = new FormData(form);
        
        try {
            const resp = await fetch('/api/process', {
                method: 'POST',
                body: formData
            });
            const result = await resp.json();

            if (result.success) {
                downloadLink.href = `/download/${result.filename}`;
                resultArea.classList.remove('hidden');
                resultArea.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert('Error: ' + result.error);
            }
        } catch (err) {
            alert('Request failed. Make sure the server is running.');
        } finally {
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });
});
