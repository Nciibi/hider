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
            labels: { hide: 'Data to hide', 'hta-polyglot': 'VBScript / Command to run (e.g. calc.exe)' },
            showObfuscate: ['hta-polyglot'],
            showPassword: ['hide', 'extract']
        },
        pdf: {
            modes: ['view', 'edit', 'open-action'],
            labels: { edit: 'New Value', 'open-action': 'JavaScript (e.g. app.alert("X");)' },
            showObfuscate: ['open-action'],
            showPassword: []
        },
        office: {
            modes: ['view', 'edit'],
            labels: { edit: 'Value' },
            showObfuscate: [],
            showPassword: []
        },
        dll: {
            modes: ['view', 'hide', 'extract'],
            labels: { hide: 'Data to hide' },
            showObfuscate: [],
            showPassword: []
        },
        video: {
            modes: ['view', 'edit'],
            labels: { edit: 'Value' },
            showObfuscate: [],
            showPassword: []
        },
        lsb: {
            modes: ['hide', 'extract'],
            labels: { hide: 'Data to hide' },
            showObfuscate: [],
            showPassword: ['hide', 'extract']
        },
        audio: {
            modes: ['hide', 'extract'],
            labels: { hide: 'Data to hide' },
            showObfuscate: [],
            showPassword: ['hide', 'extract']
        },
        archive: {
            modes: ['hide', 'extract'],
            labels: { hide: 'Data to hide' },
            showObfuscate: [],
            showPassword: ['hide', 'extract']
        },
        shortcut: {
            modes: ['generate'],
            labels: { generate: 'Command to execute' },
            showObfuscate: [],
            showPassword: []
        }
    };

    function updateForm() {
        const cmd = commandSelect.value;
        const mode = modeSelect.value;
        const cnf = config[cmd];

        const dataGroup = document.getElementById('data-group');
        const obfuscateGroup = document.getElementById('obfuscate-group');
        const dataLabel = document.getElementById('data-label');
        const keyGroup = document.getElementById('key-group'); // Assuming this element exists in HTML

        // Ensure mode is valid for command
        if (!cnf.modes.includes(modeSelect.value)) {
            modeSelect.innerHTML = cnf.modes.map(m => `<option value="${m}">${m.replace('-', ' ')}</option>`).join('');
            modeSelect.value = cnf.modes[0];
        }

        const currentMode = modeSelect.value;

        // Toggle Key/Value vs Data
        if (['edit'].includes(currentMode) && ['pdf', 'office', 'video'].includes(cmd)) {
            keyGroup.style.display = 'block';
            dataGroup.style.display = 'block';
            dataLabel.textContent = cnf.labels[currentMode] || 'Value';
        } else if (['view', 'extract'].includes(currentMode)) {
            keyGroup.style.display = 'none';
            dataGroup.style.display = 'none';
            if (cmd === 'dll' && currentMode === 'hide') {
                 dataGroup.style.display = 'block';
                 dataLabel.textContent = 'Data to hide';
            }
        } else {
            keyGroup.style.display = 'none';
            dataGroup.style.display = 'block';
            dataLabel.textContent = cnf.labels[currentMode] || 'Payload / Data';
        }
        
        // Hide Data field for view/extract universally
        if(currentMode === 'view' || currentMode === 'extract') {
             dataGroup.style.display = 'none';
        }

        // Toggle Obfuscate
        if (cnf.showObfuscate && cnf.showObfuscate.includes(currentMode)) {
            obfuscateGroup.style.display = 'flex';
        } else {
            obfuscateGroup.style.display = 'none';
        }

        // Toggle Password
        const passwordGroup = document.getElementById('password-group'); // Assuming this element exists in HTML
        if (cnf.showPassword && cnf.showPassword.includes(currentMode)) {
            passwordGroup.style.display = 'block';
        } else {
            passwordGroup.style.display = 'none';
        }
    }

    commandSelect.addEventListener('change', updateForm);
    modeSelect.addEventListener('change', updateForm);

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
