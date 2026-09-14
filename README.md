Aluno: Nathalia Ventura Kawakami
Prontuário: PT3036189

## 1.Criando e Configurando o Banco de Dados

```powershell
$env:FLASK_APP = "hello.py"
flask shell
```

```python
from hello import db, Role, User

db.create_all()

[setattr(u, 'role', Role.query.filter_by(name='User').first()) for u in User.query.filter_by(role_id=None).all()]; db.session.commit()

exit()
```

## 3. Iniciando
```powershell
flask --app hello run --debug
```
