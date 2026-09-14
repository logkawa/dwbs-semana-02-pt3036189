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
from flask_migrate import Migrate

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
migrate = Migrate(app, db)

# endregion





# --- CLASSES WTFORMS ---
# region

class NameForm(FlaskForm):
    name = StringField('Qual o seu nome?', validators=[DataRequired()])
    role = SelectField('Qual a sua função?', coerce=int)
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
    
    # Preenche o dropdown com as roles no banco de dados
    form.role.choices = [(r.id, r.name) for r in Role.query.order_by(Role.name).all()]
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        
        if user is None:
            selected_role = Role.query.get(form.role.data)
            
            user = User(username=form.name.data, role=selected_role)
            db.session.add(user)
            db.session.commit()
            
            session['known'] = False
        else:
            session['known'] = True
            
        session['name'] = form.name.data
        return redirect(url_for('index'))
    
    todos_os_usuarios = User.query.all()
    todas_as_funcoes = Role.query.all()
    
    return render_template('index.html',
                           form=form,
                           nome_completo=session.get('name'),
                           known=session.get('known', False),
                           users=todos_os_usuarios,
                           roles=todas_as_funcoes)

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