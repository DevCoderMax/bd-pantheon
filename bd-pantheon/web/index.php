<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gerenciador de Banco de Dados</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <i class="bi bi-database"></i>
            <span>DB Manager</span>
        </div>
        <div class="menu">
            <button id="btnListarTabelas" class="menu-item active">
                <i class="bi bi-table"></i>Tabelas
            </button>
            <button id="btnCriarTabela" class="menu-item">
                <i class="bi bi-plus-circle"></i>Nova Tabela
            </button>
            <button id="btnExecutarSQL" class="menu-item">
                <i class="bi bi-code-slash"></i>Executar SQL
            </button>
            <button id="btnLimparBanco" class="menu-item">
                <i class="bi bi-trash"></i> Limpar Banco
            </button>
        </div>
    </div>

    <div class="main-content">
        <div id="tabelasView" class="content-section">
            <h2>Tabelas do Banco</h2>
            <div id="listaTabelas" class="table-list"></div>
        </div>

        <div id="criarTabelaView" class="content-section hidden">
            <h2>Criar Nova Tabela</h2>
            <form id="formCriarTabela">
                <div class="mb-3">
                    <input type="text" class="form-control" id="nomeTabela" placeholder="Nome da Tabela">
                </div>
                <div id="colunasContainer">
                    <!-- Colunas serão adicionadas aqui dinamicamente -->
                </div>
                <button type="button" class="btn btn-secondary" id="btnAddColuna">
                    <i class="bi bi-plus"></i> Adicionar Coluna
                </button>
                <button type="submit" class="btn btn-primary">Criar Tabela</button>
            </form>
        </div>

        <div id="executarSQLView" class="content-section hidden">
            <h2>Executar SQL</h2>
            <div class="sql-editor">
                <textarea id="sqlQuery" class="form-control" rows="5" placeholder="Digite seu comando SQL aqui..."></textarea>
                <button id="btnExecutar" class="btn btn-primary mt-2">Executar</button>
            </div>
            <div id="resultadoSQL" class="mt-3"></div>
        </div>
    </div>

    <!-- Modal de Detalhes da Tabela -->
    <div class="modal fade" id="tabelaDetalhesModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Detalhes da Tabela</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <h6>Estrutura da Tabela</h6>
                    <div class="table-responsive">
                        <table class="table" id="estruturaTabela">
                            <thead>
                                <tr>
                                    <th>Campo</th>
                                    <th>Tipo</th>
                                    <th>Nulo</th>
                                    <th>Chave</th>
                                    <th>Padrão</th>
                                    <th>Extra</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                    <h6 class="mt-4">Amostra de Dados</h6>
                    <div class="table-responsive">
                        <table class="table" id="dadosTabela">
                            <thead></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="script.js"></script>
</body>
</html>
