-- Migração: tabela usuarios - NOT NULL em email/senha e colunas de auditoria.
-- Execute após backup: mysql -u root -p locacao_veiculos < backend/migrations/add_usuarios_not_null_e_auditoria.sql
-- Se existirem linhas com email ou senha NULL, corrija antes (ex.: desative o usuário ou defina email/senha).

SET NAMES utf8mb4;

-- Colunas de auditoria (execute uma vez; se já existirem, ignore ou comente os ADD COLUMN)
ALTER TABLE `usuarios`
  ADD COLUMN `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Data de criação do usuário',
  ADD COLUMN `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Última atualização',
  ADD COLUMN `ultimo_login` datetime DEFAULT NULL COMMENT 'Último login (preenchido no endpoint de login)';

-- NOT NULL em email e senha (obrigatórios para login)
ALTER TABLE `usuarios`
  MODIFY COLUMN `email` varchar(100) NOT NULL,
  MODIFY COLUMN `senha` varchar(255) NOT NULL;
