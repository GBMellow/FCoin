from datetime import datetime, timedelta

class Validador:
    def __init__(self, chave_seletor):
        self.chave_seletor = chave_seletor
        self.ultima_transacao = None
        self.contador_transacoes = 0
    
    def validar_transacao(self, remetente, valor):
        if remetente.saldo < valor:
            return False
        
        horario_atual = datetime.now()
        if self.ultima_transacao is not None and horario_atual <= self.ultima_transacao:
            return False
        
        if self.contador_transacoes > 1000 and horario_atual.second == 0:
            return False
        
        if remetente.chave_seletor != self.chave_seletor:
            return False
        
        self.ultima_transacao = horario_atual
        self.contador_transacoes += 1
        return True

    def concluir_transacao(self, transacao):
        if self.validar_transacao(transacao.remetente, transacao.valor):
            transacao.status = 1  # Transação concluída com sucesso
        else:
            transacao.status = 2  # Transação não aprovada (erro)
        
        return transacao