from dataclasses import dataclass
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

class Validador:
    def __init__(self, chave_seletor):
        self.chave_seletor = chave_seletor
        self.ultima_transacao = None
        self.contador_transacoes = 0
    
    def validar_transacao(self, remetente_id, valor):
        remetente = Cliente.query.get(remetente_id)
        if remetente is None:
            return False

        if remetente.qtdMoeda < valor:
            return False

        horario_atual = datetime.now()
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

validator = Validador(1234)  # Substitua 'chave_seletor' pelo valor correto

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)



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
        produtos = Seletor.query.all()
        return jsonify(produtos)


@app.route("/seletor/<string:nome>/<string:ip>", methods=["POST"])
def InserirSeletor(nome, ip):
    if request.method == "POST" and nome != "" and ip != "":
        objeto = Seletor(nome=nome, ip=ip)
        db.session.add(objeto)
        db.session.commit()
        objeto_dict = {
            "nome": objeto.nome,
            "ip": objeto.ip
        }

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
        return jsonify(transacoes)


@app.route("/transacoes/<int:id>", methods=["GET"])
def UmaTransacao(id):
    if request.method == "GET":
        objeto = Transacao.query.get(id)
        return jsonify(objeto)
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

@app.route("/transacoes/<int:rem>/<int:reb>/<int:valor>", methods=["POST"])
def CriaTransacao(rem, reb, valor):
    if request.method == "POST":
        objeto = Transacao(
            remetente=rem, recebedor=reb, valor=valor, status=0, horario=datetime.now()
        )
        
        objeto = validator.concluir_transacao(objeto)
        
        db.session.add(objeto)
        db.session.commit()
        objeto_dict = {
            "rem": objeto.remetente,
            "reb": objeto.recebedor,
            "valor": objeto.valor
        }

        return jsonify(objeto_dict)
    else:
        return jsonify(["Method not allowed"])