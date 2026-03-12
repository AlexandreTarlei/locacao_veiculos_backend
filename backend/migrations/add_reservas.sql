-- Tabela de reservas (período reservado antes da locação)
-- Execute no banco locacao_veiculos se a tabela ainda não existir.
-- A API também cria a tabela automaticamente ao subir (create_all).

CREATE TABLE IF NOT EXISTS reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    empresa_id INT NULL,
    cliente_id INT NOT NULL,
    veiculo_id INT NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'reservado',
    INDEX idx_reservas_empresa (empresa_id),
    INDEX idx_reservas_cliente (cliente_id),
    INDEX idx_reservas_veiculo (veiculo_id),
    INDEX idx_reservas_datas (data_inicio, data_fim),
    CONSTRAINT fk_reservas_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_reservas_veiculo FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
);
