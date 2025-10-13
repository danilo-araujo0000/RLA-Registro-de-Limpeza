let segundos = 7;
const timerElement = document.getElementById('timer');

const countdown = setInterval(() => {
    segundos--;
    timerElement.textContent = segundos;

    if (segundos <= 0) {
        clearInterval(countdown);
    }
}, 1000);