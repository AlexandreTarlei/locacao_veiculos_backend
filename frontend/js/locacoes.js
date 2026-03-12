/**
 * Funções para a tela de Locações - Locação de Veículos
 * API: GET /locacoes/
 */
function carregarLocacoes(apenasAtivas) {
  var url = '/locacoes/';
  if (apenasAtivas) url += '?apenas_ativas=true';
  return getJson(url);
}

function renderListaLocacoes(dados, containerId) {
  var el = document.getElementById(containerId || 'lista');
  if (!el) return;
  if (!dados || dados.length === 0) {
    el.innerHTML = '<p>Nenhuma locação.</p>';
    return;
  }
  el.innerHTML =
    '<table><thead><tr><th>ID</th><th>Cliente</th><th>Veículo</th><th>Início</th><th>Fim</th><th>Dias</th><th>Valor total</th><th>Ativa</th><th>Ações</th></tr></thead><tbody>' +
    dados.map(function (l) {
      var clienteNome = (l.cliente && l.cliente.nome) ? l.cliente.nome : '-';
      var veiculoDesc = (l.veiculo) ? (l.veiculo.marca || '') + ' ' + (l.veiculo.modelo || '') + ' (' + (l.veiculo.placa || '') + ')' : '-';
      var inicio = l.data_inicio ? (typeof l.data_inicio === 'string' ? l.data_inicio.slice(0, 10) : l.data_inicio) : '-';
      var fim = l.data_fim ? (typeof l.data_fim === 'string' ? l.data_fim.slice(0, 10) : l.data_fim) : '-';
      var valor = (l.valor_total != null) ? 'R$ ' + Number(l.valor_total).toFixed(2) : '-';
      var ativa = l.ativa ? 'Sim' : 'Não';
      var btnContrato = '<a href="#" class="btn-contrato" data-id="' + l.id + '" title="Baixar contrato em PDF">Contrato</a>';
      return '<tr><td>' + l.id + '</td><td>' + clienteNome + '</td><td>' + veiculoDesc + '</td><td>' + inicio + '</td><td>' + fim + '</td><td>' + (l.dias || '-') + '</td><td>' + valor + '</td><td>' + ativa + '</td><td>' + btnContrato + '</td></tr>';
    }).join('') +
    '</tbody></table>';
  // Delegar clique nos links de contrato
  el.querySelectorAll('.btn-contrato').forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      var id = parseInt(link.getAttribute('data-id'), 10);
      if (id) baixarContratoLocacao(id);
    });
  });
}

/**
 * Baixa o PDF do contrato de locação (GET /locacoes/{id}/contrato).
 */
function baixarContratoLocacao(locacaoId) {
  fetchApi('/locacoes/' + locacaoId + '/contrato')
    .then(function (res) {
      if (!res.ok) throw new Error('Falha ao gerar contrato');
      return res.blob();
    })
    .then(function (blob) {
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'contrato_locacao_' + locacaoId + '.pdf';
      a.click();
      URL.revokeObjectURL(url);
    })
    .catch(function (err) {
      exibirErroLocacoes(err.message);
    });
}

function exibirErroLocacoes(mensagem, containerId) {
  var el = document.getElementById(containerId || 'erro');
  if (el) el.textContent = mensagem ? 'Erro: ' + mensagem : '';
}
