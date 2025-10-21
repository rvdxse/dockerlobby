export async function fetchContainers() {
    const r = await fetch('/data');
    if (!r.ok) throw new Error('fetch failed');
    return await r.json();
}

export async function sendAction(id, cmd) {
    const r = await fetch(`/${cmd}/${id}`, { method: 'POST' });
    if (!r.ok) throw new Error(`action ${cmd} failed`);
    return r;
}

export async function getInspect(id) {
    const r = await fetch(`/inspect/${id}`);
    if (!r.ok) throw new Error('inspect failed');
    return await r.json();
}

export async function getLogs(id) {
    const r = await fetch(`/logs/${id}`);
    if (!r.ok) throw new Error('logs failed');
    return await r.text();
}
