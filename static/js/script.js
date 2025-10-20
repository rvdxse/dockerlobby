function initTypewriterHeader() {
    const headerText = "DOCKER::PANEL";
    const headerElement = document.getElementById('typed-text-header');
    const cursorElement = document.getElementById('header-cursor');
    let i = 0;
    const speed = 150; 

    function type() {
        if (i < headerText.length) {
            headerElement.textContent += headerText.charAt(i);
            i++;
            cursorElement.style.opacity = 1; 
            setTimeout(type, speed);
        } else {
            cursorElement.classList.add('cursor-blinking');
        }
    }

    setTimeout(type, 500);
}

async function fetchContainers() {
    try {
        const r = await fetch('/data');
        const list = await r.json();
        render(list);
        document.getElementById('instance-time').innerText = new Date().toLocaleString();
    } catch (e) {
        console.error('fetch error', e);
        document.getElementById('status-msg').innerHTML = 'Статус: <strong style="color:#ff6b9a">offline</strong>';
    }
}

function shortText(t, len=36){ if(!t) return ''; return t.length>len ? t.slice(0,len-1)+'…' : t; }

function render(list) {
    const grid = document.getElementById('container-grid');
    if(!Array.isArray(list) || list.length===0) {
        grid.innerHTML = `<div style="color:#55ff88;padding:18px;border-radius:8px;background:rgba(0,0,0,0.35);grid-column:1/-1">Нет контейнеров. Запусти docker run :)</div>`;
        return;
    }

    grid.innerHTML = list.map(c => {
        const stateClass = (c.status==='running') ? 'running' : 'exited';
        const readableCreated = c.created ? new Date(c.created).toLocaleString() : '-';
        const image = c.image || '-';
        const cpuPercent = c.cpu_percent || 'N/A';
        const memUsage = c.mem_usage || 'N/A';
        return `
            <div class="card" data-id="${c.id}">
                <div class="cid">${c.short_id}</div>
                <div class="name">${shortText(c.name)}</div>
                <div class="meta">Image: ${shortText(image)} <br>Created: ${readableCreated} <br>CPU: ${cpuPercent} <br>RAM: ${memUsage}</div>
                <div class="status ${stateClass}">${c.status.toUpperCase()}</div>

                <div class="actions">
                    ${c.status === 'running'
                        ? `<button class="btn stop" onclick="action('${c.id}','stop')">⏹ STOP</button>`
                        : `<button class="btn start" onclick="action('${c.id}','start')">▶ START</button>`
                    }
                    <button class="btn ghost" onclick="action('${c.id}','inspect')">🔎 INSPECT</button>
                    <button class="btn ghost" onclick="action('${c.id}','logs')">📜 LOGS</button>
                </div>
            </div>
        `;
    }).join('');
}

async function action(id, cmd) {
    try {
        if(cmd === 'start' || cmd === 'stop') {
            await fetch(`/${cmd}/${id}`, { method: 'POST' });
            await fetchContainers();
        } else if(cmd === 'inspect') {
            const r = await fetch(`/inspect/${id}`);
            const data = await r.json();
            alert(JSON.stringify(data, null, 2));
        } else if(cmd === 'logs') {
            const r = await fetch(`/logs/${id}`);
            const text = await r.text();
            const lines = text.trim().split('\\n').slice(-200).join('\\n');
            const win = window.open('', '_blank', 'width=800,height=600,scrollbars=yes');
            win.document.title = 'Logs ' + id;
            win.document.body.style.background = '#000';
            win.document.body.style.color = '#8aff8a';
            win.document.body.style.fontFamily = 'monospace';
            win.document.body.style.whiteSpace = 'pre-wrap';
            win.document.body.style.padding = '12px';
            win.document.body.innerText = lines || '(пусто)';
        }
    } catch (e) {
        console.error('action error', e);
        alert('Ошибка выполнения команды: ' + e.message);
    }
}

// FIXME: rewrite logic for webhooks instead of fetch intervals
fetchContainers();
initTypewriterHeader(); 
setInterval(fetchContainers, 3500);
