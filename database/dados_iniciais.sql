-- Dados iniciais para o banco locacao_veiculos
-- Executar após schema.sql: mysql -u root -p locacao_veiculos < database/dados_iniciais.sql
-- O usuário admin (admin@admin.com / senha: admin) é criado pelo backend na primeira subida (seed_usuarios).

SET NAMES utf8mb4;

-- ------------------------------------------------------
-- Formas de pagamento
-- ------------------------------------------------------
INSERT IGNORE INTO `formas_pagamento` (`nome`, `descricao`, `ativa`) VALUES
('PIX', 'Pagamento instantâneo via PIX', 1),
('Cartão de crédito', 'Cartão de crédito à vista ou parcelado', 1),
('Cartão de débito', 'Cartão de débito', 1),
('Dinheiro', 'Pagamento em espécie', 1),
('Boleto bancário', 'Boleto bancário', 1),
('Transferência bancária', 'Transferência TED/DOC', 1),
('Cheque', 'Pagamento com cheque', 1),
('Vale/cupom', 'Vale ou cupom de desconto', 1);

-- ------------------------------------------------------
-- Plano de contas (módulo financeiro)
-- ------------------------------------------------------
INSERT IGNORE INTO `plano_contas` (`id`, `nome`) VALUES
(1, 'Receitas'),
(2, 'Despesas'),
(3, 'Vendas'),
(4, 'Combustível'),
(5, 'Manutenção'),
(6, 'Outros');

-- Usuário admin: criado automaticamente pelo backend (main.py/app.py) na primeira subida
-- com email admin@admin.com e senha "admin" (bcrypt). Não é inserido aqui para evitar
-- armazenar hash em repositório; use seed_usuarios() no startup da API.
