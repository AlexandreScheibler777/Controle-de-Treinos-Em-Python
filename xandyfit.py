"""XandyFit - Meu Controle de Treinos.

Projeto de orientação a objetos para execução no terminal.
Autor: Alexandre Silva Scheibler.
"""

from abc import ABC, abstractmethod
import os
import sys


# As cores são opcionais: se o terminal não suportar, o texto continua legível.
def configurar_cores():
    if os.environ.get("NO_COLOR") or not sys.stdout.isatty():
        return False
    if os.name == "nt":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            saida = kernel32.GetStdHandle(-11)
            modo = ctypes.c_uint()
            if not kernel32.GetConsoleMode(saida, ctypes.byref(modo)):
                return False
            return bool(kernel32.SetConsoleMode(saida, modo.value | 0x0004))
        except (OSError, AttributeError):
            return False
    return os.environ.get("TERM", "") != "dumb"


USAR_CORES = configurar_cores()


class Cor:
    RESET = "\033[0m" if USAR_CORES else ""
    AZUL = "\033[94m" if USAR_CORES else ""
    VERDE = "\033[92m" if USAR_CORES else ""
    AMARELO = "\033[93m" if USAR_CORES else ""
    VERMELHO = "\033[91m" if USAR_CORES else ""
    CIANO = "\033[96m" if USAR_CORES else ""


def colorir(texto, cor):
    return f"{cor}{texto}{Cor.RESET}"


def pedir_texto(mensagem):
    while True:
        texto = input(mensagem).strip()
        if texto:
            return texto
        print(colorir("O campo não pode ficar vazio.", Cor.VERMELHO))


def pedir_numero(mensagem, minimo=0):
    while True:
        try:
            valor = float(input(mensagem).strip().replace(",", "."))
            if not (minimo <= valor < float("inf")):
                raise ValueError
            return valor
        except ValueError:
            print(colorir(f"Digite um número válido (mínimo: {minimo}).", Cor.VERMELHO))


# R4: interface com um método abstrato, implementado nas duas modalidades.
class Agendavel(ABC):
    @abstractmethod
    def agendar(self, horario):
        pass


# R1: classe mãe abstrata com atributos, construtor, método abstrato e normal.
class Atividade(ABC):
    def __init__(self, codigo, nome, valor_base):
        if not isinstance(codigo, int) or codigo <= 0:
            raise ValueError("O código precisa ser um inteiro positivo.")
        self.__codigo = codigo
        self.nome = nome
        self.valor_base = valor_base
        self._horario = "Ainda não agendado"

    @property
    def codigo(self):
        return self.__codigo

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, novo_nome):
        if not isinstance(novo_nome, str) or not novo_nome.strip():
            raise ValueError("O nome da atividade não pode ficar vazio.")
        self.__nome = novo_nome.strip()

    @property
    def valor_base(self):
        return self.__valor_base

    @valor_base.setter
    def valor_base(self, novo_valor):
        if not isinstance(novo_valor, (int, float)) or not (0 <= novo_valor < float("inf")):
            raise ValueError("O valor não pode ser negativo ou inválido.")
        self.__valor_base = float(novo_valor)

    @property
    def horario(self):
        return self._horario

    @abstractmethod
    def custo_mensal(self):
        pass

    def resumo_mensal(self):
        # Método normal que usa o método abstrato (R1 e R5).
        return f"{self.nome}: R$ {self.custo_mensal():.2f} por mês"


# R2: primeira filha concreta, com atributo próprio e cálculo diferente.
class Musculacao(Atividade, Agendavel):
    def __init__(self, codigo, nome, valor_base, dias_semana):
        super().__init__(codigo, nome, valor_base)
        self.dias_semana = dias_semana

    @property
    def dias_semana(self):
        return self.__dias_semana

    @dias_semana.setter
    def dias_semana(self, dias):
        if not isinstance(dias, int) or not 1 <= dias <= 7:
            raise ValueError("A frequência deve ser de 1 a 7 dias por semana.")
        self.__dias_semana = dias

    def custo_mensal(self):
        # Cada dia semanal contratado acrescenta R$ 12 ao valor-base.
        return self.valor_base + self.dias_semana * 12

    def agendar(self, horario):
        if not horario.strip():
            raise ValueError("Informe um horário.")
        self._horario = horario.strip()
        return f"Treino de musculação agendado: {self._horario}."

    def __str__(self):
        return (f"[{self.codigo}] MUSCULAÇÃO | {self.nome} | "
                f"{self.dias_semana} dia(s)/semana | {self.horario} | "
                f"R$ {self.custo_mensal():.2f}/mês")


# R2 e R4: segunda filha, que também implementa a interface Agendavel.
class Natacao(Atividade, Agendavel):
    def __init__(self, codigo, nome, valor_base, aulas_semana):
        super().__init__(codigo, nome, valor_base)
        self.aulas_semana = aulas_semana

    @property
    def aulas_semana(self):
        return self.__aulas_semana

    @aulas_semana.setter
    def aulas_semana(self, aulas):
        if not isinstance(aulas, int) or not 1 <= aulas <= 7:
            raise ValueError("A frequência deve ser de 1 a 7 aulas por semana.")
        self.__aulas_semana = aulas

    def custo_mensal(self):
        # Cada aula semanal contratada acrescenta R$ 25 ao valor-base.
        return self.valor_base + self.aulas_semana * 25

    def agendar(self, horario):
        if not horario.strip():
            raise ValueError("Informe um horário.")
        self._horario = horario.strip()
        return f"Aula de natação agendada: {self._horario}."

    def __str__(self):
        return (f"[{self.codigo}] NATAÇÃO | {self.nome} | "
                f"{self.aulas_semana} aula(s)/semana | {self.horario} | "
                f"R$ {self.custo_mensal():.2f}/mês")


