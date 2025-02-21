from sqlalchemy.orm import Session
from sqlalchemy import func, desc  
from src.Conexion.Tablas import User  


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def generar_id_usuario(self):
        ultimo_usuario = self.session.query(User.id).order_by(desc(User.id)).first()

        if ultimo_usuario and ultimo_usuario[0].startswith('USR-'):
            ultimo_numero = int(ultimo_usuario[0].split('-')[1])
            nuevo_id = f'USR-{ultimo_numero + 1:03d}'
        else:
            nuevo_id = 'USR-001'

        return nuevo_id

    def crear_usuario(self, name, email, password_hash):
        nuevo_id = self.generar_id_usuario()
        usuario = User(id=nuevo_id, name=name, email=email, password_hash=password_hash)

        self.session.add(usuario)
        self.session.commit()
        return usuario  

    def obtener_usuario_por_email(self, email):
        """Obtiene un usuario por su email."""
        return self.session.query(User).filter_by(email=email).first()

    def validar_usuario(self, email, password_hash):
        print(f"Validando usuario con email: {email}, hash: {password_hash}")
        email = email.strip()
        usuario = self.session.query(User).filter_by(email=email, password_hash=password_hash).first()
        print(f"Usuario encontrado: {usuario}")

        if usuario:
            return usuario.id  
        else:
            return None  

    def obtener_todos_los_usuarios(self):
        """Obtiene todos los usuarios."""
        return self.session.query(User).all()

    def eliminar_usuario(self, user_id):
        """Elimina un usuario por su ID"""
        usuario = self.session.query(User).filter_by(id=user_id).first()
        if usuario:
            self.session.delete(usuario)
            self.session.commit()
            return True  
        return False  

    def actualizar_usuario(self, user_id, name=None, email=None, password_hash=None):
        """Actualiza la información de un usuario"""
        usuario = self.session.query(User).get(user_id)
        if not usuario:
            return False  

        if name:
            usuario.name = name
        if email:
            usuario.email = email
        if password_hash:
            usuario.password_hash = password_hash

        self.session.commit()
        return True

    def obtener_usuario_por_id(self, user_id):
        """Obtiene un usuario por su ID."""
        return self.session.query(User).filter_by(id=user_id).first()
