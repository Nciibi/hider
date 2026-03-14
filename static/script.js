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
        },
        evasion: {
            modes: ['generate'],
            labels: { generate: 'Raw Payload (e.g. powershell -c calc)' },
            showObfuscate: [],
            showPassword: [],
            showEvasionOptions: ['generate']
        },
        vba: {
            modes: ['generate'],
            labels: { generate: 'Raw Payload to execute' },
            showObfuscate: [],
            showPassword: [],
            showEvasionOptions: ['generate']
        }
    };

    function updateForm() {
        const command = commandSelect.value;
        const configOptions = config[command];
        
        // Ensure mode is valid for command by updating mode options
        modeSelect.innerHTML = configOptions.modes.map(m => `<option value="${m}">${m.replace('-', ' ')}</option>`).join('');
        // Retain selection if possible
        const mode = configOptions.modes[0];
        
        const keyGroup = document.getElementById('key-group');
        const dataGroup = document.getElementById('data-group');
        const obfuscateGroup = document.getElementById('obfuscate-group');
        const passwordGroup = document.getElementById('password-group');
        const evasionGroup = document.getElementById('evasion-group');
        const fileUploadGroup = document.getElementById('file-upload');
        const dataLabel = document.getElementById('data-label');

        if (fileUploadGroup) {
            if (['shortcut', 'evasion', 'vba'].includes(command)) {
                fileUploadGroup.style.display = 'none';
                fileInput.removeAttribute('required');
            } else {
                fileUploadGroup.style.display = 'block';
                fileInput.setAttribute('required', 'required');
            }
        }

        // Toggle Key/Value vs Data
        if (['edit'].includes(mode) && ['pdf', 'office', 'video'].includes(command)) {
            if(keyGroup) keyGroup.style.display = 'block';
            if(dataGroup) dataGroup.style.display = 'block';
            if(dataLabel) dataLabel.textContent = configOptions.labels[mode] || 'Value';
        } else if (['view', 'extract'].includes(mode)) {
            if(keyGroup) keyGroup.style.display = 'none';
            if(dataGroup) dataGroup.style.display = 'none';
            if (command === 'dll' && mode === 'hide') {
                 if(dataGroup) dataGroup.style.display = 'block';
                 if(dataLabel) dataLabel.textContent = 'Data to hide';
            }
        } else {
            if(keyGroup) keyGroup.style.display = 'none';
            if(dataGroup) dataGroup.style.display = 'block';
            if(dataLabel) dataLabel.textContent = configOptions.labels[mode] || 'Payload / Data';
        }

        // Hide Data field for view/extract universally
        if(mode === 'view' || mode === 'extract') {
             if(dataGroup) dataGroup.style.display = 'none';
        }

        // Toggle Obfuscate
        if (configOptions.showObfuscate && configOptions.showObfuscate.includes(mode)) {
            if(obfuscateGroup) obfuscateGroup.style.display = 'flex';
        } else {
            if(obfuscateGroup) obfuscateGroup.style.display = 'none';
        }

        // Toggle Password
        if (configOptions.showPassword && configOptions.showPassword.includes(mode)) {
            if(passwordGroup) passwordGroup.style.display = 'block';
        } else {
            if(passwordGroup) passwordGroup.style.display = 'none';
        }

        // Toggle Evasion Options
        if (configOptions.showEvasionOptions && configOptions.showEvasionOptions.includes(mode)) {
            if(evasionGroup) evasionGroup.style.display = 'block';
        } else {
            if(evasionGroup) evasionGroup.style.display = 'none';
        }
    }

    commandSelect.addEventListener('change', updateForm);
    // modeSelect is now entirely driven by commandSelect redraw, but we can bind to changes if needed:
    modeSelect.addEventListener('change', () => {
        // partial update if we had multi modes
    });

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
