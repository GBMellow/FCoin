from dataclasses import dataclass
from datetime import datetime
import time
import random
import sys

from flask import Flask, jsonify, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

@dataclass
class Validador(db.Model):
    id: int
    chave_seletor: str
    ultima_transacao: datetime
    contador_transacoes: int
    saldo: int
    flags: int

    id = db.Column(db.Integer, primary_key=True)
    chave_seletor = db.Column(db.String(20), unique=False, nullable=False)
    ultima_transacao = db.Column(db.String(20), unique=False, nullable=False)
    contador_transacoes = db.Column(db.Integer, unique=False, nullable=False)
    saldo = db.Column(db.Integer, unique=False, nullable=False)
    flags = db.Column(db.Integer, unique=False, nullable=False)

    def validar_transacao(self, remetente_id, valor):
        remetente = Cliente.query.get(remetente_id)
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

    def concluir_transacao(self, transacao):
        if self.validar_transacao(transacao.remetente, transacao.valor):
            transacao.status = 1  # Transação concluída com sucesso
        else:
            transacao.status = 2  # Transação não aprovada (erro)

        return transacao

class Selecionar:
    def calcular_percentual_escolha(validador):

        print("\n\nvalidador", validador)

        saldo_minimo = 100
        saldo_maximo = 10000
        percentual_minimo = 5
        percentual_maximo = 40

        # Garante que o saldo esteja dentro do intervalo
        saldo = max(saldo_minimo, min(validador.saldo, saldo_maximo))

        # Calcula o percentual de escolha proporcional ao saldo
        percentual = (
            (saldo - saldo_minimo) / (saldo_maximo - saldo_minimo)
        ) * (percentual_maximo - percentual_minimo) + percentual_minimo

        return percentual

    def receber_fcoins(self, quantidade):
        self.saldo += quantidade

    def verificar_eliminar_validador(self):
        if self.flags > 2:
            self.saldo = 0  # Perde todo o saldo
            db.session.delete(self)
            db.session.commit()

    @staticmethod
    def eleger_validadores(transacao):

        quantidade_minima_validadores = 3
        quantidade_maxima_validadores = 5
        espera_maxima_segundos = 60

        # Recupera os validadores disponíveis com saldo mínimo suficiente
        validadores_disponiveis = Validador.query.filter(Validador.saldo >= 100).all()
        print("\n\nvalidadores_disponiveis", validadores_disponiveis)

        # Verifica se há a quantidade mínima de validadores disponíveis
        if len(validadores_disponiveis) < quantidade_minima_validadores:
            return None

        # Ordena os validadores disponíveis com base no saldo (do menor para o maior)
        validadores_ordenados = sorted(validadores_disponiveis, key=lambda v: v.saldo)
        print("\n\nvalidadores_ordenados", validadores_ordenados)

        validadores_ordenados = validadores_ordenados[:quantidade_maxima_validadores]

        # Calcula o percentual de chance de escolha para cada validador
        percentuais_escolha = [
            Selecionar.calcular_percentual_escolha(v) for v in validadores_ordenados
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
            validadores_ordenados[:quantidade_maxima_validadores], percentuais_normalizados, k=quantidade_minima_validadores
        )
        print("\n\nvalidadores_selecionados", validadores_selecionados)
        print("\n\ntransacao", transacao)

        # Atualiza o contador dos validadores selecionados
        for validador in validadores_selecionados:
            validador.contador_transacoes += 1

        # Grava as alterações no banco de dados
        db.session.commit()
        
        # Aguarda por até um minuto para concluir a transação
        tempo_espera = 0
        while tempo_espera < espera_maxima_segundos:
            transacoes = [validador.concluir_transacao(transacao) for validador in validadores_selecionados]

            if transacoes:
                sucesso = transacoes.count(1)
                erro = transacoes.count(2)

                maioria = 0

                if sucesso > erro:
                    maioria = 1
                else:
                    maioria = 2

                for i in range(len(transacoes)):

                    if transacoes[i].status != maioria:
                        validadores_selecionados[i].flags += 1
                        if validadores_selecionados[i].flags >= 2:
                            validadores_selecionados[i].saldo = 0
                    else:
                        pass

                db.session.commit()
                return transacoes
            else:
                time.sleep(1)
                tempo_espera += 1

        # Caso o tempo de espera seja excedido, retorna None (transação em espera)
        return None

@dataclass
class Cliente(db.Model):
    id: int
    nome: str
    senha: int
    qtdMoeda: int

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), unique=False, nullable=False)
    senha = db.Column(db.String(20), unique=False, nullable=False)
    qtdMoeda = db.Column(db.Integer, unique=False, nullable=False)


class Seletor(db.Model):
    id: int
    nome: str
    ip: str

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), unique=False, nullable=False)
    ip = db.Column(db.String(15), unique=False, nullable=False)


