/**
 * Reservas por período - checagem de disponibilidade e criação.
 * API: GET/POST /reservas/, GET /reservas/disponibilidade
 */
function carregarReservas(filtros) {
  var url = '/reservas/';
  var params = [];
  if (filtros && filtros.veiculo_id) params.push('veiculo_id=' + filtros.veiculo_id);
  if (filtros && filtros.cliente_id) params.push('cliente_id=' + filtros.cliente_id);
  if (filtros && filtros.data_inicio) params.push('data_inicio=' + filtros.data_inicio);
  if (filtros && filtros.data_fim) params.push('data_fim=' + filtros.data_fim);
  if (params.length) url += '?' + params.join('&');
  return getJson(url);
}

function carregarClientesParaSelect() {
  return getJson('/clientes/');
}

function carregarVeiculosParaSelect() {
  return getJson('/veiculos/');
}

function checarDisponibilidade(veiculoId, dataInicio, dataFim) {
  var url = '/reservas/disponibilidade?veiculo_id=' + encodeURIComponent(veiculoId) +
    '&data_inicio=' + encodeURIComponent(dataInicio) +
    '&data_fim=' + encodeURIComponent(dataFim);
  return getJson(url);
}

function criarReserva(payload) {
  return postJson('/reservas/', payload);
}

function excluirReserva(id) {
  return deleteApi('/reservas/' + id);
}

function criarContrato(payload) {
  return postJson('/contratos/', payload);
}

function baixarPdfContrato(contratoId) {
  fetchApi('/contratos/' + contratoId + '/pdf')
    .then(function (res) {
      if (!res.ok) throw new Error('Falha ao gerar PDF do contrato');
      return res.blob();
    })
    .then(function (blob) {
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'contrato_' + contratoId + '.pdf';
      a.click();
      URL.revokeObjectURL(url);
    })
    .catch(function (err) {
      if (typeof exibirErroReservas === 'function') exibirErroReservas(err.message);
    });
}

function formatarData(s) {
  if (!s) return '-';
  if (typeof s === 'string' && s.length >= 10) return s.slice(0, 10);
  return s;
}

function renderListaReservas(dados, containerId) {
  var el = document.getElementById(containerId || 'listaReservas');
  if (!el) return;
  if (!dados || dados.length === 0) {
    el.innerHTML = '<p>Nenhuma reserva cadastrada.</p>';
    return;
  }
  el.innerHTML =
    '<table><thead><tr><th>ID</th><th>Cliente</th><th>Veículo</th><th>Início</th><th>Fim</th><th>Status</th><th>Ações</th></tr></thead><tbody>' +
    dados.map(function (r) {
      var clienteId = r.cliente_id;
      var veiculoId = r.veiculo_id;
      var btnContrato = '<button type="button" class="btn-gerar-contrato" data-reserva-id="' + r.id + '" data-cliente-id="' + clienteId + '" data-veiculo-id="' + veiculoId + '">Gerar contrato</button>';
      return '<tr><td>' + r.id + '</td><td data-cliente-id="' + clienteId + '">-</td><td data-veiculo-id="' + veiculoId + '">-</td><td>' + formatarData(r.data_inicio) + '</td><td>' + formatarData(r.data_fim) + '</td><td>' + (r.status || 'reservado') + '</td><td>' + btnContrato + '</td></tr>';
    }).join('') +
    '</tbody></table>';
  preencherNomesReservas(dados, el);
  el.querySelectorAll('.btn-gerar-contrato').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var reservaId = parseInt(btn.getAttribute('data-reserva-id'), 10);
      var clienteId = parseInt(btn.getAttribute('data-cliente-id'), 10);
      var veiculoId = parseInt(btn.getAttribute('data-veiculo-id'), 10);
      if (typeof onGerarContratoClick === 'function') {
        onGerarContratoClick({ reserva_id: reservaId, cliente_id: clienteId, veiculo_id: veiculoId });
      }
    });
  });
}

function preencherNomesReservas(reservas, tableEl) {
  if (!reservas.length) return;
  var clienteIds = reservas.map(function (r) { return r.cliente_id; }).filter(function (id, i, a) { return a.indexOf(id) === i; });
  var veiculoIds = reservas.map(function (r) { return r.veiculo_id; }).filter(function (id, i, a) { return a.indexOf(id) === i; });
  Promise.all([carregarClientesParaSelect(), carregarVeiculosParaSelect()])
    .then(function (results) {
      var clientes = results[0] || [];
      var veiculos = results[1] || [];
      var clienteMap = {};
      clientes.forEach(function (c) { clienteMap[c.id] = c.nome || '-'; });
      var veiculoMap = {};
      veiculos.forEach(function (v) {
        var desc = (v.placa || '') + ' ' + (v.marca_nome || v.marca || '') + ' ' + (v.modelo_nome || v.modelo || '');
        veiculoMap[v.id] = desc.trim() || '-';
      });
      tableEl.querySelectorAll('[data-cliente-id]').forEach(function (cell) {
        var id = parseInt(cell.getAttribute('data-cliente-id'), 10);
        cell.textContent = clienteMap[id] || '-';
      });
      tableEl.querySelectorAll('[data-veiculo-id]').forEach(function (cell) {
        var id = parseInt(cell.getAttribute('data-veiculo-id'), 10);
        cell.textContent = veiculoMap[id] || '-';
      });
    })
    .catch(function () {});
}

function exibirErroReservas(mensagem, containerId) {
  var el = document.getElementById(containerId || 'erroReservas');
  if (el) el.textContent = mensagem ? 'Erro: ' + mensagem : '';
}

function exibirMsgReservas(mensagem, ehErro, containerId) {
  var el = document.getElementById(containerId || 'msgReservas');
  if (!el) return;
  el.textContent = mensagem || '';
  el.className = ehErro ? 'erro' : 'sucesso';
}
