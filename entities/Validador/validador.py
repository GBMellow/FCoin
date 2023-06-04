import time

class Validador:
    def __init__(self, chave_unica):
        self.chave_unica = chave_unica
        self.ultima_transacao = None
        self.num_transacoes = 0

    def validar_transacao(self, remetente, valor):
        if remetente.saldo >= valor and self.validar_horario() and self.validar_limite_transacoes():
            self.ultima_transacao = time.time()
            self.num_transacoes += 1
            if self.chave_unica == remetente.chave_unica:
                return 1  # Transação concluída com sucesso
            else:
                return 2  # Transação não concluída devido à chave inválida
        else:
            return 0  # Transação não executada

    def validar_horario(self):
        horario_atual = time.time()
        if self.ultima_transacao is None or self.ultima_transacao < horario_atual:
            return True
        return False

    def validar_limite_transacoes(self):
        if self.num_transacoes < 1000:
            return True
        else:
            proximo_minuto = int(time.time()) + 60
            while int(time.time()) < proximo_minuto:
                pass
            self.num_transacoes = 0
            return False