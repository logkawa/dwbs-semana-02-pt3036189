from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime

app = Flask(__name__)

# Iniciando extensões
bootstrap = Bootstrap(app)
moment = Moment(app)

# RAÍZ
@app.route('/')
def index():
    return render_template('index.html', current_time = datetime.utcnow())

# IDENTIFICAÇÃO
@app.route('/user/<name>')
@app.route('/user/<name>/<prontuario>')
@app.route('/user/<name>/<prontuario>/<instituicao>')
def user(name, prontuario='PT3036413', instituicao='IFSP'):
    return render_template('id.html', name=name, prontuario=prontuario, instituicao=instituicao)

# REQUISIÇÃO DE CONTEXTO
@app.route('/contextorequisicao/<name>')
def contextorequisicao(name):
    navegador = request.headers.get('User-Agent')
    ip_cliente = request.remote_addr
    host_app = request.host
    return render_template('contexto.html', name=name, navegador=navegador, ip_cliente=ip_cliente, host_app=host_app)