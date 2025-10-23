let segundos = 10;
const timerElement = document.getElementById('timer');

const countdown = setInterval(() => {
    segundos--;
    timerElement.textContent = segundos;

    if (segundos <= 0) {
        clearInterval(countdown);
        window.location.href = '/salas';
    }
}, 1000);