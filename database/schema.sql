-- Schema do banco locacao_veiculos (MariaDB/MySQL 8.0.16+ para CHECK constraints)
-- Fonte de verdade para deploy e documentação.
-- Uso: mysql -u root -p < database/schema.sql (criar banco antes: CREATE DATABASE locacao_veiculos;)
--
-- Perfis de usuário (admin, gerente, operador): tabela tipo_usuario com códigos
-- ADMIN (Administrador), GERENTE (Gerente), OPERACIONAL (Operador). O perfil
-- do usuário é definido por usuarios.id_tipo_usuario (FK para tipo_usuario).

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Remover views e tabelas em ordem de dependência (evitar erro de FK)
DROP VIEW IF EXISTS `vw_faturamento_mensal`;
DROP VIEW IF EXISTS `vw_locacoes_ativas`;
DROP VIEW IF EXISTS `vw_historico_locacoes`;
DROP TABLE IF EXISTS `pagamentos`;
DROP TABLE IF EXISTS `locacoes`;
DROP TABLE IF EXISTS `contratos`;
DROP TABLE IF EXISTS `reservas`;
DROP TABLE IF EXISTS `lancamentos_financeiros`;
DROP TABLE IF EXISTS `plano_contas`;
DROP TABLE IF EXISTS `formas_pagamento`;
DROP TABLE IF EXISTS `clientes`;
DROP TABLE IF EXISTS `manutencoes`;
DROP TABLE IF EXISTS `manutencao_programada`;
DROP TABLE IF EXISTS `veiculos`;
DROP TABLE IF EXISTS `modelos_veiculos`;
DROP TABLE IF EXISTS `marcas_veiculos`;
DROP TABLE IF EXISTS `empresa`;
DROP TABLE IF EXISTS `notificacoes`;
DROP TABLE IF EXISTS `usuarios`;
DROP TABLE IF EXISTS `tipo_usuario`;

-- ------------------------------------------------------
-- Tabela: tipo_usuario
-- Perfis do sistema: admin (ADMIN), gerente (GERENTE), operador (OPERACIONAL).
-- Código usado na aplicação; nome é o texto exibido na UI.
-- ------------------------------------------------------
CREATE TABLE `tipo_usuario` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(20) NOT NULL,
  `nome` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `ix_tipo_usuario_codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tipos de usuário: Administrador, Gerente, Operador (admin/gerente/operador)';

INSERT INTO `tipo_usuario` (`codigo`, `nome`) VALUES
  ('ADMIN', 'Administrador'),
  ('GERENTE', 'Gerente'),
  ('OPERACIONAL', 'Operador');

-- ------------------------------------------------------
-- Tabela: usuarios
-- Perfil preferido via id_tipo_usuario (FK). Coluna nivel é legado; manter para compatibilidade.
-- email e senha NOT NULL (obrigatórios para login). Auditoria: created_at, updated_at, ultimo_login.
-- ------------------------------------------------------
CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `senha` varchar(255) NOT NULL,
  `id_tipo_usuario` int(11) DEFAULT NULL,
  `nivel` varchar(20) DEFAULT NULL COMMENT 'Legado; preferir id_tipo_usuario',
  `ativo` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Data de criação do usuário',
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Última atualização',
  `ultimo_login` datetime DEFAULT NULL COMMENT 'Último login (preenchido no endpoint de login)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_usuarios_email` (`email`),
  KEY `ix_usuarios_id_tipo_usuario` (`id_tipo_usuario`),
  CONSTRAINT `fk_usuarios_tipo` FOREIGN KEY (`id_tipo_usuario`) REFERENCES `tipo_usuario` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Usuários do sistema (login e perfil). Perfis: admin, gerente, operador via tipo_usuario.';

