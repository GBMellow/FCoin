from datetime import datetime

import requests

from entities.eleicao import base_url
from entities.gerenciador.main import Validador


class Validar:
    def validar_transacao(validador, remetente_id, valor):
        remetente = requests.get(base_url + f"/cliente/{remetente_id}")
        if remetente is None:
            return False

        if remetente.qtdMoeda < valor:
            return False

        horario_atual = datetime.now()
        print("\n\nself.ultima_transacao", type(validador.ultima_transacao))
        print("\n\nhorario_atual", horario_atual)

        if type(validador.ultima_transacao) == str:
            validador.ultima_transacao = datetime.utcnow().strptime(
                validador.ultima_transacao, "%Y-%m-%d %H:%M:%S.%f"
            )
        else:
            pass
        if validador.ultima_transacao is not None and horario_atual <= validador.ultima_transacao:
            return False

        if validador.contador_transacoes > 1000 and horario_atual.second == 0:
            return False
        return True

    def concluir_transacao(self, transacao, validador: Validador):
        if self.validar_transacao(validador,transacao.remetente, transacao.valor):
            transacao.status = 1  # Transação concluída com sucesso
        else:
            transacao.status = 2  # Transação não aprovada (erro)

        return transacao
