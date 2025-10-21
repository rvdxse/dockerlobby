import { shortText, showLogsWindow } from './utils.js';
import { sendAction, getInspect, getLogs, fetchContainers } from './api.js';

export async function render(list) {
    const grid = document.getElementById('container-grid');

    if (!Array.isArray(list) || list.length === 0) {
        grid.innerHTML = `
            <div style="color:#55ff88;padding:18px;border-radius:8px;background:rgba(0,0,0,0.35);grid-column:1/-1">
                No containers ¯&bsol;_(ツ)_/¯
            </div>`;
        return;
    }

    const fragment = document.createDocumentFragment();

    list.forEach(c => {
        const card = document.createElement('div');
        card.className = 'card';
        card.dataset.id = c.id;

        const stateClass = (c.status === 'running') ? 'running' : 'exited';
        const readableCreated = c.created ? new Date(c.created).toLocaleString() : '-';
        const cpu = c.cpu_percent || 'N/A';
        const mem = c.mem_usage || 'N/A';
        const cpuHTML = (cpu !== 'N/A') ? ` <br>CPU: ${cpu}` : '<br>&nbsp;';
        const ramHTML = (mem !== 'N/A') ? ` <br>RAM: ${mem}` : '<br>&nbsp;';

        card.innerHTML = `
            <div class="cid">${c.short_id}</div>
            <div class="name">${shortText(c.name)}</div>
            <div class="meta">
                Image: ${shortText(c.image || '-')}<br>
                Created: ${readableCreated}
                ${cpuHTML}
                ${ramHTML}
            </div>
            <div class="status ${stateClass}">${c.status.toUpperCase()}</div>
            <div class="actions">
                <button class="btn ${c.status === 'running' ? 'stop' : 'start'}" data-cmd="${c.status === 'running' ? 'stop' : 'start'}">
                    ${c.status === 'running' ? '⏹ STOP' : '▶ START'}
                </button>
                <button class="btn ghost" data-cmd="inspect">🔎 INSPECT</button>
                <button class="btn ghost" data-cmd="logs">📜 LOGS</button>
            </div>
        `;

        fragment.appendChild(card);
    });

    grid.replaceChildren(fragment);
    document.getElementById('instance-time').innerText = new Date().toLocaleString();
}

export function bindActions() {
    const grid = document.getElementById('container-grid');

    grid.addEventListener('click', async e => {
        const btn = e.target.closest('button');
        if (!btn) return;

        const cmd = btn.dataset.cmd;
        const card = btn.closest('.card');
        const id = card?.dataset.id;
        if (!id || !cmd) return;

        btn.disabled = true;
        try {
            if (cmd === 'start' || cmd === 'stop') {
                await sendAction(id, cmd);
                const data = await fetchContainers();
                render(data);
            } else if (cmd === 'inspect') {
                const data = await getInspect(id);
                alert(JSON.stringify(data, null, 2));
            } else if (cmd === 'logs') {
                const text = await getLogs(id);
                showLogsWindow(id, text);
            }
        } catch (err) {
            alert('Ошибка выполнения команды: ' + err.message);
        } finally {
            btn.disabled = false;
        }
    });
}
