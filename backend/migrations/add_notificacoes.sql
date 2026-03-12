-- Migração: adiciona tabela notificacoes (notificações por usuário).
-- Execute após backup: mysql -u root -p locacao_veiculos < backend/migrations/add_notificacoes.sql
-- Requer MySQL 8.0.16+ para CHECK constraint.

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS `notificacoes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `titulo` varchar(200) NOT NULL,
  `mensagem` text DEFAULT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'nao_lida',
  `data_notificacao` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_notificacoes_id_usuario` (`id_usuario`),
  KEY `ix_notificacoes_status` (`status`),
  KEY `ix_notificacoes_data` (`data_notificacao`),
  CONSTRAINT `chk_notificacoes_status` CHECK (`status` IN ('nao_lida','lida','arquivada')),
  CONSTRAINT `fk_notificacoes_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Notificações por usuário';
