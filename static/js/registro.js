// Data passed from Django template
const todosColaboradores = window.registroData ? window.registroData.colaboradores : [];
let colaboradoresSelecionados = [];
const MAX_COLABORADORES = 5;

function mostrarAviso(mensagem) {
    const avisoContainer = document.getElementById('aviso-container');
    const aviso = document.createElement('div');
    aviso.className = 'aviso-simples';
    aviso.textContent = mensagem;
    avisoContainer.appendChild(aviso);

    
    setTimeout(() => {
        aviso.remove();
    }, 3000);
}

function adicionarColaborador(colaborador) {
    
    if (colaboradoresSelecionados.length >= MAX_COLABORADORES) {
        mostrarAviso(`Você só pode adicionar até ${MAX_COLABORADORES} colaboradores.`);
        return;
    }

    
    if (colaboradoresSelecionados.find(c => c.cd_usuario === colaborador.cd_usuario)) {
        mostrarAviso('Já adicionado');
        return;
    }

    
    colaboradoresSelecionados.push(colaborador);

    
    renderizarColaboradores();
    atualizarJSON();

    
    document.getElementById('colaborador-search').value = '';
    document.getElementById('colaborador-list').style.display = 'none';

    
    if (colaboradoresSelecionados.length >= MAX_COLABORADORES) {
        document.getElementById('search-container').style.display = 'none';
    }
}

function removerColaborador(index) {
    colaboradoresSelecionados.splice(index, 1);
    renderizarColaboradores();
    atualizarJSON();

    
    if (colaboradoresSelecionados.length < MAX_COLABORADORES) {
        document.getElementById('search-container').style.display = 'block';
    }
}

function renderizarColaboradores() {
    const container = document.getElementById('colaboradores-container');
    container.innerHTML = '';

    colaboradoresSelecionados.forEach((colaborador, index) => {
        const card = document.createElement('div');
        card.className = 'colaborador-card';
        card.innerHTML = `
            <div class="colaborador-info">
                <span class="colaborador-numero">${index + 1}</span>
                <span class="colaborador-nome">${colaborador.primeiro_nome}</span>
                <span class="colaborador-codigo">${colaborador.cd_usuario}</span>
            </div>
            <button type="button" class="btn-remover" onclick="removerColaborador(${index})">
                <i class="fas fa-times"></i> Remover
            </button>
        `;
        container.appendChild(card);
    });
}

function atualizarJSON() {
    const jsonObj = {};
    colaboradoresSelecionados.forEach((colaborador, index) => {
        jsonObj[index + 1] = colaborador.primeiro_nome;
    });

    document.getElementById('colaboradores_json').value = JSON.stringify(jsonObj);

    
    const campoJSON = document.getElementById('colaboradores_json');
    if (colaboradoresSelecionados.length > 0) {
        campoJSON.removeAttribute('required');
    } else {
        campoJSON.setAttribute('required', 'required');
    }
}

function preencherDataHora() {
    const agora = new Date();
    document.getElementById("data").value = agora.toISOString().split('T')[0];
    const horas = String(agora.getHours()).padStart(2, '0');
    const minutos = String(agora.getMinutes()).padStart(2, '0');
    document.getElementById("hora_limpeza").value = `${horas}:${minutos}`;
}

function toggleCamposTerminal() {
    const tipoLimpeza = document.getElementById("tipo_limpeza").value;
    const camposTerminal = document.getElementById("camposTerminal");
    const criticidade = document.getElementById("criticidade");

    if (tipoLimpeza === "2") { 
        camposTerminal.style.display = "block";
        criticidade.setAttribute("required", "required");
    } else {
        camposTerminal.style.display = "none";
        criticidade.removeAttribute("required");

        
        const itens = ['portas', 'teto', 'paredes', 'janelas', 'piso', 'superficie_mobiliario', 'dispenser'];
        itens.forEach(item => {
            document.getElementById(`${item}_hidden`).value = '';
            const radios = document.querySelectorAll(`input[name="modal_${item}"]`);
            radios.forEach(radio => radio.checked = false);
        });

        
        document.getElementById('contadorItens').style.display = 'none';
    }
}

function abrirModal() {
    document.getElementById('modalItensLimpeza').classList.add('show');
    
    document.querySelectorAll('.item-limpeza').forEach(item => {
        item.classList.remove('erro', 'completo');
    });
}

function fecharModal() {
    document.getElementById('modalItensLimpeza').classList.remove('show');
    
    document.querySelectorAll('.item-limpeza').forEach(item => {
        item.classList.remove('erro', 'completo');
    });
}

