from datetime import datetime
from abc import ABC, abstractmethod

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self, cliente, numero):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(cliente, numero)
    
    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor > 0 and valor <= self.saldo:
            self.saldo -= valor
            return True
        else:
            raise ValueError("Saldo insuficiente para realizar o saque.")

    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            return True
        else:
            raise ValueError("Valor de depósito inválido.")
    
class ContaCorrente(Conta):
    def __init__(self, cliente, numero, limite=500, limite_saques=3):
        super().__init__(cliente, numero)
        self._limite = limite
        self._limite_saques = limite_saques
        self._saldo_real = 0  # Saldo real
        self._saldo_efetivo = 0  # Saldo efetivo considerando o limite

    @property
    def limite(self):
        return self._limite

    @property
    def limite_saques(self):
        return self._limite_saques

    @property
    def saldo(self):
        return self._saldo_real

    @saldo.setter
    def saldo(self, valor):
        self._saldo_real = valor
        self._saldo_efetivo = self._saldo_real + self._limite

    def sacar(self, valor):
        if valor > 0 and self._saldo_efetivo >= valor:
            self.saldo -= valor  # Atualiza o saldo real e efetivo
            return True
        else:
            raise ValueError("Saldo insuficiente para realizar o saque.")

    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor  # Atualiza o saldo real e efetivo
            return True
        else:
            raise ValueError("Valor de depósito inválido.")

    
class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self.transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )
        
class Transacao(ABC):
    @abstractmethod
    def registrar(self, conta):
        pass

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

# Função para validar CPF
def validar_cpf(cpf):
    # Elimina CPFs invalidos conhecidos
    invalidos = ['00000000000', '11111111111', '22222222222', '33333333333', '44444444444', '55555555555',
                 '66666666666', '77777777777', '88888888888', '99999999999']
    if cpf in invalidos:
        return False

    # Valida tamanho do CPF
    if len(cpf) != 11:
        return False

    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = 11 - (soma % 11)
    if resto == 10 or resto == 11:
        resto = 0
    if resto != int(cpf[9]):
        return False

    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = 11 - (soma % 11)
    if resto == 10 or resto == 11:
        resto = 0
    if resto != int(cpf[10]):
        return False

    return True

# Função para imprimir o extrato
def imprimir_extrato(conta):
    extrato = ""
    for transacao in conta.historico.transacoes:
        extrato += f"{transacao['tipo']}: R$ {transacao['valor']:.2f} em {transacao['data']}\n"
    extrato += f"Saldo atual: R$ {conta.saldo:.2f}"
    print(extrato)

# Lista para armazenar os usuários do banco
usuarios = []

# Função para cadastrar um novo usuário
def cadastrar_usuario():
    nome = input("Digite o nome do usuário: ")
    data_nascimento = input("Digite a data de nascimento do usuário (DD/MM/AAAA): ")
    cpf = input("Digite o CPF do usuário: ")

    # Validação do CPF
    while not validar_cpf(cpf):
        print("CPF inválido. Por favor, digite novamente.")
        cpf = input("Digite o CPF do usuário: ")

    endereco = input("Digite o endereço do usuário (logradouro, número - bairro - cidade/sigla - estado): ")

    return PessoaFisica(nome, data_nascimento, cpf, endereco)

# Lista para armazenar as contas bancárias
contas = []

# Variável para controlar o número da próxima conta
prox_numero_conta = 1 

# Função para cadastrar uma nova conta bancária
def cadastrar_conta_bancaria(usuario):
    global prox_numero_conta
    conta = ContaCorrente(usuario, prox_numero_conta)
    usuario.adicionar_conta(conta)
    prox_numero_conta += 1
    print("Conta bancária cadastrada com sucesso.")

# Função para listar os usuários e suas contas
def listar_usuarios_contas(cpf):
    for usuario in usuarios:
        if isinstance(usuario, PessoaFisica) and usuario.cpf == cpf:
            print(f"Nome: {usuario.nome} | CPF: {usuario.cpf}")
            print("Contas vinculadas:")
            for conta in usuario.contas:
                print(f"Agência: {conta.agencia} | Número da conta: {conta.numero}")
            print("--------------------")
            return
    print("Não foi encontrado nenhum usuário com o CPF fornecido.")

# Menu de operações do banco
menu = """
[1] Depositar
[2] Sacar
[3] Extrato
[4] Cadastrar Usuário
[5] Cadastrar Conta Bancária
[6] Listar Usuários e Contas
[7] Sair

=> """

# Loop principal do programa
while True:
    opcao = input(menu)

    if opcao == "1":
        cpf = input("Digite o CPF do titular da conta: ")
        for usuario in usuarios:
            if isinstance(usuario, PessoaFisica) and usuario.cpf == cpf:
                try:
                    valor_deposito = float(input("Digite o valor a ser depositado: "))
                    deposito = Deposito(valor_deposito)
                    usuario.realizar_transacao(usuario.contas[0], deposito)
                    print(f'Depósito de R$ {valor_deposito:.2f} realizado com sucesso.')
                except ValueError as e:
                    print(e)
                break
        else:
            print("Não foi encontrado nenhum usuário com o CPF fornecido.")
  
    elif opcao == "2":
        cpf = input("Digite o CPF do titular da conta: ")
        for usuario in usuarios:
            if isinstance(usuario, PessoaFisica) and usuario.cpf == cpf:
                try:
                    valor_saque = float(input("Digite o valor a ser sacado: "))
                    saque = Saque(valor_saque)
                    usuario.realizar_transacao(usuario.contas[0], saque)
                    print(f'Saque de R$ {valor_saque:.2f} realizado com sucesso.')
                except ValueError as e:
                    print(e)
                break
        else:
            print("Não foi encontrado nenhum usuário com o CPF fornecido.")
        
    elif opcao == "3":
        cpf = input("Digite o CPF do titular da conta: ")
        for usuario in usuarios:
            if isinstance(usuario, PessoaFisica) and usuario.cpf == cpf:
                imprimir_extrato(usuario.contas[0])
                break
        else:
            print("Não foi encontrado nenhum usuário com o CPF fornecido.")
    
    elif opcao == "4":
        usuario = cadastrar_usuario()
        usuarios.append(usuario)
        print("Usuário cadastrado com sucesso.")
    
    elif opcao == "5":
        cpf = input("Digite o CPF do titular da conta: ")
        for usuario in usuarios:
            if isinstance(usuario, PessoaFisica) and usuario.cpf == cpf:
                cadastrar_conta_bancaria(usuario)
                break
        else:
            print("Não foi encontrado nenhum usuário com o CPF fornecido.")
        
    elif opcao == "6":
        cpf = input("Digite o CPF do usuário para listar suas contas: ")
        listar_usuarios_contas(cpf)
   
    elif opcao == "7":
        print("Obrigado por utilizar nosso banco, até mais...")
        break

    else:
        print("Operação inválida, por favor selecione novamente a operação desejada.")
