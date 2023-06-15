import random
import time

base_url = "http://localhost:5000"

import requests
from flask import Flask, jsonify, request
from validador import Validar

app = Flask(__name__)


class Seletor:
    def calcular_percentual_escolha(self, validador):
        log = f"calculando percentual validador {validador['id']}"
        self.salvar_eleicao(log)

        saldo_minimo = 100
        saldo_maximo = 100000
        percentual_minimo = 5
        percentual_maximo = 40

        # Garante que o saldo esteja dentro do intervalo
        saldo = max(saldo_minimo, min(validador["saldo"], saldo_maximo))

        # Calcula o percentual de escolha proporcional ao saldo
        percentual = ((saldo - saldo_minimo) / (saldo_maximo - saldo_minimo)) * (
            percentual_maximo - percentual_minimo
        ) + percentual_minimo

        log = f"percentual validador {validador['id']} = {percentual}"
        self.salvar_eleicao(log)

        return percentual

    def salvar_validador(self, validador):
        log = f"salvando alterações validador {validador['id']}"
        self.salvar_eleicao(log)
        requests.post(
            base_url
            + f"/validador/{validador['id']}/{validador['ultima_transacao']}/{validador['contador_transacoes']}/{validador['saldo']}/{validador['flags']}"
        )

    def eleger_validadores(self, transacao):
        quantidade_minima_validadores = 3
        quantidade_maxima_validadores = 5
        espera_maxima_segundos = 60
        validadores_disponiveis = []
        validar = Validar()

        # Recupera os validadores disponíveis com saldo mínimo suficiente
        validadores = requests.get(base_url + "/validador")
        objetosValidadores = validadores.json()

        log = f"todos os validadores disponiveis = {objetosValidadores}"
        self.salvar_eleicao(log)

        for validador in objetosValidadores:
            if validador["saldo"] >= 100 and validador["chave_seletor"] == "xyz":
                validadores_disponiveis.append(validador)

        log = f"validadores válidos para eleição {objetosValidadores}"
        self.salvar_eleicao(log)

        # Verifica se há a quantidade mínima de validadores disponíveis
        if len(validadores_disponiveis) < quantidade_minima_validadores:
            return None

        # Ordena os validadores disponíveis com base no saldo (do menor para o maior)
        validadores_ordenados = sorted(
            validadores_disponiveis, key=lambda v: v["saldo"]
        )
        log = f"validadores ordenados {validadores_ordenados}"
        self.salvar_eleicao(log)

        validadores_ordenados = validadores_ordenados[:quantidade_maxima_validadores]

        # Calcula o percentual de chance de escolha para cada validador
        percentuais_escolha = [
            self.calcular_percentual_escolha(v) for v in validadores_ordenados
        ]

        log = f"percentuais_escolha {percentuais_escolha}"
        self.salvar_eleicao(log)

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

        log = f"validadores selecionados {validadores_selecionados}"
        self.salvar_eleicao(log)

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

                if sucesso > erro:
                    maioria = 1
                else:
                    maioria = 2

                log = f"maioria escolheu status {maioria}"
                self.salvar_eleicao(log)

                for i in range(len(transacoes)):
                    if transacoes[i]["status"] != maioria:
                        validadores_selecionados[i]["flags"] += 1
                        validadores_selecionados[i]["contador_transacoes"] = 0

                        if validadores_selecionados[i]["flags"] >= 2:
                            validadores_selecionados[i]["saldo"] = 0
                            log = f"eliminando {validadores_selecionados[i]['id']}"
                            self.salvar_eleicao(log)
                    else:
                        quantidade = transacao["valor"]
                        validadores_selecionados[i]["saldo"] += quantidade
                        log = f"validador {validadores_selecionados[i]['id']} recebendo saldo = {quantidade}"
                        self.salvar_eleicao(log)

                        if validadores_selecionados[i]["flags"] != 0:
                            validadores_selecionados[i]["contador_transacoes"] += 1

                            log = f"aumentando transações totais validador {validadores_selecionados['id']}"
                            self.salvar_eleicao(log)

                            if (
                                validadores_selecionados[i]["contador_transacoes"]
                                == 1000
                            ):
                                validadores_selecionados[i]["flags"] = 0
                                validadores_selecionados[i]["contador_transacoes"] = 0

                                log = f"zerando flags transações totais validador {validadores_selecionados['id']}"
                                self.salvar_eleicao(log)

                    self.salvar_validador(validadores_selecionados[i])

                requests.post(base_url + f"/transacoes/{transacao['id']}/{maioria}")
                return True
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
            seletor = Seletor()
            transacao = requests.get(base_url + f"/transacoes/{id}")
            response = seletor.eleger_validadores(transacao.json())
            print("\n\nresponse: ", response)
            data = {"message": "transação validada com sucesso"}
            return jsonify(data)
        except Exception as e:
            data = {"message": "transação não validada"}
            return jsonify(e)
    else:
        return jsonify(["Method Not Allowed"])
