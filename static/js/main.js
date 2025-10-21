import { initTypewriterHeader } from './modules/typewriter.js';
import { fetchContainers } from './modules/api.js';
import { render, bindActions } from './modules/ui.js';
import { showStatusOffline, showStatusOnline } from './modules/utils.js';

document.addEventListener('DOMContentLoaded', () => {
    initTypewriterHeader();
    bindActions();
    const eventSource = new EventSource('/events');

    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            render(data);
            showStatusOnline();
        } catch (err) {
            console.error('Error:', err);
        }
    };

    eventSource.onerror = (err) => {
        console.warn('Connection error:', err);
        showStatusOffline();
    };
});
