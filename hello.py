# --- IMPORTAÇÕES ---
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# --- CONFIGURAÇÕES ---
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)

app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
app.config['API_URL'] = os.environ.get('API_URL')
app.config['API_KEY'] = os.environ.get('API_KEY')
app.config['API_FROM'] = os.environ.get('API_FROM')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# --- EXTENSÕES ---
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app, db)


# --- FORMULÁRIO ---
class NameForm(FlaskForm):
    name = StringField(
        'Qual é o seu nome?',
        validators=[DataRequired()]
    )

    enviar_email = BooleanField(
        'Deseja enviar e-mail para flaskaulasweb@zohomail.com?'
    )

    submit = SubmitField('Submit')


# --- MODELOS DO BANCO ---
class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    users = db.relationship('User', backref='role')


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True, nullable=False)

    role_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id'),
        nullable=False
    )

class EmailLog(db.Model):
    __tablename__ = 'email_logs'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=True
    )

    destinatarios = db.Column(
        db.Text,
        nullable=False
    )

    assunto = db.Column(
        db.String(200),
        nullable=False
    )

    corpo = db.Column(
        db.Text,
        nullable=False
    )

    data_envio = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False
    )

    codigo_resposta = db.Column(
        db.Integer,
        nullable=True
    )

    usuario = db.relationship('User', backref='emails')


# --- ENVIO DE E-MAIL ---

def enviar_email_cadastro(user, enviar_para_zoho=False):
    api_url = app.config['API_URL']
    api_key = app.config['API_KEY']
    email_from = app.config['API_FROM']
    email_admin = app.config['FLASKY_ADMIN']

    # Destinatários fixos
    destinatarios = [
        email_admin,
        'nathaliavkawakami@gmail.com'
    ]

    # O Zoho só recebe se o checkbox estiver marcado
    if enviar_para_zoho:
        destinatarios.append('flaskaulasweb@zohomail.com')

    # Remove valores vazios e destinatários duplicados
    destinatarios = list(dict.fromkeys(
        email.strip()
        for email in destinatarios
        if email and email.strip()
    ))

    assunto = 'Novo usuário cadastrado'

    corpo = f"""
Novo usuário cadastrado.

Prontuário: PT3036189
Nome do aluno: Nathalia Kawakami
Usuário cadastrado: {user.name}
"""

    status = 'Falha'
    codigo_resposta = None

    try:
        if not all([api_url, api_key, email_from]):
            raise ValueError(
                'API_URL, API_KEY ou API_FROM não configurados no .env.'
            )

        if not email_admin:
            raise ValueError(
                'FLASKY_ADMIN não está configurado no .env.'
            )

        resposta = requests.post(
            api_url,
            auth=('api', api_key),
            data={
                'from': email_from,
                'to': destinatarios,
                'subject': assunto,
                'text': corpo
            },
            timeout=15
        )

        codigo_resposta = resposta.status_code

        if resposta.status_code == 200:
            status = 'Enviado'
        else:
            print('Erro ao enviar e-mail:')
            print('Status:', resposta.status_code)
            print('Resposta:', resposta.text)

    except (requests.RequestException, ValueError) as erro:
        print('Falha no envio de e-mail:', erro)

    finally:
        # Registra a tentativa no histórico
        registro = EmailLog(
            user_id=user.id,
            destinatarios=', '.join(destinatarios),
            assunto=assunto,
            corpo=corpo,
            status=status,
            codigo_resposta=codigo_resposta
        )

        db.session.add(registro)
        db.session.commit()

    return status == 'Enviado'


# --- CONTEXTO GLOBAL ---
@app.context_processor
def inject_time():
    return {'current_time': datetime.utcnow()}


# --- ROTA PRINCIPAL ---

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()

    if form.validate_on_submit():
        nome = form.name.data.strip()

        # Verifica se o usuário já está cadastrado
        user = User.query.filter_by(name=nome).first()

        if user is not None:
            session['name'] = user.name
            session['known'] = True

            flash('Este usuário já está cadastrado.', 'warning')
            return redirect(url_for('index'))

        # Busca a função padrão para o novo usuário
        role_user = Role.query.filter_by(name='User').first()

        if role_user is None:
            flash(
                'A função User não existe no banco de dados. '
                'Verifique a inicialização das funções.',
                'danger'
            )
            return redirect(url_for('index'))

        # Cria e salva o usuário
        user = User(
            name=nome,
            role=role_user
        )

        db.session.add(user)
        db.session.commit()

        # Envia o e-mail e registra o resultado no histórico
        email_enviado = enviar_email_cadastro(
            user,
            form.enviar_email.data
        )

        # Guarda informações da sessão
        session['name'] = user.name
        session['known'] = False

        if email_enviado:
            flash(
                'Usuário cadastrado e e-mail aceito pelo Mailgun.',
                'success'
            )
        else:
            flash(
                'Usuário cadastrado, mas houve uma falha no envio. '
                'Consulte o histórico de e-mails.',
                'warning'
            )

        return redirect(url_for('index'))

    # Lista todos os usuários cadastrados
    usuarios = User.query.order_by(User.id).all()

    # Lista o histórico de e-mails, do mais recente ao mais antigo
    historico_emails = EmailLog.query.order_by(
        EmailLog.data_envio.desc()
    ).all()

    return render_template(
        'index.html',
        form=form,
        nome_completo=session.get('name'),
        known=session.get('known', False),
        users=usuarios,
        emails=historico_emails
    )


@app.route('/emails')
def emails_enviados():
    historico_emails = EmailLog.query.order_by(
        EmailLog.data_envio.desc()
    ).all()

    return render_template(
        'emails.html',
        emails=historico_emails
    )

# --- TRATAMENTO DE ERROS ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# --- EXECUÇÃO LOCAL ---
if __name__ == '__main__':
    app.run(debug=True)
