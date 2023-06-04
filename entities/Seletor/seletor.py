import random


class Seletor:
    def __init__(self):
        self.validadores = []
        self.transacoes_em_espera = []
        self.flags = {}

    def cadastrar_validador(self, validador):
        self.validadores.append(validador)
        self.flags[validador] = 0

    def selecionar_validadores(self, quantidade_minima):
        if len(self.validadores) < quantidade_minima:
            return None  # Transação em espera, pois não há validadores suficientes

        validadores_selecionados = random.sample(self.validadores, random.randint(quantidade_minima, 5))
        return validadores_selecionados

    def gerar_consenso(self, validadores_selecionados):
        aprovadas = 0
        nao_aprovadas = 0

        for validador in validadores_selecionados:
            chance_escolha = self.calcular_chance_escolha(validador)
            if random.random() <= chance_escolha:
                if validador.validar_transacao():
                    aprovadas += 1
                    self.flags[validador] = max(0, self.flags[validador] - 1)
                else:
                    nao_aprovadas += 1
                    self.flags[validador] += 1

        if aprovadas > nao_aprovadas:
            return 1  # Transação aprovada
        else:
            return 2  # Transação não aprovada

    def calcular_chance_escolha(self, validador):
        saldo_validador = validador.saldo
        total_saldos = sum(v.saldo for v in self.validadores)
        percentual = (saldo_validador / total_saldos) * 100
        percentual = max(5, min(40, percentual))
        return percentual

    def distribuir_fcoins(self, validadores_selecionados):
        total_fcoins = 100  # Quantidade de FCoins a ser distribuída

        for validador in validadores_selecionados:
            chance_escolha = self.calcular_chance_escolha(validador)
            fcoins_recebidas = (chance_escolha / 100) * total_fcoins
            validador.saldo += fcoins_recebidas

    def remover_validador(self, validador):
        self.validadores.remove(validador)
        del self.flags[validador]
