-- Melhorias na tabela veiculos: DECIMAL para valores e campos de auditoria.
-- Executar uma vez em bancos já existentes: mysql -u root -p locacao_veiculos < backend/migrations/veiculos_decimal_e_auditoria.sql
-- (Se as colunas data_cadastro/data_atualizacao já existirem, pule o segundo ALTER ou execute só o primeiro.)

-- Tipos numéricos (evita erros de arredondamento)
ALTER TABLE veiculos
  MODIFY COLUMN quilometragem DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  MODIFY COLUMN valor_diaria DECIMAL(10,2) NOT NULL;

-- Campos de auditoria (executar apenas se a tabela ainda não tiver essas colunas)
ALTER TABLE veiculos
  ADD COLUMN data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ADD COLUMN data_atualizacao DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP;
