from datetime import datetime

import requests
from flask import Flask
from entities.eleicao import base_url
from entities.gerenciador.main import Validador

base_url = f"http://192.168.15.17:5000"

class Validar:
    def validar_transacao(self,validador, remetente_id, valor):
        remetente = requests.get(base_url + f"/cliente/{remetente_id}")
        if remetente is None:
            return False

        if remetente.qtdMoeda < valor:
            return False

        url = f"{base_url}/hora"
        horario_atual =  self.converter_data(requests.get(url))
        
        print("\n\nself.ultima_transacao", type(validador.ultima_transacao))
        print("\n\nhorario_atual", horario_atual)

       
        validador.ultima_transacao = self.converter_data(validador.ultima_transacao)
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
    
    def converter_data(date):
        if type(date) == str:
            return datetime.utcnow().strptime(date, "%Y-%m-%d %H:%M:%S.%f")
        else:
            return date
      
    