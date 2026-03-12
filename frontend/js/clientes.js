/**
 * Funções para a tela de Clientes - Locação de Veículos
 * Depende de api.js (getJson, postJson, putJson, deleteApi)
 */
function carregarClientes() {
  return getJson('/clientes/');
}

function renderListaClientes(dados, containerId) {
  var el = document.getElementById(containerId || 'lista');
  if (!el) return;
  if (!dados || dados.length === 0) {
    el.innerHTML = '<p>Nenhum cliente cadastrado.</p>';
    return;
  }
  el.innerHTML =
    '<table><thead><tr><th>ID</th><th>Nome</th><th>CPF</th><th>Telefone</th><th>E-mail</th></tr></thead><tbody>' +
    dados.map(function (c) {
      return '<tr><td>' + c.id + '</td><td>' + (c.nome || '') + '</td><td>' + (c.cpf || '') + '</td><td>' + (c.telefone || '') + '</td><td>' + (c.email || '') + '</td></tr>';
    }).join('') +
    '</tbody></table>';
}

function exibirErroClientes(mensagem, containerId) {
  var el = document.getElementById(containerId || 'erro');
  if (el) el.textContent = mensagem ? 'Erro: ' + mensagem : '';
}
