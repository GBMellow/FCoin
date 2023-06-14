from datetime import datetime

import requests

base_url = f"http://localhost:5000"

class Validar:
    def validar_transacao(self, validador, remetente_id, valor):
        remetente = requests.get(base_url + f"/cliente/{remetente_id}")
        remetente = remetente.json()
        if remetente is None:
            return False

        if remetente['qtdMoeda'] < valor:
            return False

        url = f"{base_url}/hora"
        horario_atual =  self.converter_data(self.get_data(url))
        print("\n\nself.ultima_transacao", type(validador['ultima_transacao']))
        print("\n\nhorario_atual", horario_atual)

        validador['ultima_transacao'] = self.converter_data(validador['ultima_transacao'])
        if validador['ultima_transacao'] is not None and horario_atual <= validador['ultima_transacao']:
            return False

        if validador['contador_transacoes'] > 1000 and horario_atual.second == 0:
            return False
        return True

    def concluir_transacao(self, transacao, validador):
        print("\n\nvalidador", validador)
        print("\n\ntransacao['remetente']", transacao['remetente'])
        print("\n\ntransacao['valor'])", transacao['valor'])
        if self.validar_transacao(validador, transacao['remetente'], transacao['valor']):
            transacao['status'] = 1  # Transação concluída com sucesso
        else:
            transacao['status'] = 2  # Transação não aprovada (erro)

    
    def converter_data(date):
        if type(date) == str:
            try:
                data_convertida = datetime.utcnow().strptime(date, "%Y-%m-%d %H:%M:%S.%f")
                return data_convertida
            except:
                raise Exception("Erro ao converter a data") 
        else:
            return date
        
    def get_data(url):
        response = requests.get(url)
        if(response.status_code == 200):
            return response.json()
        else:
            raise Exception("Erro ao trazer o horario_atual")

    