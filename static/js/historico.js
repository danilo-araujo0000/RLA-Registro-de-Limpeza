// Data passed from Django template
let offset = window.historicoData ? window.historicoData.offset : 0;
const salaId = window.historicoData ? window.historicoData.salaId : null;
const tipoFilter = document.getElementById('tipoFilter');
const registrosContainer = document.getElementById('registros-container');

function atualizarDestaque() {
    const itens = Array.from(registrosContainer.querySelectorAll('.registro-item'));
    let destaqueAplicado = false;

    itens.forEach(item => {
        const visivel = item.style.display !== 'none';
        const badgeUltimo = item.querySelector('.badge.bg-primary');

        if (!destaqueAplicado && visivel) {
            item.classList.add('destaque');
            if (badgeUltimo) {
                badgeUltimo.style.display = '';
            }
            destaqueAplicado = true;
        } else {
            item.classList.remove('destaque');
            if (badgeUltimo) {
                badgeUltimo.style.display = 'none';
            }
        }
    });
}

function aplicarFiltroTipo() {
    const filtro = tipoFilter.value;
    const itens = registrosContainer.querySelectorAll('.registro-item');

    itens.forEach(item => {
        const itemTipo = item.dataset.tipo || '';
        const corresponde = !filtro || itemTipo === filtro;
        item.style.display = corresponde ? '' : 'none';
    });

    atualizarDestaque();
}

tipoFilter.addEventListener('change', aplicarFiltroTipo);

async function carregarMais() {
    const btn = document.getElementById('btn-mostrar-mais');
    btn.disabled = true;
    btn.textContent = 'Carregando...';

    try {
        const response = await fetch(`/historico/${salaId}/?offset=${offset}&ajax=1`);
        const data = await response.json();

        if (data.registros && data.registros.length > 0) {
            registrosContainer.insertAdjacentHTML('beforeend', data.html);
            offset += data.registros.length;

            if (!data.has_more) {
                btn.remove();
            } else {
                btn.disabled = false;
                btn.textContent = 'Mostrar Mais';
            }
            aplicarFiltroTipo();
        } else {
            btn.remove();
        }
    } catch (error) {
        console.error('Erro ao carregar mais registros:', error);
        btn.disabled = false;
        btn.textContent = 'Erro - Tentar Novamente';
    }
}

aplicarFiltroTipo();