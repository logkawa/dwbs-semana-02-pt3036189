# Aula 060. Bancos de dados

## Slide 21
- from hello import db
- db.create_all()

## Slide 22
- db.drop_all()
- db.create_all()

## Slide 23
- from hello import Role, User
- admin_role = Role(name='Admin')
- mod_role = Role(name='Moderator')
- user_role = Role(name='User')
- user_john = User(username='john', role=admin_role)
- user_susan = User(username='susan', role=user_role)
- user_david = User(username='david', role=user_role)

## Slide 24
- db.session.add_all([admin_role, mod_role, user_role, user_john, user_susan, user_david])

## Slide 25
- db.session.commit()

## Slide 26
- admin_role.name = 'Administrator'
- db.session.add(admin_role)
- db.session.commit()

## Slide 27
- db.session.delete(mod_role)
- db.session.commit()

## Slide 28
- Role.query.all()
- User.query.all()
- User.query.filter_by(role=user_role).all()

## Slide 30
- user_role = Role.query.filter_by(name='User').first()
