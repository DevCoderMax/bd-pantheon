document.addEventListener('DOMContentLoaded', function() {
    // Elementos da UI
    const btnListarTabelas = document.getElementById('btnListarTabelas');
    const btnCriarTabela = document.getElementById('btnCriarTabela');
    const btnExecutarSQL = document.getElementById('btnExecutarSQL');
    const btnInfoConexao = document.getElementById('btnInfoConexao');
    const views = {
        tabelas: document.getElementById('tabelasView'),
        criarTabela: document.getElementById('criarTabelaView'),
        executarSQL: document.getElementById('executarSQLView'),
        infoConexao: document.getElementById('infoConexaoView')
    };

    // Funções de navegação
    function showView(viewName) {
        Object.values(views).forEach(view => view.classList.add('hidden'));
        views[viewName].classList.remove('hidden');
    }

    // Event Listeners para navegação
    btnListarTabelas.addEventListener('click', () => {
        showView('tabelas');
        carregarTabelas();
    });
    btnCriarTabela.addEventListener('click', () => showView('criarTabela'));
    btnExecutarSQL.addEventListener('click', () => showView('executarSQL'));
    btnInfoConexao.addEventListener('click', () => {
        showView('infoConexao');
        carregarInfoConexao();
    });

    // Carregar lista de tabelas
    async function carregarTabelas() {
        try {
            const response = await fetch('https://max-python.uvxtdw.easypanel.host/listar-tabelas');
            const data = await response.json();
            
            const listaTabelas = document.getElementById('listaTabelas');
            listaTabelas.innerHTML = '';

            data.tabelas.forEach(tabela => {
                const card = document.createElement('div');
                card.className = 'table-card';
                card.innerHTML = `
                    <h3>${tabela}</h3>
                    <div class="btn-group mt-2">
                        <button class="btn btn-sm btn-info" onclick="verDetalhes('${tabela}')">
                            <i class="bi bi-eye"></i> Ver
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="limparTabela('${tabela}')">
                            <i class="bi bi-trash"></i> Limpar
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="apagarTabela('${tabela}')">
                            <i class="bi bi-trash"></i> Apagar
                        </button>
                    </div>
                `;
                listaTabelas.appendChild(card);
            });
        } catch (error) {
            console.error('Erro ao carregar tabelas:', error);
        }
    }

    // Criar nova tabela
    const formCriarTabela = document.getElementById('formCriarTabela');
    const btnAddColuna = document.getElementById('btnAddColuna');
    const colunasContainer = document.getElementById('colunasContainer');

    btnAddColuna.addEventListener('click', () => {
        const colunaDiv = document.createElement('div');
        colunaDiv.className = 'coluna-item';
        colunaDiv.innerHTML = `
            <input type="text" class="form-control" placeholder="Nome da Coluna">
            <select class="form-control tipo-coluna">
                <option value="ID">ID (Auto)</option>
                <option value="VARCHAR">VARCHAR</option>
                <option value="INT">INT</option>
                <option value="TEXT">TEXT</option>
                <option value="DATE">DATE</option>
                <option value="FLOAT">FLOAT</option>
                <option value="BOOLEAN">BOOLEAN</option>
                <option value="DATETIME">DATETIME</option>
                <option value="TIMESTAMP">TIMESTAMP</option>
                <option value="JSON">JSON</option>
            </select>
            <input type="number" class="form-control tamanho-campo" placeholder="Tamanho" min="1">
            <button type="button" class="btn btn-danger" onclick="this.parentElement.remove()">
                <i class="bi bi-trash"></i>
            </button>
        `;

        // Adiciona evento para mostrar/esconder campo de tamanho
        const tipoSelect = colunaDiv.querySelector('.tipo-coluna');
        const tamanhoInput = colunaDiv.querySelector('.tamanho-campo');
        
        tipoSelect.addEventListener('change', () => {
            const tipo = tipoSelect.value;
            if (tipo === 'VARCHAR' || tipo === 'INT') {
                tamanhoInput.style.display = 'block';
            } else {
                tamanhoInput.style.display = 'none';
                tamanhoInput.value = '';
            }
        });

        // Esconde o campo de tamanho inicialmente se não for VARCHAR
        if (tipoSelect.value !== 'VARCHAR' && tipoSelect.value !== 'INT') {
            tamanhoInput.style.display = 'none';
        }

        colunasContainer.appendChild(colunaDiv);
    });

    formCriarTabela.addEventListener('submit', async (e) => {
        e.preventDefault();
        const nomeTabela = document.getElementById('nomeTabela').value;
        const colunas = Array.from(colunasContainer.children).map(coluna => {
            const tipo = coluna.querySelector('.tipo-coluna').value;
            const tamanho = coluna.querySelector('.tamanho-campo').value;
            
            return {
                nome: coluna.querySelector('input[type="text"]').value,
                tipo: tipo === 'ID' ? 'INT AUTO_INCREMENT PRIMARY KEY' :
                     (tipo === 'VARCHAR' || tipo === 'INT') && tamanho ? 
                     `${tipo}(${tamanho})` : tipo
            };
        });

        try {
            const response = await fetch('https://max-python.uvxtdw.easypanel.host/criar-tabela', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ nome_tabela: nomeTabela, colunas })
            });
            const data = await response.json();
            if (data.status === 'Sucesso') {
                alert('Tabela criada com sucesso!');
                showView('tabelas');
                carregarTabelas();
            }
        } catch (error) {
            console.error('Erro ao criar tabela:', error);
        }
    });

    // Executar SQL
    const btnExecutar = document.getElementById('btnExecutar');
    const sqlQuery = document.getElementById('sqlQuery');
    const resultadoSQL = document.getElementById('resultadoSQL');

    btnExecutar.addEventListener('click', async () => {
        try {
            const response = await fetch('https://max-python.uvxtdw.easypanel.host/executar-sql', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ comando: sqlQuery.value })
            });
            const data = await response.json();
            
            if (data.status === 'Sucesso') {
                resultadoSQL.innerHTML = `
                    <div class="alert alert-success">Comando executado com sucesso!</div>
                    <div class="resultado-tabela">
                        <pre>${JSON.stringify(data.resultado, null, 2)}</pre>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Erro ao executar SQL:', error);
            resultadoSQL.innerHTML = `
                <div class="alert alert-danger">Erro ao executar comando: ${error}</div>
            `;
        }
    });

    // Event Listener para limpar o banco
    const btnLimparBanco = document.getElementById('btnLimparBanco');
    btnLimparBanco.addEventListener('click', async () => {
        if (confirm('Tem certeza que deseja limpar todo o banco de dados?')) {
            try {
                const response = await fetch('https://max-python.uvxtdw.easypanel.host/limpar-banco', {
                    method: 'POST'
                });
                const data = await response.json();
                alert(data.mensagem);
                carregarTabelas();
            } catch (error) {
                console.error('Erro ao limpar banco:', error);
            }
        }
    });

    // Carregar tabelas inicialmente
    carregarTabelas();
});

// Funções globais
async function verDetalhes(tabela) {
    try {
        const response = await fetch(`https://max-python.uvxtdw.easypanel.host/info-tabela/${tabela}`);
        const data = await response.json();
        
        if (data.status === 'Sucesso') {
            // Preenche a tabela de estrutura
            const estruturaBody = document.querySelector('#estruturaTabela tbody');
            estruturaBody.innerHTML = '';
            data.colunas.forEach(coluna => {
                estruturaBody.innerHTML += `
                    <tr>
                        <td>${coluna.Field}</td>
                        <td>${coluna.Type}</td>
                        <td>${coluna.Null}</td>
                        <td>${coluna.Key}</td>
                        <td>${coluna.Default || ''}</td>
                        <td>${coluna.Extra || ''}</td>
                    </tr>
                `;
            });

            // Preenche a tabela de dados
            const dadosTable = document.querySelector('#dadosTabela');
            if (data.amostra_dados && data.amostra_dados.length > 0) {
                // Cria o cabeçalho
                const headers = Object.keys(data.amostra_dados[0]);
                dadosTable.querySelector('thead').innerHTML = `
                    <tr>
                        ${headers.map(h => `<th>${h}</th>`).join('')}
                    </tr>
                `;

                // Preenche os dados
                dadosTable.querySelector('tbody').innerHTML = data.amostra_dados.map(row => `
                    <tr>
                        ${headers.map(h => `<td>${row[h]}</td>`).join('')}
                    </tr>
                `).join('');
            } else {
                dadosTable.innerHTML = '<tr><td colspan="100%">Nenhum dado encontrado</td></tr>';
            }

            // Abre o modal
            const modal = new bootstrap.Modal(document.getElementById('tabelaDetalhesModal'));
            modal.show();
        }
    } catch (error) {
        console.error('Erro ao ver detalhes:', error);
        alert('Erro ao carregar detalhes da tabela');
    }
}