class Transacao(db.Model):
    id: int
    remetente: int
    recebedor: int
    valor: int
    status: int

    id = db.Column(db.Integer, primary_key=True)
    remetente = db.Column(db.Integer, unique=False, nullable=False)
    recebedor = db.Column(db.Integer, unique=False, nullable=False)
    valor = db.Column(db.Integer, unique=False, nullable=False)
    horario = db.Column(db.DateTime, unique=False, nullable=False)
    status = db.Column(db.Integer, unique=False, nullable=False)


@app.before_first_request
def create_tables():
    db.create_all()


@app.route("/")
def index():
    return render_template("api.html")


@app.route("/cliente", methods=["GET"])
def ListarCliente():
    if request.method == "GET":
        clientes = Cliente.query.all()
        return jsonify(clientes)


@app.route("/cliente/<string:nome>/<string:senha>/<int:qtdMoeda>", methods=["POST"])
def InserirCliente(nome, senha, qtdMoeda):
    if request.method == "POST" and nome != "" and senha != "" and qtdMoeda != "":
        objeto = Cliente(nome=nome, senha=senha, qtdMoeda=qtdMoeda)
        db.session.add(objeto)
        db.session.commit()
        return jsonify(objeto)
    else:
        return jsonify(["Method Not Allowed"])


@app.route("/cliente/<int:id>", methods=["GET"])
def UmCliente(id):
    if request.method == "GET":
        objeto = Cliente.query.get(id)
        return jsonify(objeto)
    else:
        return jsonify(["Method Not Allowed"])


@app.route("/cliente/<int:id>/<int:qtdMoeda>", methods=["POST"])
def EditarCliente(id, qtdMoeda):
    if request.method == "POST":
        try:
            varId = id
            varqtdMoeda = qtdMoeda
            cliente = Cliente.query.filter_by(id=id).first()
            db.session.commit()
            cliente.qtdMoeda = qtdMoeda
            db.session.commit()
            return jsonify(cliente)
        except Exception as e:
            data = {"message": "Atualização não realizada"}
            return jsonify(data)
    else:
        return jsonify(["Method Not Allowed"])


@app.route("/cliente/<int:id>", methods=["DELETE"])
def ApagarCliente(id):
    if request.method == "DELETE":
        objeto = Cliente.query.get(id)
        db.session.delete(objeto)
        db.session.commit()

        data = {"message": "Cliente Deletado com Sucesso"}

        return jsonify(data)
    else:
        return jsonify(["Method Not Allowed"])


@app.route("/seletor", methods=["GET"])
def ListarSeletor():
    if request.method == "GET":
        seletores = Seletor.query.all()
        seletor_dict = []

        for seletor in seletores:
            seletor_obj = {"nome": seletor.nome, "ip": seletor.ip}
            seletor_dict.append(seletor_obj)

        return jsonify(seletor_dict)


@app.route("/seletor/<string:nome>/<string:ip>", methods=["POST"])
def InserirSeletor(nome, ip):
    if request.method == "POST" and nome != "" and ip != "":
        objeto = Seletor(nome=nome, ip=ip)
        db.session.add(objeto)
        db.session.commit()
        objeto_dict = {"nome": objeto.nome, "ip": objeto.ip}

        return jsonify(objeto_dict)
    else:
        return jsonify(["Method Not Allowed"])


@app.route("/seletor/<int:id>", methods=["GET"])
def UmSeletor(id):
    if request.method == "GET":
        produto = Seletor.query.get(id)
        return jsonify(produto)
    else:
        return jsonify(["Method Not Allowed"])


@app.route("/seletor/<int:id>/<string:nome>/<string:ip>", methods=["POST"])
def EditarSeletor(id, nome, ip):
    if request.method == "POST":
        try:
            varNome = nome
            varIp = ip
            validador = Seletor.query.filter_by(id=id).first()
            db.session.commit()
            validador.nome = varNome
            validador.ip = varIp
            db.session.commit()
            return jsonify(validador)
        except Exception as e:
            data = {"message": "Atualização não realizada"}
            return jsonify(data)
    else:
        return jsonify(["Method Not Allowed"])


@app.route("/seletor/<int:id>", methods=["DELETE"])
def ApagarSeletor(id):
    if request.method == "DELETE":
        objeto = Seletor.query.get(id)
        db.session.delete(objeto)
        db.session.commit()

        data = {"message": "Validador Deletado com Sucesso"}

        return jsonify(data)
    else:
        return jsonify(["Method Not Allowed"])


@app.route("/hora", methods=["GET"])
def horario():
    if request.method == "GET":
        objeto = datetime.now()
        return jsonify(objeto)


