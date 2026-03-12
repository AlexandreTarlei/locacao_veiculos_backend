/**
 * Configuração e helpers da API - Locação de Veículos
 */
var API_BASE = typeof window !== 'undefined' && window.API_BASE ? window.API_BASE : 'http://localhost:8000';
var TOKEN_KEY = 'token';

/**
 * Retorna o token JWT armazenado (se existir).
 */
function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Faz requisição à API com header Authorization quando houver token.
 * @param {string} url - Caminho relativo (ex: '/clientes/')
 * @param {RequestInit} options - Opções do fetch (method, body, headers...)
 * @returns {Promise<Response>}
 */
function fetchApi(url, options) {
  options = options || {};
  var headers = options.headers || {};
  if (typeof headers.append === 'undefined' && typeof Headers === 'undefined') {
    headers = new Object(headers);
  }
  var h = new Headers(headers);
  var token = getToken();
  if (token) {
    h.set('Authorization', 'Bearer ' + token);
  }
  if (!h.has('Content-Type') && options.body && typeof options.body === 'string') {
    h.set('Content-Type', 'application/json');
  }
  options.headers = h;
  return fetch(API_BASE + url, options);
}

/**
 * Faz GET e retorna JSON.
 */
function getJson(url) {
  return fetchApi(url).then(function (res) {
    return res.json().then(function (data) {
      if (!res.ok) {
        var msg = (data && data.detail) ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : res.statusText;
        throw new Error(msg);
      }
      return data;
    });
  });
}

/**
 * Faz POST com body JSON e retorna JSON.
 */
function postJson(url, body) {
  return fetchApi(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(function (res) {
    return res.json().then(function (data) {
      if (!res.ok) {
        var msg = (data && data.detail) ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : res.statusText;
        throw new Error(msg);
      }
      return data;
    });
  });
}

/**
 * Faz PUT com body JSON e retorna JSON.
 */
function putJson(url, body) {
  return fetchApi(url, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(function (res) {
    return res.json().then(function (data) {
      if (!res.ok) {
        var msg = (data && data.detail) ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : res.statusText;
        throw new Error(msg);
      }
      return data;
    });
  });
}

/**
 * Faz DELETE.
 */
function deleteApi(url) {
  return fetchApi(url, { method: 'DELETE' }).then(function (res) {
    if (res.status === 204) return;
    return res.json().then(function (data) {
      if (!res.ok) {
        var msg = (data && data.detail) ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : res.statusText;
        throw new Error(msg);
      }
    });
  });
}
