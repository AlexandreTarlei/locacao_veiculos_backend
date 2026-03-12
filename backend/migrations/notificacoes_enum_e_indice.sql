-- Migração: melhora schema da tabela notificacoes (status ENUM + índice composto).
-- Para bancos que já têm notificacoes com status varchar(20).
-- Execute: mysql -u root -p locacao_veiculos < backend/migrations/notificacoes_enum_e_indice.sql
-- Requer MySQL 8.0+ / MariaDB 10.2+.
-- Se algum passo falhar (ex.: CHECK já não existe ou índice já existe), pode ignorar esse passo.

SET NAMES utf8mb4;

-- 1) Alterar coluna status de VARCHAR para ENUM (valores já permitidos pelo CHECK anterior)
ALTER TABLE `notificacoes`
  MODIFY COLUMN `status` enum('nao_lida','lida','arquivada') NOT NULL DEFAULT 'nao_lida';

-- 2) Remover CHECK antigo se existir (redundante com ENUM). Em bancos criados pelo schema novo, não há CHECK.
-- ALTER TABLE `notificacoes` DROP CHECK `chk_notificacoes_status`;

-- 3) Índice composto para consultas "notificações do usuário X por status"
ALTER TABLE `notificacoes` ADD KEY `ix_notificacoes_usuario_status` (`id_usuario`, `status`);
