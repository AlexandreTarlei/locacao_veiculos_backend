/**
 * Funções para listagem de Veículos - Locação de Veículos
 * API: GET /veiculos/ (prefixo já em api.js)
 */
function carregarVeiculos(apenasDisponiveis) {
  var url = '/veiculos/';
  if (apenasDisponiveis) url += '?apenas_disponiveis=true';
  return getJson(url);
}

function renderListaVeiculos(dados, containerId) {
  var el = document.getElementById(containerId || 'lista');
  if (!el) return;
  if (!dados || dados.length === 0) {
    el.innerHTML = '<p>Nenhum veículo cadastrado.</p>';
    return;
  }
  el.innerHTML =
    '<table><thead><tr><th>ID</th><th>Placa</th><th>Marca</th><th>Modelo</th><th>Ano</th><th>Cor</th><th>Valor/dia</th><th>Disponível</th></tr></thead><tbody>' +
    dados.map(function (v) {
      var disp = v.disponivel ? 'Sim' : 'Não';
      var valor = (v.valor_diaria != null) ? 'R$ ' + Number(v.valor_diaria).toFixed(2) : '-';
      return '<tr><td>' + v.id + '</td><td>' + (v.placa || '') + '</td><td>' + (v.marca || '') + '</td><td>' + (v.modelo || '') + '</td><td>' + (v.ano || '') + '</td><td>' + (v.cor || '') + '</td><td>' + valor + '</td><td>' + disp + '</td></tr>';
    }).join('') +
    '</tbody></table>';
}

function exibirErroVeiculos(mensagem, containerId) {
  var el = document.getElementById(containerId || 'erro');
  if (el) el.textContent = mensagem ? 'Erro: ' + mensagem : '';
}
