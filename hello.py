from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap, url_for
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired



app = Flask(__name__)
app.config['SECRET_KEY'] = 'jssb0512nt1915'

# Iniciando extensões
bootstrap = Bootstrap(app)
moment = Moment(app)

class Form(FlaskForm):
  name = StringField('What is your name?', validators= [DataRequired()])
  lastname = StringField('What is your last name?', validators= [DataRequired()])
  institution = StringField('What is your institution?', validators= [DataRequired()])
  discipline = SelectField('What is your discipline?', choices=[('DSWA5', 'DSWA5'), ('DSBA4', 'DSBA4'), ('Gestão de projetos', 'Gestão de projetos')], validators= [DataRequired()])

  submit = SubmitField('Submit')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# RAÍZ
@app.route('/', methods=['GET', 'POST'])

def index():
  form = Form()
  if form.validate_on_submit():
    old_name = session.get('name')
    if old_name is not None and old_name != form.name.data:
      flash('Looks like you have changed your name!')
    session['name'] = form.name.data
    session['lastname'] = form.lastname.data
    session['institution'] = form.institution.data
    session['discipline'] = form.discipline.data
    return redirect(url_for('index'))
  return render_template(
      'index.html',
      form=form,
      name=session.get('name'),
      lastname=session.get('lastname'),
      institution=session.get('institution'),
      discipline=session.get('discipline'),
        ip=request.remote_addr,
        host=request.host,
      current_time=datetime.utcnow(),
  )



# # IDENTIFICAÇÃO   
# @app.route('/user/<name>')
# @app.route('/user/<name>/<prontuario>')
# @app.route('/user/<name>/<prontuario>/<instituicao>')
# def user(name, prontuario='PT3036413', instituicao='IFSP'):
#     return render_template('id.html', name=name, prontuario=prontuario, instituicao=instituicao)

# REQUISIÇÃO DE CONTEXTO
# @app.route('/contextorequisicao/<name>')
# def contextorequisicao(name):
#     navegador = request.headers.get('User-Agent')
#     ip_cliente = request.remote_addr
#     host_app = request.host
#     return render_template('contexto.html', name=name, navegador=navegador, ip_cliente=ip_cliente, host_app=host_app)