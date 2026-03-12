-- Tabela de contratos (vinculada a reserva opcional, cliente e veículo)
-- Execute no banco locacao_veiculos se a tabela ainda não existir.
-- A API também cria a tabela automaticamente ao subir (create_all).

CREATE TABLE IF NOT EXISTS contratos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    empresa_id INT NULL,
    reserva_id INT NULL,
    cliente_id INT NOT NULL,
    veiculo_id INT NOT NULL,
    valor_diaria DECIMAL(10,2) NULL,
    valor_total DECIMAL(10,2) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ativo',
    data_contrato TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_contratos_empresa (empresa_id),
    INDEX idx_contratos_reserva (reserva_id),
    INDEX idx_contratos_cliente (cliente_id),
    INDEX idx_contratos_veiculo (veiculo_id),
    INDEX idx_contratos_status (status),
    CONSTRAINT fk_contratos_reserva FOREIGN KEY (reserva_id) REFERENCES reservas(id),
    CONSTRAINT fk_contratos_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_contratos_veiculo FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
);