function confirmarItensLimpeza() {
    const itens = ['portas', 'teto', 'paredes', 'janelas', 'piso', 'superficie_mobiliario', 'dispenser'];
    let todosPreenchidos = true;
    const itensNaoPreenchidos = [];

    
    document.querySelectorAll('#modalItensLimpeza .item-limpeza').forEach(item => {
        item.classList.remove('erro', 'completo');
    });

    itens.forEach(item => {
        const radioSelecionado = document.querySelector(`input[name="modal_${item}"]:checked`);
        const itemDiv = document.querySelector(`input[name="modal_${item}"]`).closest('.item-limpeza');

        if (radioSelecionado) {
            document.getElementById(`${item}_hidden`).value = radioSelecionado.value;
            itemDiv.classList.add('completo');
        } else {
            todosPreenchidos = false;
            itensNaoPreenchidos.push(item);
            itemDiv.classList.add('erro');
        }
    });

    if (!todosPreenchidos) {
        
        const primeiroErro = document.querySelector('#modalItensLimpeza .item-limpeza.erro');
        if (primeiroErro) {
            primeiroErro.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        return;
    }

    
    const contador = document.getElementById('contadorItens');
    contador.textContent = `${itens.length}/${itens.length}`;
    contador.style.display = 'inline';

    
    const campoValidacao = document.getElementById('validacao_itens_limpeza');
    campoValidacao.removeAttribute('required');
    campoValidacao.setCustomValidity('');

    fecharModal();
}

function abrirModalReposicao() {
    document.getElementById('modalReposicao').classList.add('show');
    
    document.querySelectorAll('#modalReposicao .item-limpeza').forEach(item => {
        item.classList.remove('erro', 'completo');
    });
}

function fecharModalReposicao() {
    document.getElementById('modalReposicao').classList.remove('show');
    
    document.querySelectorAll('#modalReposicao .item-limpeza').forEach(item => {
        item.classList.remove('erro', 'completo');
    });
}

function confirmarItensReposicao() {
    const itens = ['papel_hig', 'papel_toalha', 'alcool', 'sabonete'];
    let todosPreenchidos = true;

    
    document.querySelectorAll('#modalReposicao .item-limpeza').forEach(item => {
        item.classList.remove('erro', 'completo');
    });

    itens.forEach(item => {
        const radioSelecionado = document.querySelector(`input[name="modal_${item}"]:checked`);
        const itemDiv = document.querySelector(`input[name="modal_${item}"]`).closest('.item-limpeza');

        if (radioSelecionado) {
            document.getElementById(`${item}_hidden`).value = radioSelecionado.value;
            itemDiv.classList.add('completo');
        } else {
            todosPreenchidos = false;
            itemDiv.classList.add('erro');
        }
    });

    if (!todosPreenchidos) {
        
        const primeiroErro = document.querySelector('#modalReposicao .item-limpeza.erro');
        if (primeiroErro) {
            primeiroErro.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        return;
    }

    
    const contador = document.getElementById('contadorReposicao');
    contador.textContent = `${itens.length}/${itens.length}`;
    contador.style.display = 'inline';

    
    const campoValidacao = document.getElementById('validacao_reposicao');
    campoValidacao.removeAttribute('required');
    campoValidacao.setCustomValidity('');

    fecharModalReposicao();
}

function updateSelectColor(selectElement) {
    selectElement.classList.remove('option-sim', 'option-nao', 'option-neutra', 'option-critico', 'option-semi-critico', 'option-nao-critico');
    if (selectElement.value === 'S') {
        selectElement.classList.add('option-sim');
    } else if (selectElement.value === 'N') {
        selectElement.classList.add('option-nao');
    } else if (selectElement.value === '1') { 
        selectElement.classList.add('option-critico');
    } else if (selectElement.value === '2') { 
        selectElement.classList.add('option-semi-critico');
    } else if (selectElement.value === '3') { 
        selectElement.classList.add('option-nao-critico');
    } else {
        selectElement.classList.add('option-neutra');
    }
}

function filtrarColaboradores(termo) {
    const termoUpper = termo.toUpperCase();
    let resultados;

    if (termo.length === 0) {
        resultados = [...todosColaboradores].sort((a, b) =>
            a.primeiro_nome.localeCompare(b.primeiro_nome)
        );
    } else {
        resultados = todosColaboradores
            .filter(colab => colab.primeiro_nome.toUpperCase().includes(termoUpper))
            .sort((a, b) => a.primeiro_nome.localeCompare(b.primeiro_nome));
    }

    const lista = document.getElementById('colaborador-list');
    lista.innerHTML = '';

    if (resultados.length > 0) {
        resultados.forEach(colaborador => {
            const li = document.createElement('li');

            const nomeSpan = document.createElement('span');
            nomeSpan.textContent = colaborador.primeiro_nome;

            const cdSpan = document.createElement('span');
            cdSpan.className = 'cd-usuario';
            cdSpan.textContent = colaborador.cd_usuario;

            li.appendChild(nomeSpan);
            li.appendChild(cdSpan);

            li.dataset.primeiroNome = colaborador.primeiro_nome;
            li.dataset.nomeCompleto = colaborador.nome_completo;
            li.dataset.cdUsuario = colaborador.cd_usuario;
            li.addEventListener('click', () => selecionarColaborador(colaborador));
            lista.appendChild(li);
        });
        lista.style.display = 'block';
    } else {
        lista.style.display = 'none';
    }
}

function mostrarTodosColaboradores() {
    filtrarColaboradores('');
}

function selecionarColaborador(colaborador) {
    adicionarColaborador(colaborador);
}

document.addEventListener('DOMContentLoaded', () => {
    preencherDataHora();
    document.getElementById("tipo_limpeza").addEventListener("change", toggleCamposTerminal);
    toggleCamposTerminal();

    const terminalSelects = document.querySelectorAll('#camposTerminal .form-select');
    terminalSelects.forEach(select => {
        updateSelectColor(select);
        select.addEventListener('change', () => updateSelectColor(select));
    });

    const inputColaborador = document.getElementById('colaborador-search');
    inputColaborador.addEventListener('click', () => {
        mostrarTodosColaboradores();
    });
    inputColaborador.addEventListener('focus', () => {
        mostrarTodosColaboradores();
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('#colaborador-search') && !e.target.closest('#colaborador-list')) {
            document.getElementById('colaborador-list').style.display = 'none';
        }
    });

    document.getElementById('btnAbrirModal').addEventListener('click', abrirModal);
    document.getElementById('btnFecharModal').addEventListener('click', fecharModal);
    document.getElementById('btnConfirmarModal').addEventListener('click', confirmarItensLimpeza);

    
    document.getElementById('btnAbrirModalReposicao').addEventListener('click', abrirModalReposicao);
    document.getElementById('btnFecharModalReposicao').addEventListener('click', fecharModalReposicao);
    document.getElementById('btnConfirmarModalReposicao').addEventListener('click', confirmarItensReposicao);

    const radios = document.querySelectorAll('#modalItensLimpeza input[type="radio"]');
    radios.forEach(radio => {
        radio.addEventListener('change', () => {
            const itemDiv = radio.closest('.item-limpeza');
            itemDiv.classList.remove('erro');
        });
    });

    const radiosReposicao = document.querySelectorAll('#modalReposicao input[type="radio"]');
    radiosReposicao.forEach(radio => {
        radio.addEventListener('change', () => {
            const itemDiv = radio.closest('.item-limpeza');
            itemDiv.classList.remove('erro');
        });
    });

    document.getElementById('formRegistro').addEventListener('submit', (e) => {
        const tipoLimpeza = document.getElementById('tipo_limpeza').value;

        const colaboradoresJson = document.getElementById('colaboradores_json').value;
        if (!colaboradoresJson || colaboradoresJson.trim() === '' || colaboradoresJson === '{}') {
            e.preventDefault();
            mostrarAviso(' selecione pelo menos um colaborador');

            setTimeout(() => {
                document.getElementById('colaborador-search').focus();
                document.getElementById('colaborador-search').click();
            }, 300);
            return false;
        }

        const itensReposicao = ['papel_hig', 'papel_toalha', 'alcool', 'sabonete'];
        let reposicaoVazio = false;

        itensReposicao.forEach(item => {
            const valor = document.getElementById(`${item}_hidden`).value;
            if (!valor || valor === '') {
                reposicaoVazio = true;
            }
        });

        if (reposicaoVazio) {
            e.preventDefault();
            const campoValidacao = document.getElementById('validacao_reposicao');
            campoValidacao.setAttribute('required', 'required');
            campoValidacao.setCustomValidity(' preencha todos os itens de reposição');
            campoValidacao.reportValidity();

            setTimeout(() => {
                abrirModalReposicao();
            }, 100);
            return false;
        }

        if (tipoLimpeza === '2') { 
            const itensLimpeza = ['portas', 'teto', 'paredes', 'janelas', 'piso', 'superficie_mobiliario', 'dispenser'];
            let itensLimpezaVazio = false;

            itensLimpeza.forEach(item => {
                const valor = document.getElementById(`${item}_hidden`).value;
                if (!valor || valor === '') {
                    itensLimpezaVazio = true;
                }
            });

            if (itensLimpezaVazio) {
                e.preventDefault();
                const campoValidacao = document.getElementById('validacao_itens_limpeza');
                campoValidacao.setAttribute('required', 'required');
                campoValidacao.setCustomValidity(' preencha todos os itens de limpeza');
                campoValidacao.reportValidity();

                setTimeout(() => {
                    abrirModal();
                }, 100);
                return false;
            }
        }
    });
});