export function initTypewriterHeader(text = "DOCKER::PANEL", speed = 150) {
    const headerElement = document.getElementById('typed-text-header');
    const cursorElement = document.getElementById('header-cursor');
    let i = 0;

    function type() {
        if (i < text.length) {
            headerElement.textContent += text.charAt(i++);
            cursorElement.style.opacity = 1;
            setTimeout(type, speed);
        } else {
            cursorElement.classList.add('cursor-blinking');
        }
    }

    setTimeout(type, 500);
}
