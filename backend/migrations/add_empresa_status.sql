-- Migração: adiciona coluna status na tabela empresa (ativo | bloqueado).
-- Execute após backup: mysql -u root -p locacao_veiculos < backend/migrations/add_empresa_status.sql

SET NAMES utf8mb4;

ALTER TABLE `empresa`
  ADD COLUMN `status` varchar(20) NOT NULL DEFAULT 'ativo'
  COMMENT 'ativo ou bloqueado';

UPDATE `empresa` SET `status` = 'ativo';
