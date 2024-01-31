import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime


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


class PessoaJuridica(Cliente):
    def __init__(self, nome_empresa, cnpj, endereco):
        super().__init__(endereco)
        self.nome_empresa = nome_empresa
        self.cnpj = cnpj


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

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
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@","Seu saldo = ", saldo)

        elif valor > 0:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===", saldo, "Valor Restante")
            return True

        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")

        elif excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
         return f"""
Agência:   {self.agencia}
C/C:       {self.numero}
Titular:   {self.cliente.nome}
""".strip()


class ContaPoupanca(Conta):
    def __init__(self, numero, cliente):
        super().__init__(numero, cliente)

    def sacar(self, valor):
        if valor > 0:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===", self.saldo, "Valor Restante")
            return True
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")

        return False


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )


class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(cls, conta):
        pass


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


def menu():
    menu = """\n
    =========== Sejam Bem Vindo ==========
    =========== Banco Tabajara ===========
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta corrente
    [np]\tNova conta poupança
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    ======================================
    => """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf_cnpj, clientes):
    clientes_filtrados = [cliente for cliente in clientes if hasattr(cliente, 'cpf') and cliente.cpf == cpf_cnpj]
    clientes_filtrados += [cliente for cliente in clientes if hasattr(cliente, 'cnpj') and cliente.cnpj == cpf_cnpj]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    # FIXME: não permite cliente escolher a conta
    return cliente.contas[0]


def depositar(clientes):
    cpf_cnpj = input("Informe o CPF ou CNPJ do cliente: ")
    cliente = filtrar_cliente(cpf_cnpj, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf_cnpj = input("Informe o CPF ou CNPJ do cliente: ")
    cliente = filtrar_cliente(cpf_cnpj, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cpf_cnpj = input("Informe o CPF ou CNPJ do cliente: ")
    cliente = filtrar_cliente(cpf_cnpj, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n============== EXTRATO ==============")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("======================================")

def criar_cliente(clientes):
    cpf_cnpj = input("Informe o CPF ou CNPJ (somente número): ")
    cliente = filtrar_cliente(cpf_cnpj, clientes)

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF ou CNPJ! @@@")
        return

    while True:
        tipo_cliente = input("Informe o tipo de cliente (1 para física, 2 para jurídica): ")

        if tipo_cliente == "1":
            nome = input("Informe o nome completo: ")
            data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
            endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")
            cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf_cnpj, endereco=endereco)
            break
        elif tipo_cliente == "2":
            nome_empresa = input("Informe o nome da empresa: ")
            endereco = input("Informe o endereço da empresa (logradouro, nro - bairro - cidade/sigla estado): ")
            cliente = PessoaJuridica(nome_empresa=nome_empresa, cnpj=cpf_cnpj, endereco=endereco)
            break
        else:
            print("\n@@@ Opção inválida! Por favor, informe 1 para física ou 2 para jurídica. @@@")
            
    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")

def criar_conta(numero_conta, clientes, contas):
    cpf_cnpj = input("Informe o CPF ou CNPJ do cliente: ")
    cliente = filtrar_cliente(cpf_cnpj, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    while True:
        tipo_conta = input("Informe o tipo de conta (1 para corrente, 2 para poupanca): ")

        if tipo_conta == "1":
            conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
            break
        elif tipo_conta == "2":
            conta = ContaPoupanca.nova_conta(cliente=cliente, numero=numero_conta)
            break
        else:
            print("\n@@@ Tipo de conta inválido! Por favor, informe 1 para corrente ou 2 para poupança. @@@")
            
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n==== Conta criada com sucesso!  ====")

def listar_contas(contas):
    for conta in contas:
        print("=" * 38)
        print(f"Agência:        {conta.agencia}")
        print(f"C/{'C' if isinstance(conta, ContaCorrente) else 'P'}:   {conta.numero}")

        if isinstance(conta, ContaCorrente) or isinstance(conta, ContaPoupanca):
            if isinstance(conta.cliente, PessoaFisica):
                print(f"Titular:        {conta.cliente.nome}")
            elif isinstance(conta.cliente, PessoaJuridica):
                print(f"Nome Empresa:   {conta.cliente.nome_empresa.upper()}")

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu().lower()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)
            
        elif opcao == "np": 
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            print(""" 
====== Banco Tabajara Agradece =======
========= Volte Sempre ===============
                 
                      """)
            break

        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")

if __name__ == "__main__":
    main()
