# --- IMPORTAÇÕES DO FLASK ---
# region

# --- Bibliotecas padrão Python ---
import os
from datetime import datetime

# --- Núcleo Flask ---
from flask import Flask, render_template, request, session, redirect, url_for, flash

# --- Interface e utilidades ---
from flask_bootstrap import Bootstrap
from flask_moment import Moment

# --- Formulários e Validações ---
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired

# --- Banco de dados ---
from flask_sqlalchemy import SQLAlchemy

# endregion





# --- CONFIGURAÇÕES BÁSICAS ---
# region

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'chaveultrasecreta' # Segurança contra CSRF
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# endregion





# --- INICIANDO EXTENSÕES ---
# region

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

# endregion





# --- CLASSES WTFORMS ---
# region

class NameForm(FlaskForm):
    name = StringField('Qual é o seu nome?', validators=[DataRequired()])
    submit = SubmitField('Enviar')

#endregion





# --- MODELOS DB SQLALCHEMY ---
# region

# --- Cargos ---
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic') # Uma Role pode estar ligada a vários Users

    def __repr__(self):
        return f'<Role {self.name}>'

# --- Usuários ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id')) # FK apontando para o id da tabela roles

    def __repr__(self):
        return f'<User {self.username}>'
    
# endregion





# --- CONTEXTOS GLOBAIS ---
# region

# --- Relógio global ---
@app.context_processor
def inject_time():
    return dict(current_time=datetime.utcnow())

#endregion





# --- ROTAS ---
# region

# --- Rota Raíz --- 
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            # Busca a role padrão 'User' no banco de dados
            user_role = Role.query.filter_by(name='User').first()
            
            # Cria o novo usuário vinculando-o à role padrão
            user = User(username=form.name.data, role=user_role)
            db.session.add(user)
            db.session.commit()
            
            session['known'] = False
        else:
            session['known'] = True
            
        session['name'] = form.name.data
        return redirect(url_for('index'))
    
    # Consulta todos os usuários para preencher a tabela HTML
    todos_os_usuarios = User.query.all()
    
    return render_template('index.html',
                           form=form,
                           nome_completo=session.get('name'),
                           known=session.get('known', False),
                           users=todos_os_usuarios)

# endregion





# --- ERROR HANDLING ---
# region

# --- ERRO 404 ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# --- ERRO 500 - SERVIDOR ---
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# endregion

# --- SERVIDOR LOCAL ---
if __name__ == '__main__':
    app.run(debug=True)