-- ------------------------------------------------------
-- Tabela: notificacoes
-- Notificações por usuário (status: nao_lida, lida, arquivada).
-- status como ENUM garante domínio no BD; índice (id_usuario, status) otimiza listagem por usuário + filtro.
-- ------------------------------------------------------
CREATE TABLE `notificacoes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `titulo` varchar(200) NOT NULL,
  `mensagem` text DEFAULT NULL,
  `status` enum('nao_lida','lida','arquivada') NOT NULL DEFAULT 'nao_lida',
  `data_notificacao` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_notificacoes_id_usuario` (`id_usuario`),
  KEY `ix_notificacoes_status` (`status`),
  KEY `ix_notificacoes_data` (`data_notificacao`),
  KEY `ix_notificacoes_usuario_status` (`id_usuario`, `status`),
  CONSTRAINT `fk_notificacoes_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Notificações por usuário (status: nao_lida, lida, arquivada)';

-- ------------------------------------------------------
-- Tabela: empresa
-- Dados da empresa para o menu Configurações (nome, CNPJ, endereço, etc.).
-- ------------------------------------------------------
CREATE TABLE `empresa` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome_fantasia` varchar(150) DEFAULT NULL,
  `razao_social` varchar(200) DEFAULT NULL,
  `cnpj` varchar(18) DEFAULT NULL,
  `endereco` varchar(300) DEFAULT NULL,
  `telefone` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `data_atualizacao` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Dados da empresa (configurações)';

INSERT INTO `empresa` (`id`, `nome_fantasia`, `razao_social`) VALUES (1, '', '');

