from werkzeug.security import generate_password_hash, check_password_hash  # Añade esta línea
from app.models import User
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_user(username, password):
    user = User(
        usr_name=username,
        usr_password=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()
    return user