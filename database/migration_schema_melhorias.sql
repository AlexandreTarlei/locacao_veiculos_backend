-- Migração para bancos existentes: aplica melhorias do schema (índices, CHECKs, nomenclatura e rastreabilidade).
-- Requer MySQL 8.0.16+ para CHECK constraints. Execute após backup: mysql -u root -p locacao_veiculos < database/migration_schema_melhorias.sql
-- Se a tabela lancamentos_financeiros já tiver id_plano_conta/id_forma_pagamento, pule o bloco de RENAME (ou adapte).

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------------
-- 1. Índices compostos (locacoes e pagamentos)
-- ---------------------------------------------------------------------------
ALTER TABLE `locacoes`
  ADD KEY `idx_locacoes_cliente_ativa` (`id_cliente`, `ativa`),
  ADD KEY `idx_locacoes_veiculo_ativa` (`id_veiculo`, `ativa`);

ALTER TABLE `pagamentos`
  ADD KEY `idx_pagamentos_locacao_data` (`id_locacao`, `data_pagamento`);

-- Se der erro "Duplicate key name", os índices já existem; pode ignorar.

-- ---------------------------------------------------------------------------
-- 2. CHECK constraints (MySQL 8.0.16+)
-- ---------------------------------------------------------------------------
ALTER TABLE `veiculos`
  ADD CONSTRAINT `chk_veiculos_valor_diaria` CHECK (`valor_diaria` >= 0),
  ADD CONSTRAINT `chk_veiculos_quilometragem` CHECK (`quilometragem` >= 0);

ALTER TABLE `locacoes`
  ADD CONSTRAINT `chk_locacoes_dias` CHECK (`dias` > 0),
  ADD CONSTRAINT `chk_locacoes_valor_total` CHECK (`valor_total` >= 0),
  ADD CONSTRAINT `chk_locacoes_datas` CHECK (`data_fim` >= `data_inicio`);

ALTER TABLE `pagamentos`
  ADD CONSTRAINT `chk_pagamentos_valor` CHECK (`valor_pagamento` > 0);

-- Se alguma constraint já existir, remova-a antes ou ignore o erro.

-- ---------------------------------------------------------------------------
-- 3. lancamentos_financeiros: colunas de rastreabilidade
-- ---------------------------------------------------------------------------
ALTER TABLE `lancamentos_financeiros`
  ADD COLUMN `id_locacao` int(11) DEFAULT NULL COMMENT 'Opcional: vincula lançamento a uma locação' AFTER `forma_pagamento_id`,
  ADD COLUMN `id_pagamento` int(11) DEFAULT NULL COMMENT 'Opcional: vincula lançamento a um pagamento' AFTER `id_locacao`;

ALTER TABLE `lancamentos_financeiros`
  ADD KEY `idx_lancamentos_id_locacao` (`id_locacao`),
  ADD KEY `idx_lancamentos_id_pagamento` (`id_pagamento`),
  ADD CONSTRAINT `fk_lancamentos_locacao` FOREIGN KEY (`id_locacao`) REFERENCES `locacoes` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_lancamentos_pagamento` FOREIGN KEY (`id_pagamento`) REFERENCES `pagamentos` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE `lancamentos_financeiros`
  ADD CONSTRAINT `chk_lancamentos_valor` CHECK (`valor` >= 0);

-- ---------------------------------------------------------------------------
-- 4. lancamentos_financeiros: renomear plano_conta_id e forma_pagamento_id
--    (só execute se a tabela ainda tiver colunas plano_conta_id / forma_pagamento_id)
-- ---------------------------------------------------------------------------
-- Remover FKs que usam as colunas antigas
ALTER TABLE `lancamentos_financeiros`
  DROP FOREIGN KEY `fk_lancamentos_plano_conta`,
  DROP FOREIGN KEY `fk_lancamentos_forma_pagamento`;

-- Renomear colunas
ALTER TABLE `lancamentos_financeiros`
  CHANGE COLUMN `plano_conta_id` `id_plano_conta` int(11) NOT NULL,
  CHANGE COLUMN `forma_pagamento_id` `id_forma_pagamento` int(11) NOT NULL;

-- Recriar FKs
ALTER TABLE `lancamentos_financeiros`
  ADD CONSTRAINT `fk_lancamentos_plano_conta` FOREIGN KEY (`id_plano_conta`) REFERENCES `plano_contas` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_lancamentos_forma_pagamento` FOREIGN KEY (`id_forma_pagamento`) REFERENCES `formas_pagamento` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- Fim da migração.
