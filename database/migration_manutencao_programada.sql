-- Migração: adiciona tabela manutencao_programada (agendamentos por km e/ou data limite).
-- Execute após backup: mysql -u root -p locacao_veiculos < database/migration_manutencao_programada.sql
-- Requer MySQL 8.0.16+ para CHECK constraint.

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS `manutencao_programada` (
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
