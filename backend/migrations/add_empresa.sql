-- Migração: adiciona tabela empresa (dados da empresa para o menu Configurações).
-- Execute após backup: mysql -u root -p locacao_veiculos < backend/migrations/add_empresa.sql

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS `empresa` (
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

-- Registro único inicial (opcional; a API pode criar na primeira leitura se não existir)
INSERT INTO `empresa` (`id`, `nome_fantasia`, `razao_social`) VALUES (1, '', '')
ON DUPLICATE KEY UPDATE `id` = `id`;
