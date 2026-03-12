from datetime import datetime, timedelta
from typing import List, Optional
import os
import requests  # type: ignore
import json
from config_db import (
    MYSQL_HOST as DB_HOST,
    MYSQL_PORT as DB_PORT,
    MYSQL_USER as DB_USER,
    MYSQL_PASSWORD as DB_PASSWORD,
    MYSQL_DATABASE as DB_NAME,
)
from conexao_bd import ConexaoBD


class Veiculo:
    """Classe que representa um veículo disponível para locação"""
    
    def __init__(self, placa: str, marca: str, modelo: str, ano: int, valor_diaria: float, cor: str, quilometragem: float, id: int = None):
        self.id = id
        self.placa = placa
        self.marca = marca
        self.modelo = modelo
        self.ano = ano
        self.valor_diaria = valor_diaria
        self.cor = cor
        self.quilometragem = quilometragem
        self.disponivel = True
    
    def __str__(self):
        status = "Disponível" if self.disponivel else "Alugado"
        return f"{self.marca} {self.modelo} ({self.ano}) - {self.cor} - {self.quilometragem}km - R$ {self.valor_diaria:.2f}/dia - [{status}]"


class Cliente:
    """Classe que representa um cliente"""
    
    def __init__(self, nome: str, cpf: str, telefone: str, email: str, cep: str, endereco: str, data_nascimento: str, id: int = None):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.email = email
        self.cep = cep
        self.endereco = endereco
        self.data_nascimento = data_nascimento
        self.data_cadastro = datetime.now()
    
    def __str__(self):
        return f"{self.nome} (CPF: {self.cpf}) - Nasc: {self.data_nascimento}"


class FormaPagamento:
    """Classe que representa uma forma de pagamento"""
    
    def __init__(self, nome: str, descricao: str = "", id: int = None, ativa: bool = True):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.ativa = ativa
    
    def __str__(self):
        status = "Ativa" if self.ativa else "Inativa"
        return f"{self.nome} - {self.descricao} [{status}]"


class Pagamento:
    """Classe que representa um pagamento de locação"""
    
    def __init__(self, id_locacao: int, id_forma_pagamento: int, valor_pagamento: float, data_pagamento: datetime = None, numero_comprovante: str = "", observacoes: str = "", id: int = None):
        self.id = id
        self.id_locacao = id_locacao
        self.id_forma_pagamento = id_forma_pagamento
        self.valor_pagamento = valor_pagamento
        self.data_pagamento = data_pagamento or datetime.now()
        self.numero_comprovante = numero_comprovante
        self.observacoes = observacoes
    
    def __str__(self):
        return f"[ID: {self.id}] Locação #{self.id_locacao} - R$ {self.valor_pagamento:.2f} em {self.data_pagamento.strftime('%d/%m/%Y %H:%M')}"


class Locacao:
    """Classe que representa uma locação de veículo"""
    
    contador_id = 1
    
    def __init__(self, id_cliente: int, id_veiculo: int, cliente: Cliente, veiculo: Veiculo, data_inicio: datetime, dias: int, id: int = None):
        self.id = id if id is not None else Locacao.contador_id
        if id is None:
            Locacao.contador_id += 1
        self.id_cliente = id_cliente
        self.id_veiculo = id_veiculo
        self.cliente = cliente
        self.veiculo = veiculo
        self.data_inicio = data_inicio
        self.data_fim = data_inicio + timedelta(days=dias)
        self.dias = dias
        self.valor_total = dias * veiculo.valor_diaria
        self.multa_atraso = 0
        self.ativa = True
        self.pagamentos: List[Pagamento] = []  # Lista para armazenar pagamentos
    
    def calcular_multa_atraso(self, data_devolucao: datetime) -> float:
        """Calcula multa por atraso na devolução (50% do valor da diária por dia)"""
        if data_devolucao > self.data_fim:
            dias_atraso = (data_devolucao - self.data_fim).days
            return dias_atraso * (self.veiculo.valor_diaria * 0.5)
        return 0.0
    
    def adicionar_pagamento(self, pagamento: Pagamento) -> bool:
        """Adiciona um pagamento à locação"""
        if pagamento.valor_pagamento <= 0:
            print("[X] Valor de pagamento deve ser maior que zero!")
            return False
        
        saldo = self.obter_saldo_pendente()
        if pagamento.valor_pagamento > saldo:
            print(f"[X] Valor do pagamento (R$ {pagamento.valor_pagamento:.2f}) excede o saldo pendente (R$ {saldo:.2f})!")
            return False
        
        self.pagamentos.append(pagamento)
        print(f"[OK] Pagamento de R$ {pagamento.valor_pagamento:.2f} adicionado com sucesso!")
        return True
    
    def obter_total_pagamentos(self) -> float:
        """Retorna o total de pagamentos já realizados"""
        return sum(p.valor_pagamento for p in self.pagamentos)
    
    def obter_saldo_pendente(self) -> float:
        """Retorna o saldo ainda a pagar"""
        return self.valor_total - self.obter_total_pagamentos()
    
    def esta_quitada(self) -> bool:
        """Verifica se a locação está totalmente quitada"""
        return self.obter_saldo_pendente() <= 0
    
    def finalizar_locacao(self, data_devolucao: datetime = None):
        """Finaliza a locação e calcula valor total com possível multa"""
        if data_devolucao is None:
            data_devolucao = datetime.now()
        
        multa = self.calcular_multa_atraso(data_devolucao)
        self.multa_atraso = multa
        self.valor_total += multa
        self.ativa = False
        self.veiculo.disponivel = True
    
    def __str__(self):
        status = "Ativa" if self.ativa else "Finalizada"
        saldo = self.obter_saldo_pendente()
        pagto_info = f" - Pagamentos: R$ {self.obter_total_pagamentos():.2f} / Pendente: R$ {saldo:.2f}" if self.pagamentos else " - Sem pagamentos"
        return f"[ID: {self.id}] {self.cliente.nome} - {self.veiculo.marca} {self.veiculo.modelo} - R$ {self.valor_total:.2f} ({status}){pagto_info}"