async function limparTabela(tabela) {
    if (confirm(`Tem certeza que deseja limpar a tabela ${tabela}?`)) {
        try {
            const response = await fetch(`https://max-python.uvxtdw.easypanel.host/limpar-tabela/${tabela}`, {
                method: 'POST'
            });
            const data = await response.json();
            if (data.status === 'Sucesso') {
                alert('Tabela limpa com sucesso!');
                carregarTabelas();
            }
        } catch (error) {
            console.error('Erro ao limpar tabela:', error);
        }
    }
}

async function apagarTabela(tabela) {
    if (confirm(`Tem certeza que deseja apagar a tabela ${tabela}?`)) {
        try {
            const response = await fetch(`https://max-python.uvxtdw.easypanel.host/apagar-tabela/${tabela}`, {
                method: 'GET'
            });
            const data = await response.json();
            if (data.status === 'Sucesso') {
                alert('Tabela apagada com sucesso!');
                carregarTabelas();
            }
        } catch (error) {
            console.error('Erro ao apagar tabela:', error);
        }
    }
}

async function carregarInfoConexao() {
    // Dados de conexão
    const dbConfig = {
        host: 'dbserver.dev.f92a9e36-50c7-46cb-99f1-c31cb3846d61.drush.in',
        port: 12816,
        db: 'pantheon',
        user: 'pantheon'
    };

    // Preenche os campos com as informações
    document.getElementById('dbHost').textContent = dbConfig.host;
    document.getElementById('dbPort').textContent = dbConfig.port;
    document.getElementById('dbName').textContent = dbConfig.db;
    document.getElementById('dbUser').textContent = dbConfig.user;

    // Verifica o status da conexão
    try {
        const response = await fetch('https://max-python.uvxtdw.easypanel.host/listar-tabelas');
        const data = await response.json();
        
        if (data.status === 'Erro') {
            document.getElementById('dbStatus').innerHTML = '<span class="badge bg-danger">Desconectado</span>';
        } else {
            document.getElementById('dbStatus').innerHTML = '<span class="badge bg-success">Conectado</span>';
        }
    } catch (error) {
        document.getElementById('dbStatus').innerHTML = '<span class="badge bg-danger">Desconectado</span>';
        console.error('Erro ao verificar status da conexão:', error);
    }
}