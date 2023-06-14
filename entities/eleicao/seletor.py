import random
import time
import json

import requests

base_url = f"http://localhost:5000"

from validador import Validar
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

class Seletor:
    def calcular_percentual_escolha(self, validador):
        log = "\n\nvalidador", validador
        self.salvar_eleicao(Seletor, log)

        saldo_minimo = 100
        saldo_maximo = 100000
        percentual_minimo = 5
        percentual_maximo = 40

        # Garante que o saldo esteja dentro do intervalo
        saldo = max(saldo_minimo, min(validador['saldo'], saldo_maximo))

        # Calcula o percentual de escolha proporcional ao saldo
        percentual = ((saldo - saldo_minimo) / (saldo_maximo - saldo_minimo)) * (
            percentual_maximo - percentual_minimo
        ) + percentual_minimo

        return percentual

    def receber_fcoins(self, quantidade, validador):
        validador['saldo'] += quantidade

    def verificar_eliminar_validador(self, validador):
        if validador.flags >= 2:
            requests.delete(base_url + f"/validador/{validador['id']}")

    def eleger_validadores(self, transacao):
        quantidade_minima_validadores = 3
        quantidade_maxima_validadores = 5
        espera_maxima_segundos = 60
        validadores_disponiveis = []
        validar = Validar()

        # Recupera os validadores disponíveis com saldo mínimo suficiente
        validadores = requests.get(base_url + "/validador")
        objetosValidadores = validadores.json()
        print("\n\nobjetosValidadores: ", objetosValidadores)
        for validador in objetosValidadores:            
            print("\n\nvalidador: ", validador)
            if validador['saldo'] >= 100:
                validadores_disponiveis.append(validador)

        print("\n\nvalidadores_disponiveis", validadores_disponiveis)

        # Verifica se há a quantidade mínima de validadores disponíveis
        if len(validadores_disponiveis) < quantidade_minima_validadores:
            return None

        # Ordena os validadores disponíveis com base no saldo (do menor para o maior)
        validadores_ordenados = sorted(validadores_disponiveis, key=lambda v: v['saldo'])
        print("\n\nvalidadores_ordenados", validadores_ordenados)

        validadores_ordenados = validadores_ordenados[:quantidade_maxima_validadores]

        # Calcula o percentual de chance de escolha para cada validador
        percentuais_escolha = [
            self.calcular_percentual_escolha(Seletor, v) for v in validadores_ordenados
        ]

        # Limita o número de validadores ao máximo permitido
        percentuais_escolha = percentuais_escolha
        print("\n\npercentuais_escolha", percentuais_escolha)

        # Normaliza os percentuais para que somem 100
        soma_percentuais = sum(percentuais_escolha)
        percentuais_normalizados = [
            (p / soma_percentuais) * 100 for p in percentuais_escolha
        ]

        # Escolhe aleatoriamente entre os validadores com base nos percentuais
        validadores_selecionados = random.choices(
            validadores_ordenados[:quantidade_maxima_validadores],
            percentuais_normalizados,
            k=quantidade_minima_validadores,
        )
        print("\n\nvalidadores_selecionados", validadores_selecionados)
        print("\n\ntransacao", transacao)

        # Atualiza o contador dos validadores selecionados
        for validador in validadores_selecionados:
            validador['contador_transacoes'] += 1

        # Aguarda por até um minuto para concluir a transação
        tempo_espera = 0
        while tempo_espera < espera_maxima_segundos:
            transacoes = [
                validar.concluir_transacao(transacao, validador)
                for validador in validadores_selecionados
            ]

            if transacoes:
                sucesso = transacoes.count(1)
                erro = transacoes.count(2)

                maioria = 0

                if sucesso > erro:
                    maioria = 1
                else:
                    maioria = 2

                for i in range(len(transacoes)):
                    if transacoes[i]['status'] != maioria:
                        validadores_selecionados[i]['flags'] += 1
                        if validadores_selecionados[i]['flags'] >= 2:
                            validadores_selecionados[i]['saldo'] = 0
                    else:
                        pass

                return True
                #requests.delete(base_url + f"/validador/{validador.id}")
            else:
                time.sleep(1)
                tempo_espera += 1

        # Caso o tempo de espera seja excedido, retorna None (transação em espera)
        return None

    def salvar_eleicao(self, log: str):
        horario = self.get_horario()
        requests.post(base_url + f"/eleicao/{log}/{horario}")

    @staticmethod
    def get_horario():
        return requests.get(base_url + "/hora")

@app.route("/transacao/<int:id>", methods=["POST"])
def ValidarTransacao(id):
    if request.method == "POST":
        try:
            transacao = requests.get(base_url + f"/transacoes/{id}")
            response = Seletor.eleger_validadores(Seletor, transacao.json())
            print("\n\nresponse: ", response)
            data = {"message": "transação validada com sucesso"}
            return jsonify(data)
        except Exception as e:
            data = {"message": "transação não validada"}
            return jsonify(e)
    else:
        return jsonify(["Method Not Allowed"])