@app.route("/transacoes", methods=["GET"])
def ListarTransacoes():
    if request.method == "GET":
        transacoes = Transacao.query.all()
        transacoes_dict = []

        for transacao in transacoes:
            transacao_obj = {
                "id": transacao.id,
                "remetente": transacao.remetente,
                "recebedor": transacao.recebedor,
                "valor": transacao.valor,
                "status": transacao.status,
            }
            transacoes_dict.append(transacao_obj)
        return jsonify(transacoes_dict)


@app.route("/transacoes/<int:rem>/<int:reb>/<int:valor>", methods=["POST"])
def CriaTransacao(rem, reb, valor):
    if request.method == "POST":
        objeto = Transacao(
            remetente=rem, recebedor=reb, valor=valor, status=0, horario=datetime.now()
        )
        db.session.add(objeto)
        db.session.commit()

        objeto = Transacao.query.all()[-1]
        print("\n\nObjeto:", objeto.id)
        seletores = Seletor.query.all()
        for seletor in seletores:
            url = "http://" + seletor.ip + f"/transacao/{objeto.id}"
            requests.post(url)

        objeto_dict = {
            "rem": objeto.remetente,
            "reb": objeto.recebedor,
            "valor": objeto.valor
        }

        return jsonify(objeto_dict)
    else:
        return jsonify(["Method Not Allowed"])

@app.route("/transacao/<int:id>", methods=["POST"])
def ValidarTransacao(id):
    if request.method == "POST":
        try:
            objeto = Transacao.query.get(id)
            print("\n\nObjeto:", objeto)
            response = Selecionar.eleger_validadores(objeto)
            print("\n\nresponse: ", response)
            data = {"message": "transação validada com sucesso"}
            return jsonify(data)
        except Exception as e:
            data = {"message": "transação não validada"}
            return jsonify(e)
    else:
        return jsonify(["Method Not Allowed"])

@app.route("/transacoes/<int:id>", methods=["GET"])
def UmaTransacao(id):
    if request.method == "GET":
        transacao = Transacao.query.get(id)
        transacao_obj = {
            "id": transacao.id,
            "remetente": transacao.remetente,
            "recebedor": transacao.recebedor,
            "valor": transacao.valor,
            "status": transacao.status,
        }
        return jsonify(transacao_obj)
    else:
        return jsonify(["Method Not Allowed"])


@app.route("/transactions/<int:id>/<int:status>", methods=["POST"])
def EditaTransacao(id, status):
    if request.method == "POST":
        try:
            objeto = Transacao.query.filter_by(id=id).first()
            db.session.commit()
            objeto.id = id
            objeto.status = status
            db.session.commit()
            return jsonify(objeto)
        except Exception as e:
            data = {"message": "transação não atualizada"}
            return jsonify(data)
    else:
        return jsonify(["Method Not Allowed"])


@app.errorhandler(404)
def page_not_found(error):
    return render_template("page_not_found.html"), 404

@app.route("/validador", methods=["GET"])
def ListarValidador():
    if request.method == "GET":
        validadores = Validador.query.all()
        validador_dict = []

        for validador in validadores:
            validador_obj = {
                "id": validador.id,
                "chave_seletor": validador.chave_seletor,
                "ultima_transacao": validador.ultima_transacao,
                "contador_transacoes": validador.contador_transacoes,
                "saldo": validador.saldo,
                "flags": validador.flags,
            }
            validador_dict.append(validador_obj)

        return jsonify(validador_dict)


@app.route("/validador/<int:id>", methods=["GET"])
def UmValidador(id):
    if request.method == "GET":
        validador = Validador.query.get(id)
        return jsonify(validador)
    else:
        return jsonify(["Method Not Allowed"])


@app.route("/validador/<string:chave_seletor>", methods=["POST"])
def InserirValidador(chave_seletor):
    if request.method == "POST" and chave_seletor != "":
        validador = Validador(
            chave_seletor=chave_seletor,
            ultima_transacao=datetime.now(),
            contador_transacoes=0,
            saldo=100,
            flags=0,
        )
        db.session.add(validador)
        db.session.commit()
        objeto_dict = {
            "id": validador.id,
            "chave_seletor": validador.chave_seletor,
            "ultima_transacao": validador.ultima_transacao,
            "contador_transacoes": validador.contador_transacoes,
            "saldo": validador.saldo,
            "flags": validador.flags,
        }

        return jsonify(objeto_dict)
    else:
        return jsonify(["Method Not Allowed"])


@app.route("/validador/<int:id>", methods=["DELETE"])
def ApagarValidador(id):
    if request.method == "DELETE":
        objeto = Validador.query.get(id)
        db.session.delete(objeto)
        db.session.commit()

        data = {"message": "Validador Deletado com Sucesso"}

        return jsonify(data)
    else:
        return jsonify(["Method Not Allowed"])