-- ------------------------------------------------------
-- Tabela: marcas_veiculos
-- ------------------------------------------------------
CREATE TABLE `marcas_veiculos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nome` (`nome`),
  KEY `ix_marcas_veiculos_nome` (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Marcas de veículos (ex.: Fiat, Volkswagen)';

-- ------------------------------------------------------
-- Tabela: modelos_veiculos
-- ------------------------------------------------------
CREATE TABLE `modelos_veiculos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_marca` int(11) NOT NULL,
  `nome` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_modelos_veiculos_id_marca` (`id_marca`),
  KEY `ix_modelos_veiculos_nome` (`nome`),
  CONSTRAINT `fk_modelos_veiculos_marca` FOREIGN KEY (`id_marca`) REFERENCES `marcas_veiculos` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Modelos de veículos por marca';

-- ------------------------------------------------------
-- Tabela: veiculos
-- ------------------------------------------------------
CREATE TABLE `veiculos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `placa` varchar(10) NOT NULL,
  `id_modelo` int(11) DEFAULT NULL,
  `marca` varchar(50) DEFAULT NULL COMMENT 'Legado: preenchido se id_modelo for NULL',
  `modelo` varchar(50) DEFAULT NULL COMMENT 'Legado: preenchido se id_modelo for NULL',
  `ano` int(11) NOT NULL,
  `cor` varchar(30) NOT NULL,
  `quilometragem` decimal(10,2) NOT NULL DEFAULT 0.00,
  `valor_diaria` decimal(10,2) NOT NULL,
  `disponivel` tinyint(1) NOT NULL DEFAULT 1,
  `fotos_json` text DEFAULT NULL COMMENT 'JSON com URLs ou paths das fotos do veículo',
  `data_cadastro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `data_atualizacao` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `placa` (`placa`),
  KEY `idx_veiculos_placa` (`placa`),
  KEY `idx_veiculos_disponivel` (`disponivel`),
  KEY `ix_veiculos_id_modelo` (`id_modelo`),
  CONSTRAINT `fk_veiculos_modelo` FOREIGN KEY (`id_modelo`) REFERENCES `modelos_veiculos` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `chk_veiculos_valor_diaria` CHECK (`valor_diaria` >= 0),
  CONSTRAINT `chk_veiculos_quilometragem` CHECK (`quilometragem` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Frota de veículos disponíveis para locação';

-- ------------------------------------------------------
-- Tabela: manutencao_programada
-- Agendamentos por quilometragem e/ou data limite (alertas de manutenção futura).
-- ------------------------------------------------------
CREATE TABLE `manutencao_programada` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_veiculo` int(11) NOT NULL,
  `tipo_manutencao` varchar(100) NOT NULL,
  `quilometragem_limite` int(11) DEFAULT NULL,
  `data_limite` date DEFAULT NULL,
  `ativa` tinyint(1) NOT NULL DEFAULT 1,
  `data_cadastro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `data_atualizacao` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_manutencao_programada_id_veiculo` (`id_veiculo`),
  KEY `idx_manutencao_programada_veiculo_data` (`id_veiculo`, `data_limite`),
  CONSTRAINT `fk_manutencao_programada_veiculo` FOREIGN KEY (`id_veiculo`) REFERENCES `veiculos` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_manutencao_programada_limite` CHECK (`quilometragem_limite` IS NOT NULL OR `data_limite` IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Manutenções programadas por veículo (km e/ou data limite)';

-- ------------------------------------------------------
-- Tabela: manutencoes
-- Registros de gastos/manutenção por veículo (usado no dashboard e relatórios).
-- No frontend locacao_veiculos.html hoje isso fica só no localStorage; com esta tabela a API pode persistir e servir.
-- ------------------------------------------------------
CREATE TABLE `manutencoes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_veiculo` int(11) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  `valor` decimal(10,2) NOT NULL DEFAULT 0.00,
  `data_manutencao` date NOT NULL,
  `data_cadastro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_manutencoes_id_veiculo` (`id_veiculo`),
  KEY `idx_manutencoes_data` (`data_manutencao`),
  CONSTRAINT `fk_manutencoes_veiculo` FOREIGN KEY (`id_veiculo`) REFERENCES `veiculos` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_manutencoes_valor` CHECK (`valor` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Registros de manutenção/gastos por veículo (dashboard e relatórios)';

-- ------------------------------------------------------
-- Tabela: clientes
-- ------------------------------------------------------
CREATE TABLE `clientes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `cpf` varchar(14) NOT NULL,
  `telefone` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL,
  `cep` varchar(10) NOT NULL,
  `endereco` varchar(200) NOT NULL,
  `data_nascimento` datetime DEFAULT NULL,
  `data_cadastro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cpf` (`cpf`),
  KEY `idx_clientes_cpf` (`cpf`),
  KEY `idx_clientes_nome` (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Clientes cadastrados para locação';

-- ------------------------------------------------------
-- Tabela: reservas
-- Período reservado antes da locação efetiva. Evita double-booking por overlap de datas.
-- ------------------------------------------------------
CREATE TABLE `reservas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `empresa_id` int(11) DEFAULT NULL,
  `cliente_id` int(11) NOT NULL,
  `veiculo_id` int(11) NOT NULL,
  `data_inicio` date NOT NULL,
  `data_fim` date NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'reservado',
  PRIMARY KEY (`id`),
  KEY `idx_reservas_empresa` (`empresa_id`),
  KEY `idx_reservas_cliente` (`cliente_id`),
  KEY `idx_reservas_veiculo` (`veiculo_id`),
  KEY `idx_reservas_datas` (`data_inicio`, `data_fim`),
  KEY `idx_reservas_veiculo_status` (`veiculo_id`, `status`),
  CONSTRAINT `fk_reservas_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_reservas_veiculo` FOREIGN KEY (`veiculo_id`) REFERENCES `veiculos` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_reservas_datas` CHECK (`data_fim` >= `data_inicio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Reservas de veículos por período (status reservado/confirmado bloqueiam o veículo)';

-- ------------------------------------------------------
-- Tabela: contratos
-- Contrato de locação (valores, status); pode vincular a uma reserva.
-- ------------------------------------------------------
CREATE TABLE `contratos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `empresa_id` int(11) DEFAULT NULL,
  `reserva_id` int(11) DEFAULT NULL,
  `cliente_id` int(11) NOT NULL,
  `veiculo_id` int(11) NOT NULL,
  `valor_diaria` decimal(10,2) DEFAULT NULL,
  `valor_total` decimal(10,2) DEFAULT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'ativo',
  `data_contrato` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_contratos_empresa` (`empresa_id`),
  KEY `idx_contratos_reserva` (`reserva_id`),
  KEY `idx_contratos_cliente` (`cliente_id`),
  KEY `idx_contratos_veiculo` (`veiculo_id`),
  KEY `idx_contratos_status` (`status`),
  CONSTRAINT `fk_contratos_reserva` FOREIGN KEY (`reserva_id`) REFERENCES `reservas` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_contratos_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_contratos_veiculo` FOREIGN KEY (`veiculo_id`) REFERENCES `veiculos` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_contratos_valor_total` CHECK (`valor_total` IS NULL OR `valor_total` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Contratos de locação (vinculados opcionalmente a reserva; valor_total = valor_diaria * dias)';

-- ------------------------------------------------------
-- Tabela: formas_pagamento
-- ------------------------------------------------------
CREATE TABLE `formas_pagamento` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(50) NOT NULL,
  `descricao` varchar(200) DEFAULT NULL,
  `ativa` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nome` (`nome`),
  KEY `idx_formas_pagamento_nome` (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Formas de pagamento (dinheiro, cartão, PIX, etc.)';

-- ------------------------------------------------------
-- Tabela: locacoes
-- ------------------------------------------------------
CREATE TABLE `locacoes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_cliente` int(11) NOT NULL,
  `id_veiculo` int(11) NOT NULL,
  `data_inicio` datetime NOT NULL,
  `data_fim` datetime NOT NULL,
  `dias` int(11) NOT NULL,
  `valor_total` decimal(10,2) NOT NULL,
  `multa_atraso` decimal(10,2) NOT NULL DEFAULT 0.00 COMMENT 'Valor da multa por atraso na devolução',
  `ativa` tinyint(1) NOT NULL DEFAULT 1,
  `observacoes` text DEFAULT NULL COMMENT 'Observações livres sobre a locação',
  PRIMARY KEY (`id`),
  KEY `idx_locacoes_id_cliente` (`id_cliente`),
  KEY `idx_locacoes_id_veiculo` (`id_veiculo`),
  KEY `idx_locacoes_data_inicio` (`data_inicio`),
  KEY `idx_locacoes_ativa` (`ativa`),
  KEY `idx_locacoes_cliente_ativa` (`id_cliente`, `ativa`),
  KEY `idx_locacoes_veiculo_ativa` (`id_veiculo`, `ativa`),
  CONSTRAINT `fk_locacoes_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_locacoes_veiculo` FOREIGN KEY (`id_veiculo`) REFERENCES `veiculos` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_locacoes_dias` CHECK (`dias` > 0),
  CONSTRAINT `chk_locacoes_valor_total` CHECK (`valor_total` >= 0),
  CONSTRAINT `chk_locacoes_datas` CHECK (`data_fim` >= `data_inicio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Contratos de locação de veículos';

-- ------------------------------------------------------
-- Tabela: pagamentos
-- ------------------------------------------------------
CREATE TABLE `pagamentos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_locacao` int(11) NOT NULL,
  `id_forma_pagamento` int(11) NOT NULL,
  `valor_pagamento` decimal(10,2) NOT NULL,
  `data_pagamento` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `numero_comprovante` varchar(50) DEFAULT NULL,
  `observacoes` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_pagamentos_id_locacao` (`id_locacao`),
  KEY `idx_pagamentos_data` (`data_pagamento`),
  KEY `idx_pagamentos_locacao_data` (`id_locacao`, `data_pagamento`),
  CONSTRAINT `fk_pagamentos_locacao` FOREIGN KEY (`id_locacao`) REFERENCES `locacoes` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_pagamentos_forma` FOREIGN KEY (`id_forma_pagamento`) REFERENCES `formas_pagamento` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_pagamentos_valor` CHECK (`valor_pagamento` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Pagamentos realizados por locação';

-- ------------------------------------------------------
-- Tabela: plano_contas
-- ------------------------------------------------------
CREATE TABLE `plano_contas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Plano de contas para lançamentos financeiros';

-- ------------------------------------------------------
-- Tabela: lancamentos_financeiros
-- ------------------------------------------------------
CREATE TABLE `lancamentos_financeiros` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `descricao` varchar(255) NOT NULL,
  `valor` decimal(10,2) NOT NULL,
  `data_lancamento` date NOT NULL,
  `data_vencimento` date DEFAULT NULL,
  `data_pagamento` date DEFAULT NULL,
  `tipo` varchar(20) NOT NULL COMMENT 'Ex.: receita, despesa',
  `id_plano_conta` int(11) NOT NULL,
  `id_forma_pagamento` int(11) NOT NULL,
  `id_locacao` int(11) DEFAULT NULL COMMENT 'Opcional: vincula lançamento a uma locação',
  `id_pagamento` int(11) DEFAULT NULL COMMENT 'Opcional: vincula lançamento a um pagamento',
  `pago` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_lancamentos_data` (`data_lancamento`),
  KEY `idx_lancamentos_tipo` (`tipo`),
  KEY `idx_lancamentos_plano_conta` (`id_plano_conta`),
  KEY `idx_lancamentos_id_locacao` (`id_locacao`),
  KEY `idx_lancamentos_id_pagamento` (`id_pagamento`),
  CONSTRAINT `fk_lancamentos_plano_conta` FOREIGN KEY (`id_plano_conta`) REFERENCES `plano_contas` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_lancamentos_forma_pagamento` FOREIGN KEY (`id_forma_pagamento`) REFERENCES `formas_pagamento` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_lancamentos_locacao` FOREIGN KEY (`id_locacao`) REFERENCES `locacoes` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_lancamentos_pagamento` FOREIGN KEY (`id_pagamento`) REFERENCES `pagamentos` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `chk_lancamentos_valor` CHECK (`valor` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Lançamentos financeiros (receitas e despesas)';

-- ------------------------------------------------------
-- Views (com JOIN em marcas_veiculos e modelos_veiculos)
-- ------------------------------------------------------
CREATE VIEW `vw_locacoes_ativas` AS
SELECT l.id, l.id_cliente, l.id_veiculo, l.data_inicio, l.data_fim, l.dias, l.valor_total, l.ativa,
       c.nome AS cliente_nome, c.cpf AS cliente_cpf,
       v.placa AS veiculo_placa,
       COALESCE(mkv.nome, v.marca) AS veiculo_marca,
       COALESCE(mv.nome, v.modelo) AS veiculo_modelo
FROM locacoes l
JOIN clientes c ON c.id = l.id_cliente
JOIN veiculos v ON v.id = l.id_veiculo
LEFT JOIN modelos_veiculos mv ON v.id_modelo = mv.id
LEFT JOIN marcas_veiculos mkv ON mv.id_marca = mkv.id
WHERE l.ativa = 1;

CREATE VIEW `vw_historico_locacoes` AS
SELECT l.id, l.id_cliente, l.id_veiculo, l.data_inicio, l.data_fim, l.dias, l.valor_total, l.ativa,
       c.nome AS cliente_nome,
       v.placa AS veiculo_placa,
       COALESCE(mkv.nome, v.marca) AS veiculo_marca,
       COALESCE(mv.nome, v.modelo) AS veiculo_modelo
FROM locacoes l
JOIN clientes c ON c.id = l.id_cliente
JOIN veiculos v ON v.id = l.id_veiculo
LEFT JOIN modelos_veiculos mv ON v.id_modelo = mv.id
LEFT JOIN marcas_veiculos mkv ON mv.id_marca = mkv.id;

-- Faturamento por mês (soma de pagamentos recebidos) para dashboard e relatórios.
CREATE VIEW `vw_faturamento_mensal` AS
SELECT
  YEAR(`data_pagamento`) AS `ano`,
  MONTH(`data_pagamento`) AS `mes`,
  COALESCE(SUM(`valor_pagamento`), 0) AS `faturamento`
FROM `pagamentos`
GROUP BY YEAR(`data_pagamento`), MONTH(`data_pagamento`);

SET FOREIGN_KEY_CHECKS = 1;
