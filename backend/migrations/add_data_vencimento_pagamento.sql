-- Adiciona data_vencimento e data_pagamento em lancamentos_financeiros
ALTER TABLE lancamentos_financeiros
ADD COLUMN data_vencimento DATE,
ADD COLUMN data_pagamento DATE;
