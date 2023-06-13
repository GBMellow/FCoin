from dataclasses import dataclass
from datetime import datetime


from flask import Flask, jsonify, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import requests

from entities.eleicao.seletor import Seletor

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
base_url = f"http://192.168.15.17:5000"
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
            "valor": objeto.valor,
            "status": objeto.status,
            "horario": objeto.horario
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
            response = Seletor.eleger_validadores(objeto)
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


@app.route("/validador/<int:id>/<string:ultima_transacao>/<int:contador_transacoes>/<int:saldo>/<int:flags>", methods=["POST"])
def EditarValidador(id, ultima_transacao, contador_transacoes, saldo, flags):
    if request.method == "POST":
        validador = Validador.query.get(id)
        validador.ultima_transacao = ultima_transacao
        validador.contador_transacoes = contador_transacoes
        validador.saldo = saldo
        validador.flags = flags
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
        objeto.saldo = 0
        db.session.commit()
        db.session.delete(objeto)
        db.session.commit()

        data = {"message": "Validador Deletado com Sucesso"}

        return jsonify(data)
    else:
        return jsonify(["Method Not Allowed"])