class XandyFit:
    def __init__(self):
        # R6: lista de objetos com três atividades iniciais.
        self._atividades = [
            Musculacao(1, "Treino de força do Xandy", 80, 4),
            Natacao(2, "Natação para condicionamento", 100, 2),
            Musculacao(3, "Treino de resistência", 70, 3),
        ]
        self._proximo_codigo = 4

    def buscar_objeto(self, termo):
        termo = termo.strip().casefold()
        return [atividade for atividade in self._atividades
                if str(atividade.codigo) == termo or termo in atividade.nome.casefold()]

    def cadastrar(self):
        print(colorir("\n--- CADASTRAR ATIVIDADE ---", Cor.CIANO))
        print("1 - Musculação")
        print("2 - Natação")
        tipo = input("Escolha a modalidade: ").strip()
        if tipo not in ("1", "2"):
            print(colorir("Modalidade inválida. Cadastro cancelado.", Cor.VERMELHO))
            return
        nome = pedir_texto("Nome do treino/atividade: ")
        base = pedir_numero("Valor-base mensal (R$): ")
        if tipo == "1":
            dias = pedir_frequencia("Dias de treino por semana (1 a 7): ")
            novo = Musculacao(self._proximo_codigo, nome, base, dias)
        else:
            aulas = pedir_frequencia("Aulas de natação por semana (1 a 7): ")
            novo = Natacao(self._proximo_codigo, nome, base, aulas)
        self._atividades.append(novo)
        self._proximo_codigo += 1
        print(colorir(f"Atividade cadastrada com código {novo.codigo}!", Cor.VERDE))

    def listar(self):
        print(colorir("\n--- MEUS TREINOS ---", Cor.CIANO))
        if not self._atividades:
            print(colorir("Nenhuma atividade cadastrada.", Cor.AMARELO))
            return
        # R5: polimorfismo; tipos diferentes respondem ao mesmo método.
        for atividade in self._atividades:
            print(atividade)  # R8: utiliza __str__.
            print("   " + atividade.resumo_mensal())

    def buscar(self):
        termo = pedir_texto("Digite o nome ou código para buscar: ")
        encontrados = self.buscar_objeto(termo)
        if not encontrados:
            print(colorir("Nenhuma atividade encontrada.", Cor.AMARELO))
        for atividade in encontrados:
            print(atividade)

    def remover(self):
        codigo = input("Código da atividade que deseja remover: ").strip()
        encontrados = [a for a in self._atividades if str(a.codigo) == codigo]
        if not encontrados:
            print(colorir("Código não encontrado.", Cor.AMARELO))
            return
        self._atividades.remove(encontrados[0])
        print(colorir("Atividade removida com sucesso!", Cor.VERDE))

    def acao(self):
        codigo = input("Código da atividade que deseja agendar: ").strip()
        encontrados = [a for a in self._atividades if str(a.codigo) == codigo]
        if not encontrados:
            print(colorir("Código não encontrado.", Cor.AMARELO))
            return
        horario = pedir_texto("Informe dia e horário (ex.: segunda 18h): ")
        print(colorir(encontrados[0].agendar(horario), Cor.VERDE))
        print(colorir(encontrados[0].resumo_mensal(), Cor.AZUL))

    def menu(self):
        while True:
            print(colorir("\n=================================", Cor.AZUL))
            print(colorir("  XANDYFIT - MEU CONTROLE DE TREINOS", Cor.CIANO))
            print(colorir("=================================", Cor.AZUL))
            print("1 - Cadastrar atividade")
            print("2 - Listar meus treinos")
            print("3 - Buscar atividade")
            print("4 - Remover atividade")
            print("5 - Agendar treino/aula")
            print("0 - Sair")
            escolha = input(colorir("Escolha uma opção: ", Cor.AMARELO)).strip()
            if escolha == "1":
                self.cadastrar()
            elif escolha == "2":
                self.listar()
            elif escolha == "3":
                self.buscar()
            elif escolha == "4":
                self.remover()
            elif escolha == "5":
                self.acao()
            elif escolha == "0":
                print(colorir("Até o próximo treino, Xandy!", Cor.VERDE))
                break
            else:
                print(colorir("Opção inválida. Tente novamente.", Cor.VERMELHO))


def pedir_frequencia(mensagem):
    while True:
        numero = pedir_numero(mensagem, minimo=1)
        if numero.is_integer() and 1 <= numero <= 7:
            return int(numero)
        print(colorir("Digite um número inteiro entre 1 e 7.", Cor.VERMELHO))


if __name__ == "__main__":
    try:
        XandyFit().menu()
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma encerrado.")
