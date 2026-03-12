-- Migração: adiciona tabela manutencoes ao banco existente.
-- O frontend (locacao_veiculos.html) hoje guarda manutenções só no localStorage;
-- com esta tabela, a API pode persistir e servir esses dados para os gráficos (Chart.js).
-- Execute após backup: mysql -u root -p locacao_veiculos < database/migration_schema_manutencoes.sql

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS `manutencoes` (
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
