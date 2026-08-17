
# A very simple Flask Hello World app for you to get started with...

from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jssb0512nt1915'


@app.route('/')
def hello_world():
    return 'Hello from Flask! Bem vindos alunos do IFSP'

