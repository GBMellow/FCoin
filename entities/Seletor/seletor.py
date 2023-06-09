from typing import List, Tuple
from Validador.validador import Validador
import random
import time

class Seletor:
    def __init__(self):
        self.validadores = []

    def cadastrar_validador(self, validador: Validador):
        self.validadores.append(validador)

    def escolher_validadores(self, quantidade_minima: int) -> List[Tuple[Validador, float]]:
        if len(self.validadores) < quantidade_minima:
            # Colocar a transação em espera por no máximo 1 minuto
            time.sleep(60)

        validadores_escolhidos = []
        total_moedas = sum(validador.saldo for validador in self.validadores)

        for validador in self.validadores:
            chance = validador.saldo / total_moedas

            # Limitar o percentual de chance de escolha entre 5% e 40%
            chance = max(chance, 0.05)
            chance = min(chance, 0.4)

            validadores_escolhidos.append((validador, chance))

        return validadores_escolhidos

    def realizar_transacao(self, validadores_escolhidos: List[Tuple[Validador, float]]) -> bool:
        status_counts = {0: 0, 1: 0, 2: 0}

        for validador, _ in validadores_escolhidos:
            # Simulação do status da transação retornada pelo validador
            status = random.choices([0, 1, 2], weights=[0.4, 0.4, 0.2])[0]
            status_counts[status] += 1

        # Verificar se o consenso foi gerado com mais de 50% de um status
        max_status_count = max(status_counts.values())
        if max_status_count > sum(status_counts.values()) / 2:
            return True
        else:
            return False

    def distribuir_fcoints(self, validadores_escolhidos: List[Tuple[Validador, float]]):
        # Simulação da distribuição de FCoins para os validadores participantes
        for validador, _ in validadores_escolhidos:
            validador.saldo += 10

    def identificar_validador_inconsistente(self, validador: Validador):
        # Simulação da identificação de validadores inconsistentes
        validador.flag_alerta += 1
        if validador.flag_alerta > 2:
            self.validadores.remove(validador)
            validador.saldo = 0
