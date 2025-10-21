export function shortText(t = '', len = 36) {
    return t.length > len ? `${t.slice(0, len - 1)}…` : t;
}

export function showStatusOnline() {
    const el = document.getElementById('status-msg');
    el.innerHTML = 'Статус: <strong style="color:#55ff88">online</strong>';
}

export function showStatusOffline() {
    const el = document.getElementById('status-msg');
    el.innerHTML = 'Статус: <strong style="color:#ff6b9a">offline</strong>';
}

export function showLogsWindow(id, text) {
    const lines = text.trim().split('\n').slice(-200).join('\n');
    const win = window.open('', '_blank', 'width=800,height=600,scrollbars=yes');
    win.document.title = 'Logs ' + id;
    win.document.body.style.cssText = `
        background:#000;
        color:#8aff8a;
        font-family:monospace;
        white-space:pre-wrap;
        padding:12px;
    `;
    win.document.body.innerText = lines || '(empty)';
}