class SistemaLocacao:
    """Sistema principal de gerenciamento de locações"""
    
    def __init__(self, usar_banco: bool = True):
        self.veiculos: List[Veiculo] = []
        self.clientes: List[Cliente] = []
        self.locacoes: List[Locacao] = []
        self.formas_pagamento: List[FormaPagamento] = []
        self.pagamentos: List[Pagamento] = []
        self.usar_banco = usar_banco
        self.bd = None
        
        if usar_banco:
            self.bd = ConexaoBD(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
            )
            if self.bd.conectar():
                self.carregar_dados_banco()
            else:
                print("[AVISO] Usando modo sem banco de dados (dados em memoria)")
                self.usar_banco = False
    
    # ===== MÉTODOS DE BANCO DE DADOS =====
    def carregar_dados_banco(self):
        """Carrega todos os dados do banco de dados para memória"""
        try:
            # Carregar veículos
            veiculos = self.bd.obter_todos_dicionario("SELECT * FROM veiculos")
            for v in veiculos:
                veiculo = Veiculo(
                    placa=v['placa'],
                    marca=v['marca'],
                    modelo=v['modelo'],
                    ano=v['ano'],
                    valor_diaria=float(v['valor_diaria']),
                    cor=v['cor'],
                    quilometragem=float(v['quilometragem']),
                    id=v['id']
                )
                veiculo.disponivel = bool(v['disponivel']) if v.get('disponivel') is not None else True
                self.veiculos.append(veiculo)
            
            # Carregar clientes
            clientes = self.bd.obter_todos_dicionario("SELECT * FROM clientes")
            for c in clientes:
                cliente = Cliente(
                    nome=c['nome'],
                    cpf=c['cpf'],
                    telefone=c['telefone'],
                    email=c['email'],
                    cep=c['cep'],
                    endereco=c['endereco'],
                    data_nascimento=c['data_nascimento'].strftime('%d/%m/%Y') if c['data_nascimento'] else '',
                    id=c['id']
                )
                self.clientes.append(cliente)
            
            # Carregar locações
            locacoes = self.bd.obter_todos_dicionario("SELECT * FROM locacoes")
            for l in locacoes:
                cliente = next((c for c in self.clientes if c.id == l['id_cliente']), None)
                veiculo = next((v for v in self.veiculos if v.id == l['id_veiculo']), None)
                
                if cliente and veiculo:
                    locacao = Locacao(
                        id_cliente=l['id_cliente'],
                        id_veiculo=l['id_veiculo'],
                        cliente=cliente,
                        veiculo=veiculo,
                        data_inicio=l['data_inicio'],
                        dias=(l['data_fim'] - l['data_inicio']).days,
                        id=l['id']
                    )
                    locacao.valor_total = float(l['valor_total'])
                    locacao.multa_atraso = float(l['multa_atraso']) if l['multa_atraso'] else 0
                    locacao.ativa = bool(l['ativa']) if l.get('ativa') is not None else True
                    self.locacoes.append(locacao)
            
            # Carregar formas de pagamento
            formas = self.bd.obter_todos_dicionario("SELECT * FROM formas_pagamento")
            for f in formas:
                forma = FormaPagamento(
                    nome=f['nome'],
                    descricao=f['descricao'],
                    id=f['id'],
                    ativa=f['ativa']
                )
                self.formas_pagamento.append(forma)
            
            # Carregar pagamentos
            pagamentos = self.bd.obter_todos_dicionario("SELECT * FROM pagamentos")
            for p in pagamentos:
                pagamento = Pagamento(
                    id_locacao=p['id_locacao'],
                    id_forma_pagamento=p['id_forma_pagamento'],
                    valor_pagamento=float(p['valor_pagamento']),
                    data_pagamento=p['data_pagamento'],
                    numero_comprovante=p['numero_comprovante'] or '',
                    observacoes=p['observacoes'] or '',
                    id=p['id']
                )
                # Adicionar pagamento à locação correspondente
                locacao = next((loc for loc in self.locacoes if loc.id == p['id_locacao']), None)
                if locacao:
                    locacao.pagamentos.append(pagamento)
                self.pagamentos.append(pagamento)
            
            print(f"[OK] Carregados {len(self.veiculos)} veículos, {len(self.clientes)} clientes, {len(self.locacoes)} locações, {len(self.formas_pagamento)} formas de pagamento e {len(self.pagamentos)} pagamentos")
        except Exception as e:
            print(f"[X] Erro ao carregar dados do banco: {e}")
    
    def fechar_conexao(self):
        """Fecha a conexão com o banco de dados"""
        if self.bd:
            self.bd.desconectar()
    
    # ===== GERENCIAMENTO DE VEÍCULOS =====
    def adicionar_veiculo(self, placa: str, marca: str, modelo: str, ano: int, valor_diaria: float, cor: str, quilometragem: float):
        """Adiciona um novo veículo à frota"""
        if any(v.placa == placa for v in self.veiculos):
            print("[X] Veículo com esta placa já existe!")
            return False
        
        # Salvar no banco de dados se ativado
        if self.usar_banco:
            query = """
                INSERT INTO veiculos (placa, marca, modelo, ano, cor, quilometragem, valor_diaria)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            if not self.bd.executar(query, (placa, marca, modelo, ano, cor, quilometragem, valor_diaria)):
                return False
            veiculo_id = self.bd.obter_ultimo_id()
        else:
            veiculo_id = None
        
        veiculo = Veiculo(placa, marca, modelo, ano, valor_diaria, cor, quilometragem, id=veiculo_id)
        self.veiculos.append(veiculo)
        print(f"[OK] Veiculo adicionado: {veiculo}")
        return True
    
    def listar_veiculos(self, apenas_disponiveis: bool = False):
        """Lista todos os veículos ou apenas os disponíveis"""
        if not self.veiculos:
            print("Nenhum veículo cadastrado.")
            return
        
        veiculos = [v for v in self.veiculos if (not apenas_disponiveis or v.disponivel)]
        
        if not veiculos:
            print("Nenhum veículo disponível no momento.")
            return
        
        print("\n" + "="*70)
        print("VEÍCULOS DISPONÍVEIS" if apenas_disponiveis else "TODOS OS VEÍCULOS")
        print("="*70)
        for i, veiculo in enumerate(veiculos, 1):
            print(f"{i}. {veiculo}")
        print("="*70)
    
    def buscar_veiculo_placa(self, placa: str) -> Optional[Veiculo]:
        """Busca veículo pela placa"""
        return next((v for v in self.veiculos if v.placa == placa), None)
    
    def editar_veiculo(self, placa: str) -> bool:
        """Edita as informações de um veículo"""
        veiculo = self.buscar_veiculo_placa(placa)
        if not veiculo:
            print("[X] Veículo não encontrado!")
            return False
        
        print(f"\n--- Editando Veículo: {placa} ---")
        print(f"Valor diária atual: R$ {veiculo.valor_diaria:.2f}")
        novo_valor = input("Novo valor da diária (Enter para manter): ").strip()
        if novo_valor:
            try:
                veiculo.valor_diaria = float(novo_valor)
            except ValueError:
                print("[X] Valor inválido!")
                return False
        
        print(f"Quilometragem atual: {veiculo.quilometragem}km")
        nova_km = input("Nova quilometragem (Enter para manter): ").strip()
        if nova_km:
            try:
                veiculo.quilometragem = float(nova_km)
            except ValueError:
                print("[X] Valor inválido!")
                return False
        
        # Atualizar no banco de dados se ativado
        if self.usar_banco and veiculo.id:
            query = "UPDATE veiculos SET valor_diaria = %s, quilometragem = %s WHERE id = %s"
            if not self.bd.executar(query, (veiculo.valor_diaria, veiculo.quilometragem, veiculo.id)):
                return False
        
        print("[OK] Veiculo atualizado com sucesso!")
        return True
    
    def deletar_veiculo(self, placa: str) -> bool:
        """Delete um veículo da frota"""
        veiculo = self.buscar_veiculo_placa(placa)
        if not veiculo:
            print("[X] Veículo não encontrado!")
            return False
        
        if not veiculo.disponivel:
            print("[X] Não é possível deletar um veículo que está alugado!")
            return False
        
        confirmacao = input(f"\nTem certeza que deseja deletar {veiculo.marca} {veiculo.modelo} (placa: {placa})? (S/N): ").strip().upper()
        if confirmacao != "S":
            print("[X] Deleção cancelada.")
            return False
        
        # Deletar do banco de dados se ativado
        if self.usar_banco and veiculo.id:
            query = "DELETE FROM veiculos WHERE id = %s"
            if not self.bd.executar(query, (veiculo.id,)):
                return False
        
        self.veiculos.remove(veiculo)
        print(f"[OK] Veículo deletado com sucesso!")
        return True
    
    # ===== GERENCIAMENTO DE CLIENTES =====
    def adicionar_cliente(self, nome: str, cpf: str, telefone: str, email: str, cep: str, endereco: str, data_nascimento: str):
        """Adiciona um novo cliente"""
        cpf_norm = self._normalizar_cpf(cpf)
        if any(self._normalizar_cpf(c.cpf) == cpf_norm for c in self.clientes):
            print("[X] Cliente com este CPF já existe!")
            return False
        
        # Salvar no banco de dados se ativado
        if self.usar_banco:
            # Converter data de DD/MM/AAAA para AAAA-MM-DD para o banco
            try:
                data_obj = datetime.strptime(data_nascimento, '%d/%m/%Y')
                data_db = data_obj.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                data_db = None

            query = """
                INSERT INTO clientes (nome, cpf, telefone, email, cep, endereco, data_nascimento)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            if not self.bd.executar(query, (nome, cpf, telefone, email, cep, endereco, data_db)):
                return False
            cliente_id = self.bd.obter_ultimo_id()
        else:
            cliente_id = None
        
        cliente = Cliente(nome, cpf, telefone, email, cep, endereco, data_nascimento, id=cliente_id)
        self.clientes.append(cliente)
        print(f"[OK] Cliente adicionado: {cliente}")
        return True
    
    def listar_clientes(self):
        """Lista todos os clientes"""
        if not self.clientes:
            print("Nenhum cliente cadastrado.")
            return
        
        print("\n" + "="*110)
        print("CLIENTES CADASTRADOS")
        print("="*110)
        for i, cliente in enumerate(self.clientes, 1):
            print(f"{i}. {cliente.nome}")
            print(f"   CPF: {cliente.cpf} | Telefone: {cliente.telefone}")
            print(f"   Data de Nascimento: {cliente.data_nascimento}")
            print(f"   CEP: {cliente.cep}")
            print(f"   Endereço: {cliente.endereco}")
            print(f"   Email: {cliente.email}")
            print(f"   Cadastrado em: {cliente.data_cadastro.strftime('%d/%m/%Y %H:%M')}")
            print("-" * 110)
        print("="*110)
    
    def _normalizar_cpf(self, cpf: str) -> str:
        """Remove pontuação do CPF para comparação"""
        return (cpf or "").replace(".", "").replace("-", "").replace(" ", "").strip()

    def buscar_cliente_cpf(self, cpf: str) -> Optional[Cliente]:
        """Busca cliente pelo CPF (aceita com ou sem pontuação)"""
        cpf_busca = self._normalizar_cpf(cpf)
        return next((c for c in self.clientes if self._normalizar_cpf(c.cpf) == cpf_busca), None)
    
    def editar_cliente(self, cpf: str) -> bool:
        """Edita as informações de um cliente existente"""
        cliente = self.buscar_cliente_cpf(cpf)
        if not cliente:
            print("[X] Cliente não encontrado!")
            return False
        
        print(f"\n--- Editando Cliente: {cliente.nome} ---")
        
        novo_nome = input(f"Nome ({cliente.nome}): ").strip()
        if novo_nome:
            cliente.nome = novo_nome
        
        novo_telefone = input(f"Telefone ({cliente.telefone}): ").strip()
        if novo_telefone:
            cliente.telefone = novo_telefone
        
        novo_email = input(f"Email ({cliente.email}): ").strip()
        if novo_email:
            cliente.email = novo_email
        
        novo_cep = input(f"CEP ({cliente.cep}): ").strip()
        if novo_cep:
            dados_cep = buscar_endereco_por_cep(novo_cep)
            if dados_cep:
                cliente.cep = novo_cep.replace('-', '').replace('.', '')
                numero = input("Número da residência: ").strip()
                complemento = input("Complemento (opcional): ").strip()
                cliente.endereco = formatar_endereco_completo(dados_cep, numero, complemento)
                print(f"[OK] Endereço atualizado: {cliente.endereco}")
            else:
                print("[X] CEP não encontrado. Endereço não foi atualizado.")
        
        novo_endereco = input(f"Endereço completo ({cliente.endereco}): ").strip()
        if novo_endereco:
            cliente.endereco = novo_endereco
        
        nova_data = input(f"Data de nascimento ({cliente.data_nascimento}): ").strip()
        if nova_data:
            cliente.data_nascimento = nova_data
        
        # Atualizar no banco de dados se ativado
        if self.usar_banco and cliente.id:
            try:
                data_obj = datetime.strptime(cliente.data_nascimento, '%d/%m/%Y')
                data_db = data_obj.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                data_db = None

            query = """
                UPDATE clientes 
                SET nome = %s, telefone = %s, email = %s, cep = %s, endereco = %s, data_nascimento = %s
                WHERE id = %s
            """
            if not self.bd.executar(query, (cliente.nome, cliente.telefone, cliente.email, cliente.cep, cliente.endereco, data_db, cliente.id)):
                return False
        
        print("[OK] Cliente atualizado com sucesso!")
        return True
    
    # ===== GERENCIAMENTO DE LOCAÇÕES =====
    def criar_locacao(self, cpf_cliente: str, placa_veiculo: str, dias: int) -> bool:
        """Cria uma nova locação"""
        cliente = self.buscar_cliente_cpf(cpf_cliente)
        if not cliente:
            print("[X] Cliente não encontrado!")
            return False
        
        veiculo = self.buscar_veiculo_placa(placa_veiculo)
        if not veiculo:
            print("[X] Veículo não encontrado!")
            return False
        
        if not veiculo.disponivel:
            print("[X] Veículo não está disponível!")
            return False
        
        if dias <= 0:
            print("[X] Número de dias deve ser maior que 0!")
            return False
        
        data_inicio = datetime.now()
        data_fim = data_inicio + timedelta(days=dias)
        valor_total = dias * veiculo.valor_diaria
        
        # Salvar no banco de dados se ativado
        if self.usar_banco:
            query = """
                INSERT INTO locacoes (id_cliente, id_veiculo, data_inicio, data_fim, valor_total)
                VALUES (%s, %s, %s, %s, %s)
            """
            if not self.bd.executar(query, (cliente.id, veiculo.id, data_inicio, data_fim, valor_total)):
                return False
            locacao_id = self.bd.obter_ultimo_id()
            
            # Atualizar disponibilidade do veículo no banco
            query_veiculo = "UPDATE veiculos SET disponivel = FALSE WHERE id = %s"
            self.bd.executar(query_veiculo, (veiculo.id,))
        else:
            locacao_id = None
        
        locacao = Locacao(cliente.id, veiculo.id, cliente, veiculo, data_inicio, dias, id=locacao_id)
        veiculo.disponivel = False
        self.locacoes.append(locacao)
        
        print(f"\n[OK] Locacao criada com sucesso!")
        print(f"ID da Locação: {locacao.id}")
        print(f"Cliente: {cliente.nome}")
        print(f"Veículo: {veiculo.marca} {veiculo.modelo}")
        print(f"Período: {locacao.data_inicio.strftime('%d/%m/%Y')} à {locacao.data_fim.strftime('%d/%m/%Y')}")
        print(f"Valor Total: R$ {locacao.valor_total:.2f}\n")
        
        return True
    
    def listar_locacoes_ativas(self):
        """Lista todas as locações ativas"""
        locacoes_ativas = [l for l in self.locacoes if l.ativa]
        
        if not locacoes_ativas:
            print("Nenhuma locação ativa no momento.")
            return
        
        print("\n" + "="*70)
        print("LOCAÇÕES ATIVAS")
        print("="*70)
        for locacao in locacoes_ativas:
            print(locacao)
        print("="*70)
    
    def finalizar_locacao(self, id_locacao: int) -> bool:
        """Finaliza uma locação"""
        locacao = next((l for l in self.locacoes if l.id == id_locacao), None)
        
        if not locacao:
            print("[X] Locação não encontrada!")
            return False
        
        if not locacao.ativa:
            print("[X] Esta locação já foi finalizada!")
            return False
        
        data_devolucao = datetime.now()
        locacao.finalizar_locacao(data_devolucao)
        
        # Atualizar no banco de dados se ativado (compatível com schema API e setup_banco)
        if self.usar_banco and locacao.id:
            query = """
                UPDATE locacoes
                SET ativa = FALSE, multa_atraso = %s, valor_total = %s
                WHERE id = %s
            """
            if not self.bd.executar(query, (locacao.multa_atraso, locacao.valor_total, locacao.id)):
                return False
            # Marcar veículo como disponível no banco
            query_veiculo = "UPDATE veiculos SET disponivel = TRUE WHERE id = %s"
            self.bd.executar(query_veiculo, (locacao.id_veiculo,))

        print(f"\n[OK] Locacao finalizada!")
        print(f"Cliente: {locacao.cliente.nome}")
        print(f"Veículo: {locacao.veiculo.marca} {locacao.veiculo.modelo}")
        print(f"Multa por atraso: R$ {locacao.multa_atraso:.2f}")
        print(f"Valor Total: R$ {locacao.valor_total:.2f}\n")
        
        return True
    
    def listar_historico_locacoes(self):
        """Lista o histórico de todas as locações"""
        if not self.locacoes:
            print("Nenhuma locação registrada.")
            return
        
        print("\n" + "="*70)
        print("HISTÓRICO DE LOCAÇÕES")
        print("="*70)
        for locacao in self.locacoes:
            print(locacao)
        print("="*70)
    
    # ===== CRUD DE FORMAS DE PAGAMENTO =====
    def recarregar_formas_pagamento(self) -> bool:
        """Recarrega a lista de formas de pagamento a partir do banco de dados."""
        if not self.usar_banco or not self.bd:
            return False
        try:
            self.formas_pagamento.clear()
            formas = self.bd.obter_todos_dicionario("SELECT * FROM formas_pagamento")
            for f in formas:
                forma = FormaPagamento(
                    nome=f['nome'],
                    descricao=f['descricao'],
                    id=f['id'],
                    ativa=f['ativa']
                )
                self.formas_pagamento.append(forma)
            return True
        except Exception as e:
            print(f"[X] Erro ao recarregar formas de pagamento: {e}")
            return False

    def obter_forma_pagamento_por_nome(self, nome: str) -> Optional[FormaPagamento]:
        """Busca uma forma de pagamento pelo nome"""
        return next((f for f in self.formas_pagamento if f.nome.lower() == nome.lower()), None)
    
    def obter_forma_pagamento_por_id(self, id_forma: int) -> Optional[FormaPagamento]:
        """Busca uma forma de pagamento pelo ID"""
        return next((f for f in self.formas_pagamento if f.id == id_forma), None)
    
    def adicionar_forma_pagamento(self, nome: str, descricao: str = "") -> bool:
        """Adiciona uma nova forma de pagamento"""
        # Verificar se já existe uma forma com este nome
        if self.obter_forma_pagamento_por_nome(nome):
            print(f"[X] Forma de pagamento '{nome}' já existe!")
            return False
        
        if not nome or nome.strip() == "":
            print("[X] Nome da forma de pagamento não pode estar vazio!")
            return False
        
        # Salvar no banco de dados se ativado
        if self.usar_banco:
            query = """
                INSERT INTO formas_pagamento (nome, descricao, ativa)
                VALUES (%s, %s, TRUE)
            """
            if not self.bd.executar(query, (nome, descricao)):
                return False
            forma_id = self.bd.obter_ultimo_id()
        else:
            forma_id = None
        
        forma = FormaPagamento(nome, descricao, id=forma_id, ativa=True)
        self.formas_pagamento.append(forma)
        print(f"[OK] Forma de pagamento '{nome}' adicionada com sucesso!")
        return True
    
    def listar_formas_pagamento(self):
        """Lista todas as formas de pagamento disponíveis"""
        if not self.formas_pagamento:
            print("Nenhuma forma de pagamento disponível.")
            return
        
        print("\n" + "="*70)
        print("FORMAS DE PAGAMENTO DISPONÍVEIS")
        print("="*70)
        for i, forma in enumerate(self.formas_pagamento, 1):
            status = "[OK] Ativa" if forma.ativa else "[X] Inativa"
            print(f"{i}. (ID: {forma.id}) {forma.nome}")
            if forma.descricao:
                print(f"   Descrição: {forma.descricao}")
            print(f"   Status: {status}")
        print("="*70)
    
    def editar_forma_pagamento(self, id_forma: int, nome: str = None, descricao: str = None, ativa: bool = None) -> bool:
        """Edita uma forma de pagamento existente"""
        forma = self.obter_forma_pagamento_por_id(id_forma)
        
        if not forma:
            print(f"[X] Forma de pagamento com ID {id_forma} não encontrada!")
            return False
        
        # Verificar se o novo nome já existe
        if nome and nome != forma.nome and self.obter_forma_pagamento_por_nome(nome):
            print(f"[X] Forma de pagamento '{nome}' já existe!")
            return False
        
        # Atualizar dados locais
        nome_antigo = forma.nome
        if nome:
            forma.nome = nome
        if descricao is not None:
            forma.descricao = descricao
        if ativa is not None:
            forma.ativa = ativa
        
        # Atualizar no banco de dados se ativado
        if self.usar_banco and forma.id:
            query = """
                UPDATE formas_pagamento 
                SET nome = %s, descricao = %s, ativa = %s
                WHERE id = %s
            """
            if not self.bd.executar(query, (forma.nome, forma.descricao, forma.ativa, forma.id)):
                return False
        
        print(f"[OK] Forma de pagamento '{nome_antigo}' atualizada com sucesso!")
        return True
    
    def ativar_forma_pagamento(self, id_forma: int) -> bool:
        """Ativa uma forma de pagamento inativa"""
        forma = self.obter_forma_pagamento_por_id(id_forma)
        
        if not forma:
            print(f"[X] Forma de pagamento com ID {id_forma} não encontrada!")
            return False
        
        if forma.ativa:
            print(f"[AVISO] Forma de pagamento '{forma.nome}' ja esta ativa!")
            return True
        
        forma.ativa = True
        
        # Atualizar no banco de dados
        if self.usar_banco and forma.id:
            query = "UPDATE formas_pagamento SET ativa = TRUE WHERE id = %s"
            if not self.bd.executar(query, (forma.id,)):
                return False
        
        print(f"[OK] Forma de pagamento '{forma.nome}' ativada com sucesso!")
        return True
    
    def desativar_forma_pagamento(self, id_forma: int) -> bool:
        """Desativa uma forma de pagamento ativa"""
        forma = self.obter_forma_pagamento_por_id(id_forma)
        
        if not forma:
            print(f"[X] Forma de pagamento com ID {id_forma} não encontrada!")
            return False
        
        if not forma.ativa:
            print(f"[AVISO] Forma de pagamento '{forma.nome}' ja esta inativa!")
            return True
        
        # Verificar se há pagamentos usando esta forma
        if self.usar_banco and forma.id:
            query = "SELECT COUNT(*) FROM pagamentos WHERE id_forma_pagamento = %s"
            resultado = self.bd.obter_um(query, (forma.id,))
            if resultado and resultado[0] > 0:
                print(f"[AVISO] Existem {resultado[0]} pagamento(s) usando esta forma.")
                confirmacao = input("Deseja desativar mesmo assim? (S/N): ").strip().upper()
                if confirmacao != "S":
                    print("[X] Operação cancelada.")
                    return False
        
        forma.ativa = False
        
        # Atualizar no banco de dados
        if self.usar_banco and forma.id:
            query = "UPDATE formas_pagamento SET ativa = FALSE WHERE id = %s"
            if not self.bd.executar(query, (forma.id,)):
                return False
        
        print(f"[OK] Forma de pagamento '{forma.nome}' desativada com sucesso!")
        return True
    
    def deletar_forma_pagamento(self, id_forma: int) -> bool:
        """Deleta uma forma de pagamento"""
        forma = self.obter_forma_pagamento_por_id(id_forma)
        
        if not forma:
            print(f"[X] Forma de pagamento com ID {id_forma} não encontrada!")
            return False
        
        # Verificar se há pagamentos usando esta forma
        if self.usar_banco and forma.id:
            query = "SELECT COUNT(*) FROM pagamentos WHERE id_forma_pagamento = %s"
            resultado = self.bd.obter_um(query, (forma.id,))
            if resultado and resultado[0] > 0:
                print(f"[X] Não é possível deletar! Existem {resultado[0]} pagamento(s) usando esta forma.")
                return False
        
        # Deletar do banco de dados
        if self.usar_banco and forma.id:
            query = "DELETE FROM formas_pagamento WHERE id = %s"
            if not self.bd.executar(query, (forma.id,)):
                return False
        
        # Remover da lista local
        self.formas_pagamento.remove(forma)
        print(f"[OK] Forma de pagamento '{forma.nome}' deletada com sucesso!")
        return True
    
    # ===== GERENCIAMENTO DE PAGAMENTOS =====
    
    def registrar_pagamento(self, id_locacao: int, nome_forma_pagamento: str, valor_pagamento: float, numero_comprovante: str = "", observacoes: str = "") -> bool:
        """Registra um pagamento para uma locação"""
        locacao = next((l for l in self.locacoes if l.id == id_locacao), None)
        if not locacao:
            print("[X] Locação não encontrada!")
            return False
        
        forma_pagamento = self.obter_forma_pagamento_por_nome(nome_forma_pagamento)
        if not forma_pagamento:
            print(f"[X] Forma de pagamento '{nome_forma_pagamento}' não encontrada!")
            self.listar_formas_pagamento()
            return False
        
        if not forma_pagamento.ativa:
            print(f"[X] A forma de pagamento '{nome_forma_pagamento}' está inativa!")
            return False
        
        # Criar objeto pagamento
        pagamento = Pagamento(
            id_locacao=id_locacao,
            id_forma_pagamento=forma_pagamento.id,
            valor_pagamento=valor_pagamento,
            data_pagamento=datetime.now(),
            numero_comprovante=numero_comprovante,
            observacoes=observacoes
        )
        
        # Adicionar pagamento à locação
        if not locacao.adicionar_pagamento(pagamento):
            return False
        
        # Salvar no banco de dados se ativado
        if self.usar_banco and locacao.id and forma_pagamento.id:
            query = """
                INSERT INTO pagamentos (id_locacao, id_forma_pagamento, valor_pagamento, data_pagamento, numero_comprovante, observacoes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            if not self.bd.executar(query, (locacao.id, forma_pagamento.id, valor_pagamento, datetime.now(), numero_comprovante, observacoes)):
                # Se falhar no banco, remove o pagamento da memória
                locacao.pagamentos.pop()
                return False
            pagamento.id = self.bd.obter_ultimo_id()
            self.pagamentos.append(pagamento)
        
        return True
    
    def listar_pagamentos_locacao(self, id_locacao: int):
        """Lista todos os pagamentos de uma locação"""
        locacao = next((l for l in self.locacoes if l.id == id_locacao), None)
        if not locacao:
            print("[X] Locação não encontrada!")
            return
        
        if not locacao.pagamentos:
            print(f"Nenhum pagamento registrado para a locação #{id_locacao}")
            return
        
        print("\n" + "="*70)
        print(f"PAGAMENTOS DA LOCAÇÃO #{id_locacao}")
        print("="*70)
        print(f"Cliente: {locacao.cliente.nome}")
        print(f"Veículo: {locacao.veiculo.marca} {locacao.veiculo.modelo}")
        print(f"Valor Total da Locação: R$ {locacao.valor_total:.2f}")
        print("-"*70)
        
        for pagamento in locacao.pagamentos:
            forma = self.obter_forma_pagamento_por_id(pagamento.id_forma_pagamento)
            forma_nome = forma.nome if forma else "Desconhecida"
            print(f"ID: {pagamento.id} | Forma: {forma_nome} | Valor: R$ {pagamento.valor_pagamento:.2f}")
            print(f"  Data: {pagamento.data_pagamento.strftime('%d/%m/%Y %H:%M:%S')}")
            if pagamento.numero_comprovante:
                print(f"  Comprovante: {pagamento.numero_comprovante}")
            if pagamento.observacoes:
                print(f"  Observações: {pagamento.observacoes}")
        
        print("-"*70)
        print(f"Total Pago: R$ {locacao.obter_total_pagamentos():.2f}")
        print(f"Saldo Pendente: R$ {locacao.obter_saldo_pendente():.2f}")
        if locacao.esta_quitada():
            print("[OK] Locacao QUITADA")
        print("="*70)
    
    def obter_resumo_pagamentos_locacao(self, id_locacao: int) -> dict:
        """Retorna um resumo dos pagamentos de uma locação"""
        locacao = next((l for l in self.locacoes if l.id == id_locacao), None)
        if not locacao:
            return None
        
        return {
            'id_locacao': locacao.id,
            'cliente': locacao.cliente.nome,
            'valor_total': locacao.valor_total,
            'total_pago': locacao.obter_total_pagamentos(),
            'saldo_pendente': locacao.obter_saldo_pendente(),
            'quitada': locacao.esta_quitada(),
            'quantidade_pagamentos': len(locacao.pagamentos)
        }


def buscar_endereco_por_cep(cep: str) -> dict:
    """
    Busca endereço automaticamente via API ViaCEP
    Retorna um dicionário com os dados do endereço
    """
    # Remove caracteres especiais do CEP
    cep_limpo = cep.replace('-', '').replace('.', '').strip()
    
    # Valida se o CEP tem 8 dígitos
    if len(cep_limpo) != 8 or not cep_limpo.isdigit():
        return None
    
    try:
        url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            dados = response.json()
            
            # Verifica se o CEP é válido (não retorna erro)
            if "erro" not in dados:
                return dados
            else:
                return None
    except requests.exceptions.RequestException as e:
        print(f"[AVISO] Erro ao conectar com o servidor de CEP: {e}")
        return None


def formatar_endereco_completo(dados_cep: dict, numero: str, complemento: str) -> str:
    """
    Formata o endereço completo a partir dos dados da API ViaCEP
    """
    rua = dados_cep.get('logradouro', '')
    bairro = dados_cep.get('bairro', '')
    cidade = dados_cep.get('localidade', '')
    estado = dados_cep.get('uf', '')
    cep = dados_cep.get('cep', '')
    
    endereco = f"{rua}, {numero}"
    if complemento:
        endereco += f", {complemento}"
    endereco += f" - {bairro}, {cidade}, {estado}"
    
    return endereco


def limpar_tela():
    """Limpa a tela do console"""
    os.system('cls' if os.name == 'nt' else 'clear')


def menu_principal(sistema: SistemaLocacao):
    """Menu principal da aplicação"""
    while True:
        print("\n" + "="*70)
        print("  SISTEMA DE LOCACAO DE VEICULOS")
        print("="*70)
        print("1. Gerenciar Veículos")
        print("2. Gerenciar Clientes")
        print("3. Gerenciar Locações")
        print("4. Gerenciar Formas de Pagamento")
        print("5. Alterar Veículo (rápido)")
        print("6. Alterar Cliente (rápido)")
        print("7. Sair")
        print("="*70)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            menu_veiculos(sistema)
        elif opcao == "2":
            menu_clientes(sistema)
        elif opcao == "3":
            menu_locacoes(sistema)
        elif opcao == "4":
            menu_formas_pagamento(sistema)
        elif opcao == "5":
            placa = input("\nPlaca do veículo a alterar: ").strip().upper()
            sistema.editar_veiculo(placa)
        elif opcao == "6":
            cpf = input("\nCPF do cliente a alterar: ").strip()
            sistema.editar_cliente(cpf)
        elif opcao == "7":
            print("\n  Ate logo!")
            break
        else:
            print("[X] Opção inválida!")


def menu_veiculos(sistema: SistemaLocacao):
    """Menu de gerenciamento de veículos"""
    while True:
        print("\n" + "="*70)
        print("GERENCIAR VEÍCULOS")
        print("="*70)
        print("1. Adicionar novo veículo")
        print("2. Listar todos os veículos")
        print("3. Listar veículos disponíveis")
        print("4. Editar veículo")
        print("5. Deletar veículo")
        print("6. Voltar")
        print("="*70)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            print("\n--- Adicionar Novo Veículo ---")
            placa = input("Placa: ").strip().upper()
            marca = input("Marca: ").strip()
            modelo = input("Modelo: ").strip()
            cor = input("Cor: ").strip()
            
            try:
                ano = int(input("Ano: ").strip())
                valor = float(input("Valor da diária (R$): ").strip())
                quilometragem = float(input("Quilometragem atual (km): ").strip())
                sistema.adicionar_veiculo(placa, marca, modelo, ano, valor, cor, quilometragem)
            except ValueError:
                print("[X] Valores inválidos!")
        
        elif opcao == "2":
            sistema.listar_veiculos()
        
        elif opcao == "3":
            sistema.listar_veiculos(apenas_disponiveis=True)
        
        elif opcao == "4":
            placa = input("\nPlaca do veículo a editar: ").strip().upper()
            sistema.editar_veiculo(placa)
        
        elif opcao == "5":
            placa = input("\nPlaca do veículo a deletar: ").strip().upper()
            sistema.deletar_veiculo(placa)
        
        elif opcao == "6":
            break
        
        else:
            print("[X] Opção inválida!")


def menu_clientes(sistema: SistemaLocacao):
    """Menu de gerenciamento de clientes"""
    while True:
        print("\n" + "="*70)
        print("GERENCIAR CLIENTES")
        print("="*70)
        print("1. Adicionar novo cliente")
        print("2. Listar clientes")
        print("3. Editar cliente")
        print("4. Voltar")
        print("="*70)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            print("\n--- Adicionar Novo Cliente ---")
            nome = input("Nome completo: ").strip()
            cpf = input("CPF (apenas números): ").strip()
            telefone = input("Telefone: ").strip()
            email = input("Email: ").strip()
            
            # Buscar endereço via CEP
            cep = input("CEP (formato: 12345-678 ou 12345678): ").strip()
            dados_cep = buscar_endereco_por_cep(cep)
            
            if dados_cep:
                print(f"\n[OK] CEP encontrado!")
                print(f"   Rua: {dados_cep.get('logradouro', 'N/A')}")
                print(f"   Bairro: {dados_cep.get('bairro', 'N/A')}")
                print(f"   Cidade: {dados_cep.get('localidade', 'N/A')}, {dados_cep.get('uf', 'N/A')}")
                
                numero = input("\nNúmero da residência: ").strip()
                complemento = input("Complemento (opcional, ex: apt 101): ").strip()
                endereco = formatar_endereco_completo(dados_cep, numero, complemento)
                cep_limpo = cep.replace('-', '').replace('.', '')
            else:
                print("\n[X] CEP nao encontrado! Insira o endereco manualmente.")
                endereco = input("Endereço completo: ").strip()
                cep_limpo = cep.replace('-', '').replace('.', '')
            
            data_nascimento = input("Data de nascimento (DD/MM/AAAA): ").strip()
            sistema.adicionar_cliente(nome, cpf, telefone, email, cep_limpo, endereco, data_nascimento)
        
        elif opcao == "2":
            sistema.listar_clientes()
        
        elif opcao == "3":
            cpf = input("\nCPF do cliente a editar: ").strip()
            sistema.editar_cliente(cpf)
        
        elif opcao == "4":
            break
        
        else:
            print("[X] Opção inválida!")


def menu_formas_pagamento(sistema: SistemaLocacao):
    """Menu de gerenciamento de formas de pagamento"""
    while True:
        # Atualiza a lista de formas de pagamento a partir do banco
        if sistema.usar_banco:
            sistema.recarregar_formas_pagamento()
        print("\n" + "="*70)
        print("GERENCIAR FORMAS DE PAGAMENTO")
        print("="*70)
        print("1. Listar formas de pagamento")
        print("2. Adicionar nova forma de pagamento")
        print("3. Editar forma de pagamento")
        print("4. Ativar forma de pagamento")
        print("5. Desativar forma de pagamento")
        print("6. Deletar forma de pagamento")
        print("7. Voltar")
        print("="*70)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            sistema.listar_formas_pagamento()
        
        elif opcao == "2":
            print("\n--- Adicionar Nova Forma de Pagamento ---")
            nome = input("Nome da forma de pagamento: ").strip()
            descricao = input("Descrição (opcional): ").strip()
            if sistema.adicionar_forma_pagamento(nome, descricao):
                print()
        
        elif opcao == "3":
            print("\n--- Editar Forma de Pagamento ---")
            sistema.listar_formas_pagamento()
            try:
                id_forma = int(input("\nID da forma a editar: ").strip())
                forma = sistema.obter_forma_pagamento_por_id(id_forma)
                if forma:
                    print(f"\nEditando: {forma.nome}")
                    novo_nome = input("Novo nome (deixe vazio para manter): ").strip() or None
                    nova_descricao = input("Nova descrição (deixe vazio para manter): ").strip()
                    sistema.editar_forma_pagamento(id_forma, novo_nome, nova_descricao if nova_descricao else None)
                else:
                    print("[X] Forma de pagamento não encontrada!")
            except ValueError:
                print("[X] ID inválido!")
        
        elif opcao == "4":
            print("\n--- Ativar Forma de Pagamento ---")
            sistema.listar_formas_pagamento()
            try:
                id_forma = int(input("\nID da forma a ativar: ").strip())
                sistema.ativar_forma_pagamento(id_forma)
            except ValueError:
                print("[X] ID inválido!")
        
        elif opcao == "5":
            print("\n--- Desativar Forma de Pagamento ---")
            sistema.listar_formas_pagamento()
            try:
                id_forma = int(input("\nID da forma a desativar: ").strip())
                sistema.desativar_forma_pagamento(id_forma)
            except ValueError:
                print("[X] ID inválido!")
        
        elif opcao == "6":
            print("\n--- Deletar Forma de Pagamento ---")
            sistema.listar_formas_pagamento()
            try:
                id_forma = int(input("\nID da forma a deletar: ").strip())
                confirmacao = input("Tem certeza? (S/N): ").strip().upper()
                if confirmacao == "S":
                    sistema.deletar_forma_pagamento(id_forma)
                else:
                    print("[X] Operação cancelada.")
            except ValueError:
                print("[X] ID inválido!")
        
        elif opcao == "7":
            break
        
        else:
            print("[X] Opção inválida!")


def menu_locacoes(sistema: SistemaLocacao):
    """Menu de gerenciamento de locações"""
    while True:
        print("\n" + "="*70)
        print("GERENCIAR LOCAÇÕES")
        print("="*70)
        print("1. Criar nova locação")
        print("2. Listar locações ativas")
        print("3. Finalizar locação")
        print("4. Ver histórico de locações")
        print("5. Registrar pagamento")
        print("6. Ver pagamentos de uma locação")
        print("7. Voltar")
        print("="*70)

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            print("\n--- Criar Nova Locação ---")
            cpf = input("CPF do cliente: ").strip().replace(".", "").replace("-", "")
            placa = input("Placa do veículo: ").strip().upper()

            try:
                dias = int(input("Número de dias: ").strip())
                sistema.criar_locacao(cpf, placa, dias)
            except ValueError:
                print("[X] Valor inválido!")

        elif opcao == "2":
            sistema.listar_locacoes_ativas()

        elif opcao == "3":
            try:
                id_locacao = int(input("ID da locação a finalizar: ").strip())
                sistema.finalizar_locacao(id_locacao)
            except ValueError:
                print("[X] ID inválido!")

        elif opcao == "4":
            sistema.listar_historico_locacoes()

        elif opcao == "5":
            print("\n--- Registrar Pagamento ---")
            sistema.listar_locacoes_ativas()
            try:
                id_locacao = int(input("\nID da locação: ").strip())
                if sistema.usar_banco:
                    sistema.recarregar_formas_pagamento()
                sistema.listar_formas_pagamento()
                forma = input("Nome da forma de pagamento: ").strip()
                valor = float(input("Valor (R$): ").strip().replace(",", "."))
                comprovante = input("Número do comprovante (opcional): ").strip()
                obs = input("Observações (opcional): ").strip()
                sistema.registrar_pagamento(id_locacao, forma, valor, comprovante, obs)
            except ValueError:
                print("[X] ID ou valor inválido!")

        elif opcao == "6":
            try:
                id_locacao = int(input("\nID da locação para ver pagamentos: ").strip())
                sistema.listar_pagamentos_locacao(id_locacao)
            except ValueError:
                print("[X] ID inválido!")

        elif opcao == "7":
            break

        else:
            print("[X] Opção inválida!")


def carregar_dados_exemplo(sistema: SistemaLocacao):
    """Carrega alguns dados de exemplo para testes"""
    print("Carregando dados de exemplo...\n")
    
    # Adicionar veículos
    sistema.adicionar_veiculo("ABC1234", "Toyota", "Corolla", 2023, 150.00, "Prata", 15000.0)
    sistema.adicionar_veiculo("DEF5678", "Honda", "Civic", 2022, 180.00, "Preto", 28000.0)
    sistema.adicionar_veiculo("GHI9012", "Hyundai", "HB20", 2023, 120.00, "Branco", 8000.0)
    sistema.adicionar_veiculo("JKL3456", "Chevrolet", "Onix", 2022, 110.00, "Vermelho", 22000.0)
    
    # Adicionar clientes
    sistema.adicionar_cliente("João Silva", "12345678900", "11987654321", "joao@email.com", "01311100", "Avenida Paulista, 1578 - Bela Vista, São Paulo, SP", "15/05/1990")
    sistema.adicionar_cliente("Maria Santos", "98765432100", "11912345678", "maria@email.com", "01310100", "Avenida Paulista, 1000 - Bela Vista, São Paulo, SP", "22/08/1992")
    sistema.adicionar_cliente("Pedro Oliveira", "55555555500", "11988888888", "pedro@email.com", "01310200", "Avenida Paulista, 500, apt 202 - Bela Vista, São Paulo, SP", "10/03/1988")
    
    print("\n[OK] Dados de exemplo carregados com sucesso!\n")


if __name__ == "__main__":
    sistema = SistemaLocacao(usar_banco=True)
    
    print("\n  Bem-vindo ao Sistema de Locacao de Veiculos!\n")
    
    # Só carrega dados de exemplo se não estiver usando banco (dados em memória apenas)
    if not sistema.usar_banco:
        opcao = input("Deseja carregar dados de exemplo? (S/N): ").strip().upper()
        if opcao == "S":
            carregar_dados_exemplo(sistema)
        else:
            print()
    
    try:
        menu_principal(sistema)
    finally:
        sistema.fechar_conexao()
