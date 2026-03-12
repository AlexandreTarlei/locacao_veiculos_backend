-- Garante que todas as formas de pagamento padrão existam.
-- Insere apenas as que ainda não existem (comparação por nome, case-insensitive).
-- Pode ser executado manualmente no MariaDB/MySQL: mysql -u root -p locacao_veiculos < seed_formas_pagamento_se_faltando.sql

-- PIX
INSERT INTO formas_pagamento (nome, descricao, ativa)
SELECT 'PIX', 'Pagamento instantâneo via PIX', 1
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM formas_pagamento WHERE LOWER(nome) = LOWER('PIX'));

-- Cartão de crédito
INSERT INTO formas_pagamento (nome, descricao, ativa)
SELECT 'Cartão de crédito', 'Cartão de crédito à vista ou parcelado', 1
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM formas_pagamento WHERE LOWER(nome) = LOWER('Cartão de crédito'));

-- Cartão de débito
INSERT INTO formas_pagamento (nome, descricao, ativa)
SELECT 'Cartão de débito', 'Cartão de débito', 1
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM formas_pagamento WHERE LOWER(nome) = LOWER('Cartão de débito'));

-- Dinheiro
INSERT INTO formas_pagamento (nome, descricao, ativa)
SELECT 'Dinheiro', 'Pagamento em espécie', 1
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM formas_pagamento WHERE LOWER(nome) = LOWER('Dinheiro'));

-- Boleto bancário
INSERT INTO formas_pagamento (nome, descricao, ativa)
SELECT 'Boleto bancário', 'Boleto bancário', 1
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM formas_pagamento WHERE LOWER(nome) = LOWER('Boleto bancário'));

-- Transferência bancária
INSERT INTO formas_pagamento (nome, descricao, ativa)
SELECT 'Transferência bancária', 'Transferência TED/DOC', 1
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM formas_pagamento WHERE LOWER(nome) = LOWER('Transferência bancária'));

-- Cheque
INSERT INTO formas_pagamento (nome, descricao, ativa)
SELECT 'Cheque', 'Pagamento com cheque', 1
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM formas_pagamento WHERE LOWER(nome) = LOWER('Cheque'));

-- Vale/cupom
INSERT INTO formas_pagamento (nome, descricao, ativa)
SELECT 'Vale/cupom', 'Vale ou cupom de desconto', 1
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM formas_pagamento WHERE LOWER(nome) = LOWER('Vale/cupom'));
