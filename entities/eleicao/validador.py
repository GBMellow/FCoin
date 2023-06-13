from datetime import datetime

from entities.gerenciador.main import Validador
from entities.eleicao import base_url

import requests
class Validar:
    def validar_transacao(self, remetente_id, valor):
        remetente = requests.get(base_url + f"/cliente/{remetente_id}")
        if remetente is None:
            return False

        if remetente.qtdMoeda < valor:
            return False

        horario_atual = datetime.now()
        print("\n\nself.ultima_transacao", type(self.ultima_transacao))
        print("\n\nhorario_atual", horario_atual)

        if type(self.ultima_transacao) == str:
            self.ultima_transacao = datetime.utcnow().strptime(self.ultima_transacao, '%Y-%m-%d %H:%M:%S.%f')
        else:
            pass
        if self.ultima_transacao is not None and horario_atual <= self.ultima_transacao:
            return False

        if self.contador_transacoes > 1000 and horario_atual.second == 0:
            return False

        self.ultima_transacao = horario_atual
        self.contador_transacoes += 1
        return True

    def concluir_transacao(self, transacao, validador: Validador):
        if self.validar_transacao(transacao.remetente, transacao.valor):
            transacao.status = 1  # Transação concluída com sucesso
        else:
            transacao.status = 2  # Transação não aprovada (erro)

        return transacao

