# --- IMPORTAÇÕES DO FLASK ---
# region

# --- Bibliotecas padrão Python ---
import os
from datetime import datetime

# --- Requisições HTTP ---
import requests

# --- Variáveis de ambiente ---
from dotenv import load_dotenv

# --- Núcleo Flask ---
from flask import Flask, render_template, session, redirect, url_for, flash

# --- Interface e utilidades ---
from flask_bootstrap import Bootstrap
from flask_moment import Moment

# --- Formulários e Validações ---
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired

# --- Banco de dados ---
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# endregion


# --- CONFIGURAÇÕES BÁSICAS ---
# region

# Carrega as variáveis do arquivo .env
basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)

# --- Variáveis de ambiente ---
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
app.config['FLASKY_APP'] = os.environ.get('FLASKY_APP')

app.config['API_URL'] = os.environ.get('API_URL')
app.config['API_KEY'] = os.environ.get('API_KEY')
app.config['API_FROM'] = os.environ.get('API_FROM')

# --- Chave secreta ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# --- Banco de dados ---
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# endregion


# --- INICIANDO EXTENSÕES ---
# region

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app, db)

# endregion


# --- CLASSE DO FORMULÁRIO ---
# region

class NameForm(FlaskForm):

    nome = StringField(
        'Qual o seu nome?',
        validators=[DataRequired()]
    )

    prontuario = StringField(
        'Qual o seu prontuário?',
        validators=[DataRequired()]
    )

    username = StringField(
        'Qual o seu usuário?',
        validators=[DataRequired()]
    )

    enviar_email = BooleanField(
        'Deseja enviar e-mail para flaskaulasweb@zohomail.com?'
    )

    submit = SubmitField('Enviar')


# endregion


# --- MODELO DO BANCO DE DADOS ---
# region

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(100),
        nullable=False
    )

    prontuario = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    username = db.Column(
        db.String(100),
        unique=True,
        index=True,
        nullable=False
    )

    def __repr__(self):
        return f'<User {self.username}>'


# endregion


# --- ENVIO DE E-MAIL ---
# region

def enviar_email_cadastro(user, enviar_para_outro_email=False):

    api_url = app.config['API_URL']
    api_key = app.config['API_KEY']
    email_from = app.config['API_FROM']
    email_admin = app.config['FLASKY_ADMIN']

    # O admin sempre recebe o e-mail
    destinatarios = [
        email_admin,
        'nathaliavkawakami@gmail.com'
    ]

    # O segundo e-mail só recebe se o checkbox estiver marcado
    if enviar_para_outro_email:
        destinatarios.append('flaskaulasweb@zohomail.com')

    dados = {
        'from': email_from,

        'to': destinatarios,

        'subject': 'Novo usuário cadastrado',

        'text': f"""
Novo usuário cadastrado.

Prontuário: {user.prontuario}
Nome do aluno: {user.nome}
Usuário: {user.username}
"""
    }

    resposta = requests.post(
        api_url,
        auth=('api', api_key),
        data=dados
    )

    if resposta.status_code == 200:
        return True

    print('Erro ao enviar e-mail:')
    print('STATUS:', resposta.status_code)
    print('RESPOSTA:', resposta.text)

    return False


# endregion


# --- CONTEXTOS GLOBAIS ---
# region

@app.context_processor
def inject_time():

    return dict(
        current_time=datetime.utcnow()
    )


# endregion


# --- ROTAS ---
# region

@app.route('/', methods=['GET', 'POST'])
def index():

    form = NameForm()

    if form.validate_on_submit():

        # Verifica se o usuário já existe
        user = User.query.filter_by(
            username=form.username.data
        ).first()

        if user is None:

            user = User(
                nome=form.nome.data,
                prontuario=form.prontuario.data,
                username=form.username.data
            )

            db.session.add(user)
            db.session.commit()

            # Só envia e-mail se o checkbox estiver marcado
            email_enviado = enviar_email_cadastro(
                user,
                form.enviar_email.data
            )

            if email_enviado:

                if form.enviar_email.data:
                    flash(
                        'Usuário cadastrado e e-mails enviados com sucesso!',
                        'success'
                    )
                else:
                    flash(
                        'Usuário cadastrado e e-mail enviado para o administrador!',
                        'success'
                    )

            else:

                flash(
                    'Usuário cadastrado, mas ocorreu um erro ao enviar o e-mail.',
                    'warning'
                )

            session['name'] = user.nome
            session['known'] = False

        else:

            session['name'] = user.nome
            session['known'] = True

            flash(
                'Este usuário já está cadastrado.',
                'warning'
            )

        return redirect(url_for('index'))

    # Busca todos os usuários cadastrados
    todos_os_usuarios = User.query.order_by(
        User.id
    ).all()

    return render_template(
        'index.html',
        form=form,
        nome_completo=session.get('name'),
        known=session.get('known', False),
        users=todos_os_usuarios
    )


# endregion


# --- ERROR HANDLING ---
# region

@app.errorhandler(404)
def page_not_found(e):

    return render_template(
        '404.html'
    ), 404


@app.errorhandler(500)
def internal_server_error(e):

    return render_template(
        '500.html'
    ), 500


# endregion


# --- SERVIDOR LOCAL ---
if __name__ == '__main__':

    app.run(debug=True)